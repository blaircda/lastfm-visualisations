import pandas as pd
import streamlit as st
from plot_functions import *

def format_item(item, top_df):
    """
    handles formatting of tuples (track/album, artist) as opposed to just artist
    """
    if type(item) == tuple:
        lbl = ' - '.join(item)
    else:
        lbl = item
    return f"{lbl} ({top_df.at[item,'total_plays']} plays)"
            
def show_play_history(df, display_item, calendar_axis):
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

    top_df = df.head(N)#.set_index(display_item)
    
    selection = st.multiselect(
                display_item.capitalize(),
                top_df.index,
                format_func = lambda x : format_item(x,top_df),
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
    """
    displays graphs of old vs new plays by year
    """
    figs= plot_novelties_in_time(df)

    st.subheader(f"Number of distinct old vs new {display_item}s played")
    st.pyplot(figs["items"])
    st.pyplot(figs["items_ratio"])
    st.subheader(f"Total plays of old vs new {display_item}s")
    st.pyplot(figs["plays"])
    st.pyplot(figs["plays_ratio"])

def show_power_laws(df, display_item):
    """
    allows selection and display of power law graphs
    """
    
    #exponents = [p[1] for p in df["fit_vars"]]
    #min_exp = min(exponents)
    #max_exp = max(exponents)
    #N = st.slider("Exponent range", -min_exp, -max_exp, (-min_exp, -max_exp), key=f"{display_item}_PL_slider")
    #st.write("Selected range:", N)

    selection = st.multiselect(
                display_item.capitalize(),
                df.index,
                format_func = lambda x : format_item(x,df),
                key = f"{display_item}_select_PL")

    #if len(selection)>1:
    fig_ad = plot_amplitudes_decays_selection(df, selection)
    st.pyplot(fig_ad)
    if selection:
        fig = plot_fit_multi(df, selection, power_law)
        st.pyplot(fig)


def show_power_law_summaries(df, display_item):
    """
    unused function to display power law summaries for chosen range of entries
    """
    st.write(display_item.capitalize())
    N = st.slider("Select a number range", 1, 250, (1, 20), key=f"{display_item}_PL_slider")
    st.write("Selected range:", N)
    st.write(len(df))
    df = df.iloc[N[0]: N[1]+1]
    fig = plot_amplitudes_decays(df)
    st.pyplot(fig)
