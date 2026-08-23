# SIH2026 – Weather & Flood Risk Dashboard

## Overview

A weather and flood risk monitoring dashboard developed for SIH2026.

The system combines real weather data, flood-related datasets, derived weather-risk features, and a machine learning model to provide district-wise flood risk information.

## Key Features

- District-wise weather information
- Latest weather data for each district
- Weather risk assessment
- Flood-related statistics
- Flooded area information
- Flood event information
- Population information
- Machine Learning-based flood prediction
- ML prediction probability
- Overall flood/weather risk level
- Interactive dashboard

## Machine Learning

The project uses a trained machine learning model to predict flood risk.

The model uses the following features:

- Temperature
- Humidity
- Rainfall
- 6-hour rainfall
- 24-hour rainfall
- 6-hour average temperature
- 6-hour average humidity
- Heat risk
- Rainfall risk
- Rainfall intensity
- Humidity-rain index
- Flood pressure index
- Hour
- Day
- Month

The model returns:

- Flood prediction
- Prediction probability
- Risk level (HIGH / LOW)

## Backend

The backend is built using Flask.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard |
| `/health` | GET | Backend health check |
| `/districts` | GET | Returns available districts |
| `/weather` | GET | Returns latest weather data |
| `/weather?district=<name>` | GET | Returns latest data for a selected district |
| `/predict` | POST | Generates ML flood prediction |

## Data Processing Pipeline

The project contains scripts for:

- Weather data downloading
- Grid weather processing
- District-wise weather aggregation
- Flood data processing
- Weather and flood data merging
- ML dataset preparation
- ML model training

## Project Structure

```text
SIH2026/
│
├── backend/
│   └── app.py
│
├── data/
│   └── processed/
│       └── final_weather_flood_dataset.csv
│
├── models/
│   └── flood_risk_model.pkl
│
├── scripts/
│   ├── aggregate_weather_district.py
│   ├── build_final_weather_dataset.py
│   ├── create_weather_features.py
│   ├── create_weather_grid.py
│   ├── download_grid_weather.py
│   ├── download_weather.py
│   ├── merge_flood_data.py
│   ├── merge_flood_weather.py
│   ├── prepare_ml_dataset.py
│   ├── test_setup.py
│   └── train_model.py
│
├── index.html
├── requirements.txt
├── README.md
└── .gitignore