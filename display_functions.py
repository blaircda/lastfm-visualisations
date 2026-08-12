import pandas as pd
import streamlit as st
from plot_functions import *

def filter_play_history(df_summary, display_item):
    """
    """
    df = df_summary[display_item]
    min_ranking = 1
    max_ranking = len(df)
    ranking = st.slider("Ranking", min_ranking, max_ranking, (1, 50), key = f"{display_item}_ranking_slider")
    top_df = df.iloc[ranking[0]-1:ranking[1]]

    min_total_plays = min(top_df)
    max_total_plays = max(top_df)

    if min_total_plays != max_total_plays:
        total = st.slider("Total playcount", min_value = min_total_plays,  max_value = max_total_plays, value = ( min_total_plays, max_total_plays), key = f"{display_item}_total_play_slider")
        sel = top_df[ (top_df >= total[0] ) & (top_df <= total[1]) ]
    else:
        st.write(f"Total playcount: {min_total_plays}")
        sel = top_df
    return sel

def show_play_history(df_history, df_summary, filter_sel, display_item):

    selection = st.multiselect(
                f"{display_item.capitalize()} ({len(filter_sel)} options)",
                filter_sel.index,
                format_func = lambda x : format_item(x,df_summary[display_item]),
                key = f"{display_item}_select")
                
    #st.write(f"{len(selection)} selected of {len(filter_df)}")

    plot_options = {
        "Calendar years": {
        "type": "cal",
         "period": "YS",   
         "cumulative": False
         },
        "Calendar years (cumulative)": {
        "type": "cal",
         "period": "YS",   
         "cumulative": True
         },
        "Calendar months": {
        "type": "cal",
         "period": "ME",   
         "cumulative": False
         },
        "Calendar months (cumulative)": {
        "type": "cal",
         "period": "ME",   
         "cumulative": True
         },
        "Calendar days": {
        "type": "cal",
         "period": "D",   
         "cumulative": False
         },
        "Calendar days (cumulative)": {
        "type": "cal",
         "period": "D",   
         "cumulative": True
         },
        "Years since first listen": {
        "type": "rel",
         #"period": "YS",   
         "cumulative": False
         },
        "Years since first listen (cumulative)": {
        "type": "rel",
         #"period": "YS",   
         "cumulative": True
         },
        "Months aggregated": {
         "type": "agg",
         "agg_period": "month",   
         "cumulative": False
         },
        "Days aggregated": {
         "type": "agg",
         "agg_period": "weekday",   
         "cumulative": False
         },
        "Hour aggregated (timezone not dealt with)": {
         "type": "agg",
         "agg_period": "hour",   
         "cumulative": False
         },
        "Day and hour aggregated (timezone not dealt with)": {
         "type": "agg",
         "agg_period": "day and hour",   
         "cumulative": False
         }
    }   
    
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
    options = plot_options[select_plot_type]

    if selection:
        if display_item == "artist":
            grouping = ["artist"]
            col = "artist"
            mask = df_history["artist"].isin(selection)
        else:
            grouping = [display_item, "artist"]
            col = display_item+"_artist"
            mask = df_history[col].isin(selection)

        filtered = df_history[mask]

        # calendar time filtering
        if options["type"] == "cal":
            full_index = df_history.resample(options["period"]).size().index
            plays = filtered.groupby(col).resample(options["period"]).size().unstack(-1, fill_value=0)
            plays = plays.reindex(columns = full_index, fill_value=0)
        # relative time filtering
        elif options["type"] == "rel":
            # copy the filtered dataframe
            plays = filtered.copy()
            # extract the first listen for each item in col
            first_listen = filtered.groupby(col).apply(lambda x: x.index.min())
            # write first listen as a new column
            plays["first_listen"] = plays[col].map(first_listen)
            # compute years elapsed since first listen and write as a new column
            plays["years_since_first_listen"] = (plays.index - plays["first_listen"]).dt.days // 365
            # aggregate the number of plays in each year since first listen
            plays = plays.groupby([col,"years_since_first_listen"]).size()
            # reindex within each item to fill in missing zeros within the range we have listening data for
            # NOT adding extra zeros at the end
            # finally unstack to get a dataframe where the index is the item and the columns are the years since first listen
            plays = plays.groupby(level=0).apply(
                    lambda x: x.droplevel(0).reindex(range(x.index.get_level_values(1).max()+1), fill_value=0)
            ).unstack("years_since_first_listen")
        # aggregations
        elif options["type"] == "agg":
            agg_period = options["agg_period"]
            times = {
                "month": filtered.index.month,
                "weekday": filtered.index.weekday,
                "hour": filtered.index.hour,
                "day and hour": filtered.index.weekday * 24 + filtered.index.hour
            }

            domains = {
            "month": range(1, 13),
            "weekday": range(7),
            "hour": range(24),
            "day and hour": range(168),
            }

            plays = filtered.groupby([col, times[agg_period]]).size()
            # count zero values
            plays = plays.groupby(level=0).apply(
                    lambda x: x.droplevel(0).reindex(domains[agg_period], fill_value=0)
            ).unstack("datetime_utc")
        fig = plot_play_histories(plays, options)
        st.pyplot(fig,width='stretch')

