import pandas as pd
import streamlit as st
import altair as alt

# --- Page Configuration ---
st.set_page_config(
    page_title="Spotify Dashboard",
    page_icon="🎵",
    layout="wide",
)

# --- Data Loading ---
# This function now loads our single, processed history file
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {file_path}. Please create the example CSV or process your real data.")
        return None

# Use the example file for now
# WHEN YOUR REAL DATA IS READY, YOU WILL CHANGE THIS FILENAME
history_df = load_data("data/real_play_counts_EXAMPLE.csv")

if history_df is None:
    st.stop()

# --- Main Application ---
st.title("🎵 Spotify Listening History Dashboard EX")
st.markdown("An all-time analysis of your listening habits based on your extended streaming history.")
st.markdown("Please Note: This dashboard uses example practice data that I created.")

# --- Sidebar for Filters ---
with st.sidebar:
    st.header("Filters")
    # Time range is gone, as this is all-time data
    category = st.selectbox("Choose Category:", ["Tracks", "Artists"])
    top_n = st.slider("Select number of top items:", 5, 50, 15) # Increased max range

# --- Process Data based on Selection ---
if category == "Tracks":
    # For tracks, the data is already in the right format
    df = history_df.copy()
    label_col = "trackName"
    # For a cleaner display, we'll combine track and artist
    df['display_name'] = df['trackName'] + " - " + df['artistName']
    display_col = "display_name"
    title = f"Top {top_n} Tracks"
else: # category == "Artists"
    # For artists, we need to group by artist and sum the plays
    artist_plays = history_df.groupby('artistName')['play_count'].sum().reset_index()
    df = artist_plays.copy()
    label_col = "artistName"
    display_col = "artistName"
    title = f"Top {top_n} Artists"

value_col = "play_count"
df_top_n = df.sort_values(value_col, ascending=False).head(top_n)
df_top_n['percent_of_total'] = (df_top_n[value_col] / df_top_n[value_col].sum() * 100).round(2)

# --- Display KPIs ---
st.subheader(f"{title} (All-Time)")

total_plays = int(df_top_n[value_col].sum())
top_item_name = df_top_n.iloc[0][display_col]
top_item_plays = int(df_top_n.iloc[0][value_col])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=f"Total Plays for Top {top_n}", value=f"{total_plays:,}")
with col2:
    st.metric(label=f"Most Played {category.rstrip('s')}", value=top_item_name)
with col3:
    st.metric(label="Plays for Top Item", value=f"{top_item_plays:,}")

st.markdown("---")

# --- Visualizations and Data Table ---
col_chart, col_data = st.columns([2, 1])

with col_chart:
    st.subheader("Distribution of Plays")

    bar_chart = alt.Chart(df_top_n).mark_bar().encode(
        x=alt.X(f'{value_col}:Q', title='Total Plays'),
        y=alt.Y(f'{display_col}:N', sort='-x', title=category.rstrip('s')),
        color=alt.Color(f'{display_col}:N', legend=None),
        tooltip=[
            alt.Tooltip(display_col, title=category.rstrip('s')),
            alt.Tooltip(value_col, title="Plays"),
            alt.Tooltip('percent_of_total', title="% of Total", format=".2f")
        ]
    ).properties(height=alt.Step(30))
    
    # Using use_container_width for compatibility with your Streamlit version
    st.altair_chart(bar_chart, use_container_width=True)

with col_data:
    st.subheader("Data View")
    
    # Prepare dataframe for display (show relevant columns)
    display_df_cols = [display_col, value_col, 'percent_of_total']
    if category == "Tracks":
        display_df_cols = ['trackName', 'artistName', value_col, 'percent_of_total']

    st.dataframe(
        df_top_n[display_df_cols],
        column_config={
            label_col: category.rstrip('s'),
            value_col: "Plays",
            'percent_of_total': "% of Total"
        },
        hide_index=True,
        use_container_width=True
    )