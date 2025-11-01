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
@st.cache_data
def load_data():
    try:
        tracks = pd.read_csv("data/top_tracks_all.csv")
        artists = pd.read_csv("data/top_artists_all.csv")
        return tracks, artists
    except FileNotFoundError:
        st.error("Data files not found. Make sure 'top_tracks_all.csv' and 'top_artists_all.csv' are in the 'data' directory.")
        return None, None

tracks, artists = load_data()

if tracks is None or artists is None:
    st.stop()

# --- Main Application ---
st.title("🎵 Spotify Listening Dashboard")
st.markdown("An overview of your most listened to tracks and artists.")

# --- Sidebar for Filters ---
with st.sidebar:
    st.header("Filters")
    time_range = st.selectbox(
        "Select Time Range:",
        options=['short_term', 'medium_term', 'long_term'],
        format_func=lambda x: x.replace('_', ' ').title(),
        index=1
    )
    category = st.selectbox("Choose Category:", ["Tracks", "Artists"])
    top_n = st.slider("Select number of top items:", 5, 20, 10)

# --- Filter Data ---
if category == "Tracks":
    df = tracks[tracks['time_range'] == time_range].copy()
    label_col = "name"
    value_col = "user_listens"
    title = f"Top {top_n} Tracks"
else:
    df = artists[artists['time_range'] == time_range].copy()
    label_col = "name"
    value_col = "user_listens"
    title = f"Top {top_n} Artists"

df_top_n = df.sort_values(value_col, ascending=False).head(top_n)
df_top_n['percent_of_total'] = (df_top_n[value_col] / df_top_n[value_col].sum() * 100).round(2)

# --- Display KPIs ---
st.subheader(f"{title} - {time_range.replace('_', ' ').title()}")

total_listens = int(df_top_n[value_col].sum())
top_item_name = df_top_n.iloc[0][label_col]
top_item_plays = int(df_top_n.iloc[0][value_col])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label=f"Total Plays for Top {top_n}", value=f"{total_listens:,}")
with col2:
    st.metric(label=f"Most Played {category.rstrip('s')}", value=top_item_name)
with col3:
    st.metric(label="Plays for Top Item", value=f"{top_item_plays:,}")

st.markdown("---")

# --- Visualizations and Data Table ---
col_chart, col_data = st.columns([2, 1])

with col_chart:
    st.subheader("Plays Distribution")
    bar_chart = alt.Chart(df_top_n).mark_bar().encode(
        x=alt.X(f'{value_col}:Q', title='Number of Plays'),
        y=alt.Y(f'{label_col}:N', sort='-x', title=category.rstrip('s')),
        color=alt.Color(f'{label_col}:N', legend=None),
        tooltip=[
            alt.Tooltip(label_col, title=category.rstrip('s')),
            alt.Tooltip(value_col, title="Plays"),
            alt.Tooltip('percent_of_total', title="% of Total", format=".2f")
        ]
    ).properties(height=alt.Step(30))
    
    # REVERTED LINE
    st.altair_chart(bar_chart, use_container_width=True)

with col_data:
    st.subheader("Data View")
    
    # REVERTED LINE
    st.dataframe(
        df_top_n[[label_col, value_col, 'percent_of_total']],
        column_config={
            label_col: category.rstrip('s'),
            value_col: "Plays",
            'percent_of_total': "% of Total"
        },
        hide_index=True,
        use_container_width=True
    )

st.markdown("---")
st.subheader("Alternative View: Donut Chart")

donut_chart = alt.Chart(df_top_n).mark_arc(innerRadius=100).encode(
    theta=alt.Theta(field="percent_of_total", type="quantitative"),
    color=alt.Color(field=label_col, type="nominal", title=category),
    tooltip=[
        label_col,
        alt.Tooltip(value_col, title="Plays"),
        alt.Tooltip("percent_of_total", title="% of Total", format=".2f")
    ]
)

# REVERTED LINE
st.altair_chart(donut_chart, use_container_width=True)