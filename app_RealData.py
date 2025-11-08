import pandas as pd
import streamlit as st
import altair as alt
import os
import json

# --- Page Configuration ---
st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎵",
    layout="wide",
)

# --- Load and Combine JSON Files ---
@st.cache_data
def load_spotify_history(folder_path="data"):
    all_data = []
    for file in os.listdir(folder_path):
        if file.startswith("StreamingHistory_music_") and file.endswith(".json"):
            file_path = os.path.join(folder_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                all_data.extend(data)
    if not all_data:
        st.error("No streaming history files found in the data folder.")
        return None

    df = pd.DataFrame(all_data)
    df["endTime"] = pd.to_datetime(df["endTime"], errors="coerce")
    # Clean missing or invalid rows
    df = df.dropna(subset=["artistName", "trackName"])
    df = df[~df["artistName"].str.contains("unknown", case=False, na=False)]
    df = df[~df["trackName"].str.contains("unknown", case=False, na=False)]
    df = df[df["msPlayed"] > 0]

    df["play_count"] = 1  # each row = one play instance
    return df

# Load combined history
history_df = load_spotify_history("data")

if history_df is None:
    st.stop()

# --- Main App ---
st.title("🎵 Spotify Listening History Dashboard")
st.markdown("An all-time analysis of your Spotify listening habits.")
st.caption("Data from your exported streaming history files.")

earliest = history_df["endTime"].min()
latest = history_df["endTime"].max()

st.write(f"📅 Data collection started on: {earliest}")
st.write(f"📅 Data collection ended on: {latest}")

# --- Sidebar ---
with st.sidebar:
    st.header("Filters")
    category = st.selectbox("Choose Category:", ["Tracks", "Artists"])
    top_n = st.slider("Select number of top items:", 5, 50, 15)

# --- Processing ---
if category == "Tracks":
    df = history_df.groupby(["trackName", "artistName"]).agg(
        play_count=("play_count", "sum"),
        total_ms=("msPlayed", "sum")
    ).reset_index()
    df["display_name"] = df["trackName"] + " - " + df["artistName"]
    label_col, display_col = "trackName", "display_name"
    title = f"Top {top_n} Tracks"
else:
    df = history_df.groupby("artistName").agg(
        play_count=("play_count", "sum"),
        total_ms=("msPlayed", "sum")
    ).reset_index()
    label_col, display_col = "artistName", "artistName"
    title = f"Top {top_n} Artists"

value_col = "play_count"
df_top_n = df.sort_values(value_col, ascending=False).head(top_n)
df_top_n["percent_of_total"] = (df_top_n[value_col] / df_top_n[value_col].sum() * 100).round(2)

# --- KPIs ---
st.subheader(title)

total_plays = int(history_df["play_count"].sum())
total_hours = round(history_df["msPlayed"].sum() / (1000 * 60 * 60), 1)
top_item = df_top_n.iloc[0][display_col]
top_item_plays = int(df_top_n.iloc[0][value_col])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Plays (All-Time)", f"{total_plays:,}")
with col2:
    st.metric("Total Hours Streamed", f"{total_hours:,} hrs")
with col3:
    st.metric(f"Top {category.rstrip('s')}", top_item)

st.markdown("---")

# --- Chart + Data Table ---
col_chart, col_data = st.columns([2, 1])

with col_chart:
    st.subheader("Distribution of Plays")
    bar_chart = (
        alt.Chart(df_top_n)
        .mark_bar()
        .encode(
            x=alt.X(f"{value_col}:Q", title="Total Plays"),
            y=alt.Y(f"{display_col}:N", sort="-x", title=category.rstrip('s')),
            color=alt.Color(f"{display_col}:N", legend=None),
            tooltip=[display_col, value_col, "percent_of_total"]
        )
        .properties(height=alt.Step(30))
    )
    st.altair_chart(bar_chart, use_container_width=True)

with col_data:
    st.subheader("Data View")
    display_cols = ["artistName", "trackName", "play_count", "percent_of_total"] if category == "Tracks" else ["artistName", "play_count", "percent_of_total"]
    st.dataframe(df_top_n[display_cols], hide_index=True, use_container_width=True)

