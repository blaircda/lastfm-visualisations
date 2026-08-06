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

    selection = st.multiselect(
                tab_title,
                top_df.index,
                format_func = format_artist,
                key = f"{key}_select")

    plot_options = {
        "Calendar years": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year"
         },
         "Years since start of data": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data"
         },
         f"Years since first listen of {to_display}": {
         "column": "plays_yearly_relative",
         "x": None,
         "xlabel": "Years since first listen of {to_display}"
        }
    }
    
    select_plot_type = st.selectbox(
                            "Type of plays",
                            plot_options.keys(),
                            key = f"{key}_type_select")
                            
    options = plot_options[select_plot_type]

    if selection:
        fig = plot_play_histories(top_df, selection, options)
        st.pyplot(fig)
        
    #plays = top_df.at[selection,  sel_type]
    
    #print( top_df.loc[selection] )

    #if sel_type == "plays_yearly_cal":
    #    fig = plot_play_history(year_axis, plays)
    #else:
    #    fig = plot_play_history(range(len(plays)), plays)

    #st.pyplot(fig)
    
with tab1:
    show_play_history(song_plays_df, "track", "Tracks", "tracks")
with tab2:
    show_play_history(artist_plays_df, "artist", "Artists", "artist")
with tab3:
    show_play_history(album_plays_df, "album", "Albums", "album")




#plot_plays_top(song_plays_df,10)
