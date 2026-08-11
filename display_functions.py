import pandas as pd
import streamlit as st
from plot_functions import *
from plot_functions_pt import *

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
            first_listen = filtered.groupby(col).apply(lambda x: x.index.min())
            plays = filtered.copy()
            plays["first_listen"] = plays[col].map(first_listen)
            plays["years_since_first_listen"] = (plays.index - plays["first_listen"]).dt.days // 365
            plays = plays.groupby([col,"years_since_first_listen"]).size()
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


def format_item(item, top_df):
    """
    handles formatting of tuples (track/album, artist) as opposed to just artist
    """
    if type(item) == tuple:
        lbl = ' - '.join(item)
    else:
        lbl = item
    return f"{lbl} ({top_df[item]} plays)"
