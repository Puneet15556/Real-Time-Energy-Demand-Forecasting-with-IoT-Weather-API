# 🚀 Real-Time Energy Demand Forecasting (ML + IoT + MongoDB)

## 📌 Overview

This project implements a **real-time time-series forecasting pipeline** for energy demand prediction using **Machine Learning (XGBoost), MongoDB, and IoT integration (ESP32)**.

The system continuously generates predictions using historical data and stores them in a database, enabling a **recursive forecasting pipeline**.

---

## ⚙️ Key Features

### 🔁 Recursive Forecasting Pipeline

* Predicts **next timestamp energy demand**
* Uses **lag-based features (up to lag_168)**
* Each prediction is stored and reused for future predictions

---

### 🧠 Feature Engineering

* Time-based features:

  * `hour`, `day`, `month`, `day_of_week`, `is_weekend`
* Lag features:

  * `lag_1`, `lag_2`, ..., `lag_168`
* Rolling feature:

  * `rolling_mean_24`

---

### 🗄️ MongoDB Integration

* Stores:

  * historical data
  * predicted values
  * environmental data (temperature, humidity)

* Uses a **placeholder → update pipeline**:

  1. Insert future timestamp
  2. Generate features
  3. Predict value
  4. Update same document

---

### 🌦️ IoT + API Integration (Data Collection Only)

* Temperature & humidity are collected from:

  * **ESP32 (IoT device)** → primary source
  * **Weather API (OpenWeather)** → fallback

⚠️ **Important Note:**

* These values are **stored in MongoDB for future use**
* They are **NOT currently used as input features for the ML model**
* This design allows easy future extension of the model

---

### 📡 IoT Support (ESP32)

* Captures real-world environmental data
* Sends data to the system
* Improves system realism and extensibility

---

### 🔄 Fault-Tolerant Design

* Handles:

  * API failures
  * missing data
  * schema inconsistencies
* Ensures pipeline continues without crashing

---

### ⏱️ Execution Modes

* Local testing:

  * `Simple a RUN pipeline`
* Production-ready:

  * Cron jobs / Task Scheduler / Airflow

---

## 🧠 Machine Learning Model

* Model: **XGBoost Regressor**
* Learns patterns from:

  * time features
  * lagged historical values
* Designed for **short-term energy demand forecasting**

---

## 🔄 System Workflow

```
1. Fetch latest data from MongoDB
2. Insert next timestamp (placeholder)
3. Generate features (lags + time features)
4. Fetch temperature/humidity (ESP32 → API fallback)
5. Predict next energy demand
6. Update MongoDB with prediction + weather data
7. Repeat (recursive forecasting)
```

---

## 🧪 Example Output

```
2018-01-10 07:00 → 60367 MW
2018-01-10 08:00 → 59915 MW
2018-01-10 09:00 → 59438 MW
```

---

## 🛠️ Tech Stack

* Python
* Pandas / NumPy
* XGBoost
* MongoDB
* ESP32 (IoT)
* OpenWeather API

---

## 📁 Project Structure

```        
├── energy_model.pkl
├── model.ipynb      
├── mongoDB_insertion.py             
├── pipeline_with_IoT.py
├── pipeline.py
├── PJME_hourly.csv
```

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run pipeline
python pipeline_with_IoT.py
```

---

## 🔐 API Setup

1. Get API key from:
   https://openweathermap.org/api

2. Add in code:

```python
API_KEY = "your_api_key_here"
```

---

## 🎯 Key Learnings

* End-to-end ML pipeline design
* Real-time data handling
* Recursive forecasting
* Feature consistency between training & inference
* Integration of IoT + external APIs

---

## 🚀 Future Improvements

* Use **weather forecast API (future weather)**
* Include weather data as model features
* Deploy using **FastAPI + Docker**
* Add visualization dashboard (Streamlit)
* Automate retraining pipeline

---

## 🧠 Interview Pitch

> Built a real-time energy demand forecasting system using XGBoost with lag-based features, integrated IoT (ESP32) and weather APIs for data collection, and implemented a recursive prediction pipeline with MongoDB for continuous forecasting.

---

## ⭐ Notes

* Designed with **scalability and extensibility** in mind
* Weather and IoT data currently serve as **stored signals for future model enhancement**
* Pipeline mimics real-world energy forecasting systems

---
