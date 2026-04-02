from pymongo import MongoClient
import pandas as pd
from datetime import timedelta
import joblib
import requests
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
        "humidity": data['main']['humidity']
    }

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
    last_time = df['Datetime'].max()
    next_time = last_time + timedelta(hours=1)
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

    weather = get_weather()

    collection.update_one(
        {"Datetime": next_time_str},
        {
            "$set": {
                "PJME_MW": float(pred),
                "temp": weather["temp"],
                "humidity": weather["humidity"]
            }
        }
    )

    print(f"✅ Updated {next_time} → {pred}")


def run_pipeline(steps=10):
    for _ in range(steps):
        predict_next()

# -----------------------------
# RUN
# -----------------------------
run_pipeline(10)