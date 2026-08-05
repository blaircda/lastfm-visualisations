import streamlit as st
import matplotlib.pyplot as plt

from main import *

tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])




with tab1:
    st.header("Tracks")
    N = st.number_input(
        "Top N", value=10, placeholder="Type a number...",
        min_value = 1, max_value = 100, key ="N_tracks"
    )

    top_df = song_plays_df.head(N).copy()
    track = st.selectbox("Track", top_df["track"])
    fig = plot_play_history(top_df.loc[top_df["track"] == track].iloc[0]["plays_yearly_absolute"])
    st.pyplot(fig)
    
with tab2:
    st.header("Artists")
    N = st.number_input(
        "Top N", value=10, placeholder="Type a number...",
        min_value = 1, max_value = 100, key ="N_artists"
    )

    top_df = artist_plays_df.head(N).copy()
    track = st.selectbox("Artist", top_df["artist"])
    fig = plot_play_history(top_df.loc[top_df["artist"] == track].iloc[0]["plays_yearly_absolute"])
    st.pyplot(fig)
    
with tab3:
    st.header("Albums")
    N = st.number_input(
        "Top N", value=10, placeholder="Type a number...",
        min_value = 1, max_value = 100, key = "N_albums"
    )

    top_df = album_plays_df.head(N).copy()
    track = st.selectbox("Album", top_df["album"])
    fig = plot_play_history(top_df.loc[top_df["album"] == track].iloc[0]["plays_yearly_absolute"])
    st.pyplot(fig)




#plot_plays_top(song_plays_df,10)
