import streamlit as st

from main import *
from plot_functions import *

tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])

def show_play_history( df, to_display, tab_title, key):
    st.header(tab_title)

    N = st.number_input(
        "Top N", value=10,
        min_value = 1, max_value = 100, key = f"{key}_N"
    ) 

    top_df = df.head(N).set_index(to_display)

    def format_artist(label_name):
        if to_display != "artist":
            return f"{label_name} - {top_df.at[label_name, 'artist']}"
        else:
            return f"{label_name}"

    selection = st.selectbox(
                tab_title,
                top_df.index,
                format_func= format_artist,
                key = f"{key}_select")

    types_of_plays = {"By years since start of listening history": "plays_yearly_absolute",
                      f"By years since {to_display}": "plays_yearly_relative",
                      "By calendar years": "plays_yearly_cal"
                    }
    select_type_of_plays = st.selectbox(
                            "Type of plays",
                            types_of_plays.keys(),
                            key = f"{key}_type_select")
    sel_type = types_of_plays[select_type_of_plays]
    plays = top_df.at[selection,  sel_type]
    
    #print( top_df.loc[selection] )

    if sel_type == "plays_yearly_cal":
        fig = plot_play_history(year_axis, plays)
    else:
        fig = plot_play_history(range(len(plays)), plays)

    st.pyplot(fig)
    
with tab1:
    show_play_history(song_plays_df, "track", "Tracks", "tracks")
with tab2:
    show_play_history(artist_plays_df, "artist", "Artists", "artist")
with tab3:
    show_play_history(album_plays_df, "album", "Albums", "album")




#plot_plays_top(song_plays_df,10)
