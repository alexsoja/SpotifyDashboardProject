# app.py
import streamlit as st
import pandas as pd
import os

# --- Setup ---
st.set_page_config(page_title="Spotify Dashboard", layout="wide")
st.title("Spotify Dashboard — MVP")

# Determine script directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Ensure data folder exists
if not os.path.exists(DATA_DIR):
    st.error(f"Data folder not found: {DATA_DIR}. Run spotify_fetch.py first.")
    st.stop()

# --- Sidebar ---
time_range = st.sidebar.selectbox("Select Time Range", ["short_term", "medium_term", "long_term"])
st.sidebar.write("Note: CSVs currently reflect one time range. Update spotify_fetch.py to fetch by time_range.")

# --- Load Data ---
def load_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        st.error(f"File not found: {path}. Run spotify_fetch.py first.")
        st.stop()
    return pd.read_csv(path)

artists = load_csv("top_artists.csv")
tracks = load_csv("top_tracks.csv")

# --- Top Artists ---
st.header("Top Artists")
st.dataframe(artists)

st.subheader("Top Artists Popularity")
st.bar_chart(artists.set_index("name")["popularity"])

# --- Genre Distribution ---
st.subheader("Genres Distribution")
all_genres = []
for g in artists.get("genres", []):
    if pd.notna(g):
        all_genres.extend(g.split(", "))
genre_counts = pd.Series(all_genres).value_counts()
st.bar_chart(genre_counts)

# --- Genre Popularity ---
st.subheader("Average Popularity by Genre")

genre_popularity = {}

for _, row in artists.iterrows():
    if pd.notna(row.get("genres")):
        for g in row["genres"].split(", "):
            if g not in genre_popularity:
                genre_popularity[g] = []
            genre_popularity[g].append(row["popularity"])

# Calculate average popularity per genre
avg_genre_popularity = {g: sum(p)/len(p) for g, p in genre_popularity.items()}

# Convert to DataFrame for Streamlit
genre_pop_df = pd.DataFrame.from_dict(avg_genre_popularity, orient="index", columns=["avg_popularity"])
genre_pop_df = genre_pop_df.sort_values(by="avg_popularity", ascending=False)

st.bar_chart(genre_pop_df)

# --- Top Tracks ---
st.header("Top Tracks")
st.dataframe(tracks)

st.subheader("Top Tracks Popularity")
st.bar_chart(tracks.set_index("name")["popularity"])
