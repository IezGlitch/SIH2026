# Aditya — Vegetation Indices, Frontend & Integration

## Role

**Aditya — Vegetation Indices (30%) + Frontend / Integration**

My role in the SIH project is divided into two major areas:

1. **Remote-sensing / crop-stress processing** — calculating vegetation indices from Sentinel-2 data.
2. **Frontend & integration** — building the dashboard, connecting it to the backend API, displaying map layers, and presenting alerts to users.

---

## 1. Vegetation Index & Crop-Stress Work

I am responsible for calculating vegetation indices that help identify crop health and stress.

### Main indices

| Index | Purpose |
|---|---|
| **NDVI** | Measures vegetation greenness and overall plant health |
| **NDRE** | Helps detect early vegetation/chlorophyll stress |
| **NDWI / NDMI** | Helps estimate vegetation/canopy moisture and water stress |

### NDVI

The standard NDVI formula is:

`NDVI = (NIR - Red) / (NIR + Red)`

For Sentinel-2, this commonly uses:

- **B8 — NIR**
- **B4 — Red**

### NDRE

NDRE uses a near-infrared band and a red-edge band to provide sensitivity to chlorophyll and early crop stress.

### NDWI / NDMI

These indices use NIR/SWIR information to estimate vegetation moisture and identify water-related stress.

---

## 2. Crop-Stress Raster Outputs

The calculated indices need to be converted into usable raster/map layers.

My responsibilities include:

- Processing Sentinel-2 vegetation-index data.
- Generating NDVI, NDRE and NDWI/NDMI raster outputs.
- Checking the generated values and detecting obvious processing errors.
- Keeping the raster outputs in a consistent format.
- Providing the crop-stress layers to the model/backend pipeline.
- Working with **Supriya** and **Ayush** so that the outputs match their expected format.

---

## 3. Frontend Dashboard

I am responsible for building the part of the application that users actually interact with.

The dashboard should allow users to:

- View the affected geographical area.
- View flood-risk information.
- View heat-risk information.
- View crop-stress information.
- Switch between different map layers.
- Understand the severity/risk level easily.
- View important alerts and warnings.
- Access relevant prediction information from the backend.

---

## 4. Backend API Integration

**Pratik** develops the backend and exposes the processed model results through APIs.

My responsibility is to consume those APIs from the frontend.

The integration flow is:

```text
Ayush's ML Models
        ↓
Pratik's Backend / API
        ↓
Aditya's Frontend
        ↓
Dashboard + Maps + Alerts
```

I should design the frontend so that backend data can be plugged in without rebuilding the UI.

During development, I can use **mock JSON/sample API responses** until Pratik's actual API is ready.

---

## 5. Map Integration

The dashboard should display geographical information as map layers.

Potential layers include:

- Flood-risk layer
- Heat-risk layer
- Crop-stress layer
- NDVI layer
- NDRE layer
- NDWI/NDMI layer
- Model prediction/risk zones

The frontend should allow users to turn layers on/off and understand what each layer represents.

---

## 6. Alert System

The frontend should convert model/API results into understandable alerts.

Examples:

```text
⚠ High Crop Stress
Vegetation stress detected in the selected region.

⚠ Flood Risk
Standing-water/flood risk detected in the selected area.

⚠ Heat Stress
High land-surface-temperature conditions detected.
```

The exact alert should be generated from the backend/model output rather than being hard-coded.

---

## 7. Team Dependencies

### Supriya
Provides satellite-derived physical features such as:

- SAR flood features
- Thermal/LST features
- Processed satellite data

### Ayush
Builds the ML models for:

- Flood prediction
- Heat prediction
- Crop-stress prediction

He needs both satellite features and weather/ground data before final model training.

### Pratik
Builds the backend that:

- Receives model outputs
- Stores results
- Converts them into usable map/API data
- Serves the results to the frontend

### Aditya
Consumes Pratik's API and turns the data into:

**Maps + Dashboard + Alerts + User-facing information**

---

## 8. What I Do NOT Own

My primary responsibility is **not**:

- SAR backscatter processing
- Flood-water feature extraction
- Land Surface Temperature calculation
- Training the main ML models
- Building the backend/database/API infrastructure

Those tasks belong primarily to **Supriya, Ayush and Pratik** respectively.

I focus on **vegetation-index/crop-stress processing and the frontend/integration layer**.

---

## 9. Suggested Tech Stack

### Frontend

- HTML
- CSS
- JavaScript
- React *(if the team is using React)*

### Maps

- Leaflet.js
- OpenStreetMap
- GeoJSON / raster map layers

### API Integration

- REST API
- JSON
- JavaScript `fetch()`

### Remote Sensing

- Python
- NumPy
- Rasterio
- GDAL
- Sentinel-2 data

The exact tools can be adjusted according to the team's final architecture.

---

## 10. End-to-End Responsibility

```text
Sentinel-2 Data
      ↓
Vegetation Bands
      ↓
NDVI / NDRE / NDWI-NDMI
      ↓
Crop-Stress Raster Layers
      ↓
Ayush's Crop-Stress Model
      ↓
Pratik's Backend / API
      ↓
Aditya's Frontend
      ↓
Interactive Map
      ↓
Risk Visualization + Alerts
      ↓
End User
```

## Development Strategy

To avoid blocking the frontend on other team members:

1. Build the dashboard UI first.
2. Create sample/mock JSON responses.
3. Build the map and layer-switching system.
4. Build the alert components.
5. Connect the frontend to Pratik's API when available.
6. Replace mock data with real model outputs.
7. Test the complete pipeline with real geographical data.

---

## Final Deliverable

The final frontend should provide a clear interface where an authority/user can:

**Select an area → View map layers → Check flood/heat/crop stress → Understand risk → Receive actionable alerts.**

My role connects the **remote-sensing crop-health information** with the **user-facing application**.
