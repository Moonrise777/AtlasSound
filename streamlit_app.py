# --------------------------------------------------
#                  LIBRARIES
# --------------------------------------------------

import altair as alt
import pandas as pd
import streamlit as st

# --------------------------------------------------
#               PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Atlas Sound 🎵",
    page_icon="💚",
    layout="wide"
)

# --------------------------------------------------
#               CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: serif;
}

h1, h2, h3 {
    font-family: serif;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
#               HERO SECTION
# --------------------------------------------------

st.markdown("""
<div style="padding-top:20px">

<p style="
letter-spacing:4px;
font-size:12px;
color:#BA6F4D;">
SPOTIFY ANALYTICS
</p>

<h1 style="
font-size:70px;
line-height:0.9;
margin-bottom:0px;
color:#163D35;">
Find the patterns in music
</h1>

<h1 style="
font-size:70px;
line-height:0.9;
font-style:italic;
font-weight:400;
color:#BA6F4D;">
that move us.
</h1>

<p style="
font-size:20px;
max-width:700px;
color:#4D4741;">
Explore Spotify's global music landscape from 2009–2025,
compare it against the most streamed songs of all time,
and uncover the audio characteristics driving success.
</p>

</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
#                  INDEX
# --------------------------------------------------

st.divider()

st.markdown("## ₊‧°𐐪 Dashboard Guide 𐑂°‧₊")

st.markdown("""
### 🔑 Key Metrics
Get a high-level overview of Spotify data with KPIs covering tracks, artists, streaming volume, and dataset size. Perfect for quickly understanding the scale of the music ecosystem.

### 🎧 Explore Spotify Music
Interactively filter artists and popularity ranges to focus your analysis on specific segments of the music catalog.

### 🔥 Most Popular Tracks
Discover the songs with the highest popularity scores and identify the tracks currently dominating listener attention.

### 🎵 Most Streamed Songs of All Time
Explore Spotify's most successful songs ever released and compare streaming performance across artists and titles.

### 📊 Popularity Distribution
Understand how popularity scores are distributed across thousands of tracks and identify patterns among mainstream and niche music.

### 🚨 Explicit vs Non-Explicit
Analyze the relationship between explicit content and track prevalence within Spotify's catalog.

### 👑 Most Featured Artists
Identify artists with the largest presence in the dataset and understand which performers dominate the platform.

### ⚙️ Data Engineering Overview
Monitor dataset quality through completeness, duplicate records, missing values, and overall data health metrics.
""")

st.divider()

# --------------------------------------------------
#                   DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():

    # Spotify Global Music Dataset (2009–2025)
    global_df = pd.read_csv(
        "data/spotify_data_clean.csv"
    )

    # Spotify Most Streamed Songs
    streamed_df = pd.read_csv(
        "data/spotify_most_streamed_songs.csv"
    )

    return global_df, streamed_df


global_df, streamed_df = load_data()

# --------------------------------------------------
#          TEXT NORMALIZATION / ENCODING FIX
# --------------------------------------------------

def fix_encoding(value):
    if isinstance(value, str):
        try:
            return value.encode("latin1").decode("utf-8")
        except:
            return value
    return value

for df in [global_df, streamed_df]:
    text_cols = df.select_dtypes(include="object").columns

    for col in text_cols:
        df[col] = (
            df[col]
            .astype(str)
            .apply(fix_encoding)
            .str.strip()
        )

# --------------------------------------------------
#           STANDARDIZE COLUMN NAMES
# --------------------------------------------------

global_df.columns = global_df.columns.str.strip().str.lower()
streamed_df.columns = streamed_df.columns.str.strip().str.lower()
global_df = global_df.drop_duplicates()
streamed_df = streamed_df.drop_duplicates()

global_df = global_df.replace(["", "nan", "None"], pd.NA)
streamed_df = streamed_df.replace(["", "nan", "None"], pd.NA)

# Adjust these if your dataset names differ
global_df = global_df.rename(
    columns={
        "track_name": "song",
        "artist_name": "artist",
        "track_popularity": "popularity"
    }
)

# Split "Artist and Title"
if "artist and title" in streamed_df.columns:

    split_cols = streamed_df["artist and title"].str.split(
        " - ",
        n=1,
        expand=True
    )

    streamed_df["artist"] = split_cols[0]
    streamed_df["song"] = split_cols[1]

if "streams" in streamed_df.columns:
    streamed_df["streams"] = (
        streamed_df["streams"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )

# --------------------------------------------------
#                DATA PREVIEW
# --------------------------------------------------

st.subheader("🌷 Dataset Preview")

tab1, tab2 = st.tabs(
    [
        "Global Music Dataset",
        "Most Streamed Songs"
    ]
)

with tab1:
    st.dataframe(global_df.head())

with tab2:
    st.dataframe(streamed_df.head())

# --------------------------------------------------
#                  KPI SECTION
# --------------------------------------------------

st.subheader("✨ Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Tracks",
        f"{len(global_df):,}"
    )

with col2:
    st.metric(
        "Artists",
        global_df["artist"].nunique()
    )

with col3:
    st.metric(
        "Top Songs Dataset",
        f"{len(streamed_df):,}"
    )

with col4:
    st.metric(
        "Total Streams",
        f"{streamed_df['streams'].sum()/1_000_000_000:.1f}B"
    )

# --------------------------------------------------
#                   FILTERS
# --------------------------------------------------

st.divider()

st.subheader("🎧 Explore Your Music Universe")

artist_filter = st.multiselect(
    "Artist",
    sorted(global_df["artist"].dropna().unique())
)

popularity_range = st.slider(
    "Spotify Popularity Score",
    int(global_df["popularity"].min()),
    int(global_df["popularity"].max()),
    (
        int(global_df["popularity"].min()),
        int(global_df["popularity"].max())
    )
)

global_filtered = global_df.copy()

if artist_filter:
    global_filtered = global_filtered[
        global_filtered["artist"].isin(artist_filter)
    ]

global_filtered = global_filtered[
    global_filtered["popularity"].between(
        popularity_range[0],
        popularity_range[1]
    )
]

st.caption(
    "Spotify popularity is a score from 0–100 indicating how popular a track is currently. Higher values mean the song is receiving more recent listener activity."
)

# --------------------------------------------------
#               TRACK POPULARITY
# --------------------------------------------------

st.subheader("🔥 Most Popular Tracks ˃ 𖥦 ˂")

popular_tracks = (
    global_filtered
    .sort_values(
        "popularity",
        ascending=False
    )
    .head(25)
)
display_tracks = popular_tracks.copy()

if "track_id" in display_tracks.columns:
    display_tracks = display_tracks.drop(
        columns=["track_id"]
    )

st.dataframe(
    display_tracks,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
#              TOP STREAMED SONGS
# --------------------------------------------------

st.subheader("🎵 Most Streamed Songs Of All Time ♡")

top_streams = (
    streamed_df
    .sort_values(
        "streams",
        ascending=False
    )
    .head(20)
)

chart_streams = (
    alt.Chart(top_streams)
    .mark_bar(color="#CDB4DB")
    .encode(
        x=alt.X(
            "streams:Q",
            title="Streams"
        ),
        y=alt.Y(
            "song:N",
            sort="-x",
            title="Song"
        ),
        tooltip=[
            "artist",
            "song",
            "streams"
        ]
    )
    .properties(height=600)
)

st.altair_chart(
    chart_streams,
    use_container_width=True
)

# --------------------------------------------------
#         POPULARITY DISTRIBUTION
# --------------------------------------------------

st.subheader("📊 Popularity Distribution ୨୧")

pop_hist = (
    alt.Chart(global_filtered)
    .mark_bar()
    .encode(
        x=alt.X(
            "popularity:Q",
            bin=True,
            title="Popularity Score ✨"
        ),
        y=alt.Y(
            "count()",
            title="Tracks ♡"
        ),
        color=alt.Color(
            "popularity:Q",
            scale=alt.Scale(
                range=[
                    "#FFD6E8",  # pink
                    "#FFE4B5",  # peach
                    "#FFF3B0",  # yellow
                    "#D8F3DC",  # mint
                    "#CDE7FF",  # blue
                    "#E4C1F9"   # lavender
                ]
            ),
            legend=None
        )
    )
)

st.altair_chart(
    pop_hist,
    use_container_width=True
)

# --------------------------------------------------
#       EXPLICIT VS NON-EXPLICIT SONGS
# --------------------------------------------------

if "explicit" in global_filtered.columns:

    st.subheader("🚨 Explicit vs Non-Explicit")

    explicit_df = (
        global_filtered
        .groupby("explicit")
        .size()
        .reset_index(name="tracks")
    )

    explicit_chart = (
        alt.Chart(explicit_df)
        .mark_arc(
            innerRadius=60
        )
        .encode(
            theta="tracks:Q",
            color=alt.Color(
                "explicit:N",
                scale=alt.Scale(
                    range=[
                        "#FFCAD4",
                        "#A0E7E5"
                    ]
                )
            )
        )
    )

    st.altair_chart(
        explicit_chart,
        use_container_width=True
    )

# --------------------------------------------------
#           TOP ARTISTS BY TRACKS
# --------------------------------------------------

st.subheader("👑 Most Featured Artists")

artist_count = (
    global_filtered
    .groupby("artist")
    .size()
    .reset_index(name="tracks")
    .sort_values(
        "tracks",
        ascending=False
    )
    .head(15)
)

artist_chart = (
    alt.Chart(artist_count)
    .mark_bar(color="#A8DADC")
    .encode(
        x=alt.X(
            "tracks:Q",
            title="Tracks"
        ),
        y=alt.Y(
            "artist:N",
            sort="-x"
        ),
        tooltip=[
            "artist",
            "tracks"
        ]
    )
    .properties(height=500)
)

st.altair_chart(
    artist_chart,
    use_container_width=True
)

# --------------------------------------------------
#      AUDIO FEATURE ANALYSIS
# --------------------------------------------------

audio_cols = [
    c for c in [
        "danceability",
        "energy",
        "acousticness",
        "instrumentalness",
        "liveness",
        "speechiness",
        "valence"
    ]
    if c in global_filtered.columns
]

if len(audio_cols) > 0:

    st.subheader("🎛 Audio Feature Averages")

    features_df = pd.DataFrame({
        "Feature": audio_cols,
        "Average": [
            global_filtered[c].mean()
            for c in audio_cols
        ]
    })

    feature_chart = (
        alt.Chart(features_df)
        .mark_bar(color="#99C5B5")
        .encode(
            x="Average:Q",
            y=alt.Y(
                "Feature:N",
                sort="-x"
            ),
            tooltip=[
                "Feature",
                "Average"
            ]
        )
    )

    st.altair_chart(
        feature_chart,
        use_container_width=True
    )

# --------------------------------------------------
#           DATA QUALITY DASHBOARD
# --------------------------------------------------

st.divider()

st.subheader("⚙️ Data Engineering Overview")

total_missing = global_df.isna().sum().sum()

duplicates = global_df.duplicated().sum()

completeness = (
    1 -
    (
        total_missing /
        global_df.size
    )
) * 100

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Rows",
        len(global_df)
    )

with c2:
    st.metric(
        "Duplicates",
        duplicates
    )

with c3:
    st.metric(
        "Missing Values",
        total_missing
    )

with c4:
    st.metric(
        "Completeness",
        f"{completeness:.1f}%"
    )

# --------------------------------------------------
#                   FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown("""
### About this project

✅ Spotify Global Music Dataset (2009–2025)

✅ Spotify Most Streamed Songs Of All Time

✅ Music Trend Analysis

✅ Artist Performance Analysis

✅ Interactive BI Dashboard

Built with Streamlit, Pandas and Altair.
""")