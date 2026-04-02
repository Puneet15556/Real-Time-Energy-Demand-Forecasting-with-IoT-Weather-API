from pymongo import MongoClient
import pandas as pd

df = pd.read_csv("PJME_hourly.csv")  

last_50 = df.tail(200)

data = last_50.to_dict(orient="records")

client = MongoClient("mongodb://localhost:27017/")

db = client["Timeseries_db"]        
collection = db["Data"]    

collection.insert_many(data)

print("✅ Last 200 rows inserted successfully!")    
print(client.list_database_names())
print(db.list_collection_names())

print(collection.count_documents({}))