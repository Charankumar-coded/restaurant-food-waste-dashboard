# Restaurant Food Waste Prediction & Analytics

## Files
- `app.py` — Streamlit dashboard
- `restaurant_food_waste_dataset.csv` — synthetic educational dataset (1,200 records)
- `requirements.txt` — dependencies

## Run locally
1. Install Python 3.10 or newer.
2. Put all files in the same folder.
3. Open a terminal in that folder and run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

4. Streamlit will show a local URL, usually `http://localhost:8501`.

## Dashboard features
- Filters for meal type, special event, and restaurant type
- KPI cards for meals prepared/sold/wasted, waste rate, and estimated waste cost
- Interactive charts for demand, waste, weekdays, temperature, and events
- CSV preview and download
- A simple historical-median demand estimate with a preparation buffer

## Important
The dataset is synthetic and created for educational demonstration. It is not real restaurant data. The prediction screen is a simple baseline demonstration, not a trained machine-learning model. For a real deployment, use validated restaurant records and evaluate a proper forecasting model.
