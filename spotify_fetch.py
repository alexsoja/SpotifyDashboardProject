import os
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope="user-top-read"
))

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

time_ranges = ["short_term", "medium_term", "long_term"]

# Fetch top artists
artist_frames = []
for t in time_ranges:
    top_artists = sp.current_user_top_artists(limit=50, time_range=t)
    data = []
    for idx, artist in enumerate(top_artists['items']):
        data.append({
            "name": artist['name'],
            "user_listens": 50 - idx,   # proxy for relative listens (top artist = more)
            "time_range": t
        })
    artist_frames.append(pd.DataFrame(data))

artists_df = pd.concat(artist_frames)
artists_df.to_csv("data/top_artists_all.csv", index=False)
print("✅ Top artists saved to data/top_artists_all.csv")


# Fetch top tracks
track_frames = []
for t in time_ranges:
    top_tracks = sp.current_user_top_tracks(limit=50, time_range=t)
    data = []
    for idx, track in enumerate(top_tracks['items']):
        data.append({
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "user_listens": 50 - idx,  # proxy for relative plays
            "time_range": t
        })
    track_frames.append(pd.DataFrame(data))

tracks_df = pd.concat(track_frames)
tracks_df.to_csv("data/top_tracks_all.csv", index=False)
print("✅ Top tracks saved to data/top_tracks_all.csv")
