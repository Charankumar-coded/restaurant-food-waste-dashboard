import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Restaurant Food Waste Dashboard", page_icon="🍽️", layout="wide")

st.title("🍽️ Restaurant Food Waste Prediction & Analytics")
st.caption("Explore meal demand, food waste, and estimated waste costs to support smarter food preparation.")

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_csv("restaurant_food_waste_dataset.csv")
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    return data

uploaded = st.sidebar.file_uploader("Upload a dataset CSV (optional)", type=["csv"])
try:
    df = load_data(uploaded)
except FileNotFoundError:
    st.error("Dataset not found. Keep restaurant_food_waste_dataset.csv in the same folder as app.py, or upload it in the sidebar.")
    st.stop()

st.sidebar.header("Dashboard filters")
meal_options = sorted(df["meal_type"].dropna().unique())
selected_meals = st.sidebar.multiselect("Meal type", meal_options, default=meal_options)
event_options = sorted(df["special_event"].dropna().unique())
selected_events = st.sidebar.multiselect("Special event", event_options, default=event_options)
restaurant_options = sorted(df["restaurant_type"].dropna().unique())
selected_restaurants = st.sidebar.multiselect("Restaurant type", restaurant_options, default=restaurant_options)

filtered = df[
    df["meal_type"].isin(selected_meals)
    & df["special_event"].isin(selected_events)
    & df["restaurant_type"].isin(selected_restaurants)
].copy()

if filtered.empty:
    st.warning("No rows match these filters. Select at least one option in each filter.")
    st.stop()

total_prepared = int(filtered["meals_prepared"].sum())
total_sold = int(filtered["meals_sold"].sum())
total_waste = int(filtered["food_waste_meals"].sum())
waste_rate = (total_waste / total_prepared * 100) if total_prepared else 0
waste_cost = float(filtered["estimated_waste_cost_inr"].sum())
avg_demand = float(filtered["meals_sold"].mean())

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Meals prepared", f"{total_prepared:,}")
c2.metric("Meals sold", f"{total_sold:,}")
c3.metric("Meals wasted", f"{total_waste:,}")
c4.metric("Waste rate", f"{waste_rate:.1f}%")
c5.metric("Estimated waste cost", f"₹{waste_cost:,.0f}")

st.info("Dataset note: this is a synthetic educational dataset created for a college project. Costs and patterns are simulated, not real restaurant records.")

tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Demand patterns", "Waste & cost", "Prediction demo"])