def show_all_history(df, summary_df):
    
    start, end = st.slider("Date range", df.index.min().to_pydatetime(), df.index.max().to_pydatetime(), value=( df.index.min().to_pydatetime(), df.index.max().to_pydatetime()) )

    plot_options = {
        "Calendar years": {
        "type": "cal",
         "period": "YS",   
         "cumulative": False
         },
        "Calendar years (cumulative)": {
        "type": "cal",
         "period": "YS",   
         "cumulative": True
         },
        "Calendar months": {
        "type": "cal",
         "period": "ME",   
         "cumulative": False
         },
        "Calendar months (cumulative)": {
        "type": "cal",
         "period": "ME",   
         "cumulative": True
         },
        "Calendar days": {
        "type": "cal",
         "period": "D",   
         "cumulative": False
         },
        "Calendar days (cumulative)": {
        "type": "cal",
         "period": "D",   
         "cumulative": True
         },
        "Months aggregated": {
         "type": "agg",
         "agg_period": "month",   
         "cumulative": False
         },
        "Days aggregated": {
         "type": "agg",
         "agg_period": "weekday",   
         "cumulative": False
         },
        "Hour aggregated (timezone not dealt with)": {
         "type": "agg",
         "agg_period": "hour",   
         "cumulative": False
         },
        "Day and hour aggregated (timezone not dealt with)": {
         "type": "agg",
         "agg_period": "day and hour",   
         "cumulative": False
         }
    }

    select_plot_type = st.selectbox(
                        "Time range",
                        plot_options.keys(),
                        key = f"everything_type_select")
    options = plot_options[select_plot_type]

    if select_plot_type:
        if options["type"] == "cal":
            fig = plot_time_data(df, options["period"], start, end, options["cumulative"])
        # aggregations
        elif options["type"] == "agg":
            agg_period = options["agg_period"]
            fig = plot_time_agg(df, agg_period, start, end)
        st.pyplot(fig,width='stretch')
        
########################################################################

def show_power_laws(df, df_summary, display_item):
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
                format_func = lambda x : format_item(x,df_summary[display_item]),
                key = f"{display_item}_select_PL")

    fig_ad = plot_amplitudes_decays_selection(filter_df, selection)
    st.pyplot(fig_ad)
    if selection:
        fig = plot_fit_multi(filter_df, selection, power_law)
        st.pyplot(fig)


########################################################################
def show_novelties_in_time(data, display_item):
    """
    displays graphs of old vs new plays by year
    """
    df = data[display_item]
    figs= plot_novelties_in_time(df)

    st.subheader(f"Number of distinct old vs new {display_item}s played")
    st.pyplot(figs["items"])
    st.pyplot(figs["items_ratio"])
    st.subheader(f"Total plays of old vs new {display_item}s")
    st.pyplot(figs["plays"])
    st.pyplot(figs["plays_ratio"])


def format_item(item, top_df):
    """
    handles formatting of tuples (track/album, artist) as opposed to just artist
    """
    if type(item) == tuple:
        lbl = ' - '.join(item)
    else:
        lbl = item
    return f"{lbl} ({top_df[item]} plays)"
