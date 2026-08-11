import streamlit as st
from display_functions import  *
from organise_data import *

st.set_page_config(layout="wide", page_title="LastFM visualisations")
col1, col2, col3 = st.columns([0.15,0.7,0.15])

history_file = "recenttracks-antiselfdual-1737987394.csv"
excludes = ["Chris Blair", "Super Simple Songs"]

listening_data, summary = analyse_history_csv(history_file, excludes)

start = listening_data.index.min()
end = listening_data.index.max()
total_plays = len(listening_data)

with col2:
    st.title("LastFM visualisations")

    st.write("Data: csv download via https://mainstream.ghan.nl/export.html")
    st.write(f"Timespan: {start.strftime("%Y-%m-%d")} to {end.strftime("%Y-%m-%d")}. Total plays: {total_plays}")


    mt1, mt2, mt3 = st.tabs(["Play histories", "Power laws", "Old vs new"])
    # bare play histories
    with mt1:
        st.header("Play histories")
        tab1, tab2, tab3, tab4 = st.tabs(["Tracks", "Artists", "Albums", "Everything"])
        with tab1:
            first_sel = filter_play_history(summary, "track")
            show_play_history(listening_data, summary, first_sel, "track")
        with tab2:
            first_sel = filter_play_history(summary, "artist")
            show_play_history(listening_data, summary, first_sel, "artist")
        with tab3:
            first_sel = filter_play_history(summary, "album")
            show_play_history(listening_data, summary, first_sel, "album")
        with tab4:
            pass
    # powerlaws 
    #with mt2:
    #    st.header("Power laws")
    #    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    #    with tab1:
    #        show_power_laws(data["track_pl"], "track")
    #    with tab2:
    #        show_power_laws(data["artist_pl"], "artist")
    #    with tab3:
    #        show_power_laws(data["album_pl"], "album")
        #with tab4:
        #    show_power_law_summaries(song_power_laws_df, "track")
        #    show_power_law_summaries(album_power_laws_df, "album")
        #    show_power_law_summaries(artist_power_laws_df, "artist")
    # old vs new
    #with mt3:
    #    st.header("Old vs new")
    #    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    #    with tab1:
    #        show_novelties_in_time(data["track_novelty"], "track")
    #    with tab2:
    #        show_novelties_in_time(data["artist_novelty"], "artist")
    #    with tab3:
    #        show_novelties_in_time(data["album_novelty"], "album")
