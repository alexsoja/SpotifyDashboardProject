import pandas as pd
import streamlit as st
import altair as alt

# Load data
tracks = pd.read_csv("data/top_tracks_all.csv")
artists = pd.read_csv("data/top_artists_all.csv")

st.title("🎵 Spotify Dashboard - Top 10 (Medium Term)")

# Filter medium term
tracks = tracks[tracks['time_range'] == 'medium_term']
artists = artists[artists['time_range'] == 'medium_term']

# Select category
category = st.selectbox("Choose category:", ["Tracks", "Artists"])

if category == "Tracks":
    df = tracks.copy()
    label_col = "name"
elif category == "Artists":
    df = artists.copy()
    label_col = "name"

# Take top 10 by user listens
df = df.sort_values("user_listens", ascending=False).head(10)

# Calculate percentages
df['percent_of_total'] = df['user_listens'] / df['user_listens'].sum() * 100

st.subheader(f"Top 10 {category} - Medium Term")

# Pie chart using Altair
pie = alt.Chart(df).mark_arc().encode(
    theta=alt.Theta(field="percent_of_total", type="quantitative"),
    color=alt.Color(field=label_col, type="nominal"),
    tooltip=[label_col, alt.Tooltip("user_listens", title="Plays"),
             alt.Tooltip("percent_of_total", title="% of Total", format=".2f")]
)

st.altair_chart(pie, use_container_width=True)
