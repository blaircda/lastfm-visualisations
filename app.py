import streamlit as st
from display_functions import  *
from organise_data import *
from config import *

st.set_page_config(layout="wide", page_title="LastFM visualisations")
padl, content, padr = st.columns([0.15,0.7,0.15])

listening_data, summary, novelty = analyse_history_csv(history_file, excludes, whereabouts)
    
start = listening_data.index.min()
end = listening_data.index.max()
total_plays = len(listening_data)

with content:
    st.title("LastFM visualisations")
    st.write("Data: csv download via https://mainstream.ghan.nl/export.html")
    st.write(f"Timespan: {start.strftime("%Y-%m-%d")} to {end.strftime("%Y-%m-%d")}. Total plays: {total_plays}")
    # create tabs for different  visualisations
    play_hist_tab, power_law_tab, old_new_tab = st.tabs(["Play histories", "Power laws", "Old vs new"])

########################################################################
# play histories
########################################################################
with play_hist_tab:
    st.header("Play histories")
    tab1, tab2, tab3, tab4 = st.tabs(["Tracks", "Artists", "Albums", "Everything"])
    with tab1:
        first_sel = filter_play_history(summary, "track", key="ph")
        show_play_history(listening_data, summary, first_sel, "track")
    with tab2:
        first_sel = filter_play_history(summary, "artist", key="ph")
        show_play_history(listening_data, summary, first_sel, "artist")
    with tab3:
        first_sel = filter_play_history(summary, "album", key="ph")
        show_play_history(listening_data, summary, first_sel, "album")
    with tab4:
        show_all_history(listening_data, life_divisions)
        
########################################################################
# power law fits of listening data
########################################################################
with power_law_tab:
    st.header("Power laws")
    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    with tab1:
        with st.expander("Filter tracks to include"):
            first_sel = filter_play_history(summary, "track", key="pl")
            second_sel = multisel_items(first_sel, summary, "track", key = "pl_second", max_sels=250)
        if second_sel:
            show_power_laws(listening_data, summary, second_sel, "track")
    with tab2:
        with st.expander("Filter artists to include"):
            first_sel = filter_play_history(summary, "artist", key="pl")
            second_sel = multisel_items(first_sel, summary, "artist", key = "pl_second", max_sels=250)
        if second_sel:
            show_power_laws(listening_data,summary, second_sel, "artist")
    with tab3:
        with st.expander("Filter albums to include"):
            first_sel = filter_play_history(summary, "album", key="pl")
            second_sel = multisel_items(first_sel, summary, "album", key = "pl_second", max_sels=250)
        if second_sel:
            show_power_laws(listening_data,summary, second_sel, "album")
            
########################################################################
# old vs new plays by year
########################################################################
with old_new_tab:
    st.header("Old vs new")
    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    with tab1:
        show_novelties_in_time(novelty, "track")
    with tab2:
        show_novelties_in_time(novelty, "artist")
    with tab3:
        show_novelties_in_time(novelty, "album")
