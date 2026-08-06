import streamlit as st

from main import *
from plot_functions import *
from power_laws import *

st.set_page_config(layout="wide")

mt1, mt2, mt3 = st.tabs(["Play histories", "Power laws", "Old vs new"])

def format_artist(label_name, display_item, top_df):
    if display_item != "artist":
        return f"{label_name} - {top_df.at[label_name, 'artist']} ({top_df.at[label_name,'total_plays']} plays)"
    else:
        return f"{label_name} ({top_df.at[label_name,'total_plays']} plays)"

def show_play_history(df, display_item):
    """
    function to manage display of play_histories (calendar year, absolute, relative)
    for different display_item
    which can be one of: track, artist, album
    """
    #st.write(display_item)
    
    N = st.number_input(
        "Top N", value=100,
        min_value = 1, max_value = 250, key = f"{display_item}_N"
    ) 

    top_df = df.head(N).set_index(display_item)
    
    selection = st.multiselect(
                display_item.capitalize(),
                top_df.index,
                format_func = lambda x : format_artist(x, display_item, top_df),
                key = f"{display_item}_select")

    plot_options = {
        "Calendar years": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": False
         },
         "Years since start of data": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": False
         },
         f"Years since first listen of {display_item}": {
         "column": "plays_yearly_relative",
         "x": None,
         "xlabel": "Years since first listen of {to_display}",
         "cumulative": False,
         },
        "Calendar years (cumulative)": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": True,
         },
         "Years since start of data (cumulative)": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": True,
         },
         f"Years since first listen of {display_item} (cumulative)": {
         "column": "plays_yearly_relative",
         "x": None,
         "xlabel": "Years since first listen of {to_display}",
         "cumulative": True,
        }
    }
    
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
                            
    options = plot_options[select_plot_type]

    if selection:
        fig = plot_play_histories(top_df, selection, options)
        st.pyplot(fig,width='stretch')
        
    #plays = top_df.at[selection,  sel_type]
    #st.pyplot(fig)

def show_novelties_in_time(df, display_item):
    figs= plot_novelties_in_time(df)
    for f in figs:
        st.pyplot(f)

def show_power_laws(df, display_item):
    #top_df = df.head(N).set_index(display_item)
    df = df.set_index(display_item)
    
    selection = st.selectbox(
                display_item.capitalize(),
                df.index,
                format_func = lambda x : format_artist(x, display_item, df),
                key = f"{display_item}_select_PL")

    if selection:
        fig = plot_fit(df, selection, power_law)
        st.pyplot(fig)

    fig = plot_amplitudes_decays(df, display_item)
    st.pyplot(fig)

# bare play histories
with mt1:
    st.header("Play histories")
    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    with tab1:
        show_play_history(song_plays_df, "track")
    with tab2:
        show_play_history(artist_plays_df, "artist")
    with tab3:
        show_play_history(album_plays_df, "album")
# powerlaws 
with mt2:
    st.header("Power laws")
    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    with tab1:
        show_power_laws(song_power_laws_df, "track")

    with tab2:
        show_power_laws(artist_power_laws_df, "artist")
    with tab3:
        show_power_laws(album_power_laws_df, "album")
# old vs new
with mt3:
    st.header("Old vs new")
    tab1, tab2, tab3 = st.tabs(["Tracks", "Artists", "Albums"])
    with tab1:
        show_novelties_in_time(song_yearly_novelty_df, "track")
    with tab2:
        show_novelties_in_time(artist_yearly_novelty_df, "artist")
    with tab3:
        show_novelties_in_time(album_yearly_novelty_df, "album")






#plot_plays_top(song_plays_df,10)