with tab1:
    left, right = st.columns(2)
    daily = filtered.groupby("date", as_index=False).agg(
        meals_sold=("meals_sold", "sum"),
        meals_prepared=("meals_prepared", "sum"),
        food_waste_meals=("food_waste_meals", "sum")
    ).sort_values("date")
    with left:
        fig = px.line(daily, x="date", y=["meals_sold", "meals_prepared"], markers=True,
                      title="Meals prepared vs meals sold", labels={"value": "Meals", "date": "Date", "variable": "Measure"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        by_meal = filtered.groupby("meal_type", as_index=False).agg(
            meals_sold=("meals_sold", "sum"), food_waste_meals=("food_waste_meals", "sum")
        )
        fig = px.bar(by_meal, x="meal_type", y=["meals_sold", "food_waste_meals"], barmode="group",
                     title="Sales and waste by meal", labels={"value": "Meals", "meal_type": "Meal", "variable": "Measure"})
        st.plotly_chart(fig, use_container_width=True)
    st.subheader("Filtered data preview")
    st.dataframe(filtered.head(100), use_container_width=True)
    st.download_button("Download filtered data as CSV", filtered.to_csv(index=False).encode("utf-8"),
                       file_name="filtered_restaurant_food_waste.csv", mime="text/csv")

with tab2:
    left, right = st.columns(2)
    with left:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday = filtered.groupby("day_of_week", as_index=False).agg(avg_meals_sold=("meals_sold", "mean"))
        weekday["day_of_week"] = pd.Categorical(weekday["day_of_week"], categories=weekday_order, ordered=True)
        weekday = weekday.sort_values("day_of_week")
        fig = px.bar(weekday, x="day_of_week", y="avg_meals_sold", title="Average meal demand by day of week",
                     labels={"day_of_week": "Day", "avg_meals_sold": "Average meals sold"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        fig = px.box(filtered, x="meal_type", y="meals_sold", color="meal_type",
                     title="Distribution of meals sold by meal type",
                     labels={"meal_type": "Meal type", "meals_sold": "Meals sold"})
        st.plotly_chart(fig, use_container_width=True)
    fig = px.scatter(filtered, x="weather_temperature_c", y="meals_sold", color="meal_type",
                     size="restaurant_capacity", hover_data=["date", "special_event"],
                     title="Temperature vs meals sold", labels={"weather_temperature_c": "Temperature (°C)", "meals_sold": "Meals sold"})
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    left, right = st.columns(2)
    with left:
        waste_by_category = filtered.groupby("menu_category", as_index=False).agg(
            food_waste_meals=("food_waste_meals", "sum")
        ).sort_values("food_waste_meals", ascending=False)
        fig = px.bar(waste_by_category, x="menu_category", y="food_waste_meals",
                     title="Food waste by menu category", labels={"menu_category": "Menu category", "food_waste_meals": "Meals wasted"})
        st.plotly_chart(fig, use_container_width=True)
    with right:
        waste_by_event = filtered.groupby("special_event", as_index=False).agg(
            waste_cost=("estimated_waste_cost_inr", "sum")
        ).sort_values("waste_cost", ascending=False)
        fig = px.pie(waste_by_event, names="special_event", values="waste_cost", hole=0.45,
                     title="Share of estimated waste cost by event")
        st.plotly_chart(fig, use_container_width=True)
    st.metric("Average ingredient waste per record", f"{filtered['ingredient_waste_kg'].mean():.2f} kg")
    st.metric("Average estimated waste cost per record", f"₹{filtered['estimated_waste_cost_inr'].mean():,.2f}")

with tab4:
    st.write("Use the controls below to estimate meal demand from similar historical records. This is a transparent baseline model using the nearest matching records, not a production-grade forecasting system.")
    p1, p2, p3 = st.columns(3)
    with p1:
        pred_meal = st.selectbox("Meal type", sorted(df["meal_type"].dropna().unique()), key="pred_meal")
        pred_day = st.selectbox("Day of week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="pred_day")
    with p2:
        pred_event = st.selectbox("Special event", sorted(df["special_event"].dropna().unique()), key="pred_event")
        pred_temp = st.slider("Temperature (°C)", 15, 43, 29)
    with p3:
        pred_restaurant = st.selectbox("Restaurant type", sorted(df["restaurant_type"].dropna().unique()), key="pred_restaurant")
        safety_buffer = st.slider("Preparation buffer (%)", 0, 25, 5)

    if st.button("Estimate demand", type="primary"):
        matches = df[
            (df["meal_type"] == pred_meal)
            & (df["day_of_week"] == pred_day)
            & (df["special_event"] == pred_event)
            & (df["restaurant_type"] == pred_restaurant)
        ]
        if len(matches) < 5:
            matches = df[(df["meal_type"] == pred_meal) & (df["restaurant_type"] == pred_restaurant)]
        if len(matches) == 0:
            matches = df[df["meal_type"] == pred_meal]
        estimated_demand = int(round(matches["meals_sold"].median()))
        recommended_prep = int(np.ceil(estimated_demand * (1 + safety_buffer / 100)))
        historical_waste_rate = (matches["food_waste_meals"].sum() / matches["meals_prepared"].sum() * 100) if matches["meals_prepared"].sum() else 0
        st.success(f"Estimated demand: **{estimated_demand} meals**")
        st.write(f"Suggested preparation quantity with buffer: **{recommended_prep} meals**")
        st.write(f"Historical waste rate in matched records: **{historical_waste_rate:.1f}%**")
        st.caption(f"Based on {len(matches)} similar historical records. Use as a classroom demonstration only; validate with real restaurant data before operational use.")

st.markdown("---")
st.caption("Built with Streamlit, Pandas, NumPy and Plotly | College Data Visualization Project")
