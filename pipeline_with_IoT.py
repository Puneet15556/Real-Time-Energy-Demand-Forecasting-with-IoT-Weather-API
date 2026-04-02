import requests
from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import joblib
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")
# -----------------------------
# 1. MongoDB Connection
# -----------------------------
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Timeseries_db"]
collection = db["Data"]

# -----------------------------
# 2. Load Model
# -----------------------------
model = joblib.load("energy_model.pkl")


def get_arduino_data():
    try:
        #ESP32 local server
        res = requests.get("http://192.168.1.50/data", timeout=2)

        if res.status_code == 200:
            data = res.json()
            return {
                "temp": data["temp"],
                "humidity": data["humidity"],
                "datetime": datetime.now(),
                "source": "MICROCONTROLLER"
            }

    except Exception as e:
        print("Arduino not available:", e)

    return None

feature_cols = [
    'hour',
    'day_of_week',
    'is_weekend',
    'month',
    'day',
    'lag_1',
    'lag_2',
    'lag_3',
    'lag_6',
    'lag_12',
    'lag_24',
    'lag_48',
    'lag_168',
    'rolling_mean_24'
]
# -----------------------------
# 3. Weather API
# -----------------------------

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?q=Delhi&appid={API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    print(data)  

    return {
        "temp": data['main']['temp'],
        "humidity": data['main']['humidity'],
        "datetime": datetime.now(),
        "source": "api"
    }
    
def get_data_auto():
    data = get_arduino_data()

    if data is not None:
        return data
    
    print("Switching to API...")
    return get_weather()    
    

# -----------------------------
# 4. Fetch Data
# -----------------------------
def get_data(n=200):
    data = list(collection.find().sort("Datetime", -1).limit(n))
    df = pd.DataFrame(data)
    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    df = df.sort_values("Datetime")
  
    return df

# -----------------------------
# 5. Feature Engineering
# -----------------------------
def create_features(df):
    df = df.copy()

    # Time features
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['hour'] = df['Datetime'].dt.hour
    df['day'] = df['Datetime'].dt.day
    df['month'] = df['Datetime'].dt.month
    df['day_of_week'] = df['Datetime'].dt.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # Lags 
    lags = [1,2,3,6,12,24,48,168]
    for lag in lags:
        df[f'lag_{lag}'] = df['PJME_MW'].shift(lag)

    # Rolling mean
    df['rolling_mean_24'] = df['PJME_MW'].shift(1).rolling(24).mean()

    return df


def predict_next():

   
    df = get_data()


    now = datetime.now()

    next_time = now.replace(minute=0, second=0, microsecond=0)
    next_time_str = next_time.strftime("%Y-%m-%d %H:%M:%S")

    collection.insert_one({
        "Datetime": next_time_str,
        "PJME_MW": None
    })

    df = get_data()

    df_feat = create_features(df)

    row = df_feat.iloc[-1:]

    X = row.drop(columns=['PJME_MW', '_id' , 'Datetime'], errors='ignore')
    X = X.reindex(columns=feature_cols, fill_value=0)
    pred = model.predict(X)[0]

    data = get_data_auto()

    collection.update_one(
        {"Datetime": next_time_str},
        {
            "$set": {
                "temp": data["temp"],
                "humidity": data["humidity"],
                "weather_source": data["source"]
            }
        }
    )
    print(f"✅ Updated {next_time} → {pred}")


def run_pipeline(steps=1):
    for _ in range(steps):
        predict_next()

# -----------------------------
# RUN
# -----------------------------
run_pipeline(1)