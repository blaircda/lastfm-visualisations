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
            
def show_play_history(df, display_item, calendar_axis, monthly_axis):
    """
    function to manage display of play_histories (calendar year, absolute, relative)
    for different display_item
    which can be one of: track, artist, album
    """
    min_ranking = 1
    max_ranking = len(df)
    ranking = st.slider("Ranking", min_ranking, max_ranking, (1, 50), key = f"{display_item}_ranking_slider")
    top_df = df.iloc[ranking[0]-1:ranking[1]]

    min_total_plays = min(top_df["total_plays"])
    max_total_plays = max(top_df["total_plays"])

    if min_total_plays != max_total_plays:
        total = st.slider("Total playcount", min_value = min_total_plays,  max_value = max_total_plays, value = ( min_total_plays, max_total_plays), key = f"{display_item}_total_play_slider")
        filter_df = top_df[ (top_df["total_plays"] >= total[0] ) & (top_df["total_plays"] <= total[1]) ]
    else:
        st.write(f"Total playcount: {min_total_plays}")
        filter_df = top_df

    selection = st.multiselect(
                f"{display_item.capitalize()} ({len(filter_df)} options)",
                filter_df.index,
                format_func = lambda x : format_item(x,top_df),
                key = f"{display_item}_select")
    #st.write(f"{len(selection)} selected of {len(filter_df)}")

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
         "xlabel": "Years since first listen",
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
         "xlabel": "Years since first listen",
         "cumulative": True,
        },
        "Calendar months": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months (cumulative)": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": True
         },
        "Calendar months since first listen": {
         "column": "plays_monthly_relative",
         "x": None,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months since first listen (cumulative)": {
         "column": "plays_monthly_relative",
         "x": None,
         "xlabel": "Month",
         "cumulative": True
         },
        "Months of the year aggregated": {
         "column": "plays_months",
         "x": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
         "xlabel": "Month ",
         "cumulative": False
         },
        "Days of the week aggregated": {
         "column": "plays_days",
         "x": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
         "xlabel": "Day",
         "cumulative": False
         },
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

def show_everything_history(df, display_item, calendar_axis, monthly_axis):
    """
    function to manage display of play_histories (calendar year, absolute, relative)
    for different display_item
    which can be one of: track, artist, album
    """
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
        "Calendar months": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months (cumulative)": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": True
         },
        "Months of the year aggregated": {
         "column": "plays_months",
         "x": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
         "xlabel": "Month ",
         "cumulative": False
         },
        "Days of the week aggregated": {
         "column": "plays_days",
         "x": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
         "xlabel": "Day",
         "cumulative": False
         },
    }
    
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
                            
    options = plot_options[select_plot_type]

    if select_plot_type:
        fig = plot_play_history(df, options)
        st.pyplot(fig,width='stretch')


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
    exponents = df["param_1"]

    sliders = []
    param_name = ["Coefficient", "Exponent"]
    for k in range(2):
        param = df[f"param_{k}"]    
        min_param = min(param)
        max_param = max(param)
        sliders.append( st.slider(param_name[k], min_param, max_param, (min_param, max_param), key=f"{display_item}_PL_slider_{k}") )

    filter_df = df[ (df["param_0"] >= sliders[0][0] ) & (df["param_0"] <= sliders[0][1]) &  (df["param_1"] >= sliders[1][0] ) & (df["param_1"] <= sliders[1][1]) ] 

    selection = st.multiselect(
                f"{display_item.capitalize()} ({len(filter_df)} options)",
                filter_df.index,
                format_func = lambda x : format_item(x,df),
                key = f"{display_item}_select_PL")

    fig_ad = plot_amplitudes_decays_selection(filter_df, selection)
    st.pyplot(fig_ad)
    if selection:
        fig = plot_fit_multi(filter_df, selection, power_law)
        st.pyplot(fig)
