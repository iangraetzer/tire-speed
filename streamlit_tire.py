import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page title
st.title("F1 Lap Time Analysis")

# Load data
@st.cache_data
def load_data(file_path="/Users/iangraetzer/Documents/GitHub/tire-speed/lap_tire_df_no_outliers.csv"):
    df = pd.read_csv(file_path)
    
    if df["Lap Time"].dtype == object:
        def convert_lap_time(time_str):
            if pd.isna(time_str):
                return np.nan
            
            try:
                if ':' in str(time_str):
                    parts = str(time_str).split(':')
                    minutes = float(parts[0])
                    seconds = float(parts[1])
                    return minutes * 60 + seconds
                else:
                    return float(time_str)
            except (ValueError, TypeError):
                return np.nan
        
        df["Lap Time"] = df["Lap Time"].apply(convert_lap_time)
    
    if df["Lap Number"].dtype == object:
        df["Lap Number"] = pd.to_numeric(df["Lap Number"], errors="coerce")
    

    if "meeting_key" in df.columns and "meeting_name" not in df.columns:
        # Method 1: Direct copy (simplest approach)
        df["meeting_name"] = df["meeting_key"]

    
    return df

# Load the data
df = load_data()

st.sidebar.header("Filters")

meeting_names = sorted(df["meeting_name"].unique())
selected_meeting = st.sidebar.selectbox("Select Race", meeting_names)

filtered_drivers_df = df[df["meeting_name"] == selected_meeting]
driver_options = filtered_drivers_df[["driver_number", "driver_name"]].drop_duplicates()
driver_display_list = [f"{row['driver_number']} - {row['driver_name']}" for _, row in driver_options.iterrows()]
driver_display_list = sorted(driver_display_list)

selected_driver_display = st.sidebar.selectbox("Select Driver", driver_display_list)
selected_driver_number = selected_driver_display.split(" - ")[0]

# Filter data based on selections
filtered_data = df[(df["meeting_name"] == selected_meeting) & 
                  (df["driver_number"].astype(str) == selected_driver_number)]

# Display driver info
driver_name = filtered_data["driver_name"].iloc[0]
st.write(f"Showing lap times for Driver #{selected_driver_number} ({driver_name}) at Meeting {selected_meeting}")

# Create scatter plot
fig = px.scatter(
    filtered_data, 
    x="Lap Number", 
    y="Lap Time",
    color="compound",
    title=f"Lap Times for {driver_name} at {selected_meeting}",
    labels={"Lap Time": "Lap Time (seconds)", "Lap Number": "Lap Number"},
    hover_data=["session_key", "compound"]
)

# Improve layout
fig.update_layout(
    xaxis=dict(
        tickmode='linear',
        tick0=0,
        dtick=10
    ),
    legend_title="Tire Compound"
)

st.plotly_chart(fig, use_container_width=True)

# Add a data summary
st.subheader("Lap Time Summary by Compound")
summary = filtered_data.groupby("compound")["Lap Time"].agg(["count", "min", "mean", "max"]).reset_index()
summary = summary.rename(columns={"count": "Laps", "min": "Best Lap", "mean": "Average", "max": "Worst Lap"})

# Format time values
for col in ["Best Lap", "Average", "Worst Lap"]:
    summary[col] = summary[col].round(3)

st.dataframe(summary)

# Display the raw data
if st.checkbox("Show raw data"):
    st.dataframe(filtered_data)