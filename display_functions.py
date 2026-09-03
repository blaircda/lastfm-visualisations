import pandas as pd
import streamlit as st
import datetime as datetime
from plot_functions import *
from organise_data import relative_listens, calculate_fit

def filter_play_history(df_summary, display_item, key):
    """
    controls the selection of items of type display_item (artist, track-artist, album-artist)
    reading total playcount and ranking from df_summary
    key is a str to ensure the streamlit inputs are uniquely identified
    """
    df = df_summary[display_item]
    min_ranking = 1
    max_ranking = len(df)
    ranking = st.slider(
        "Ranking",
        min_value = min_ranking,
        max_value = max_ranking,
        value = (1, 50),
        key = f"{display_item}_ranking_slider_{key}"
    )

    # first filter by ranking selected
    top_df = df.iloc[ranking[0]-1:ranking[1]]

    # next filter by plays
    min_total_plays = min(top_df)
    max_total_plays = max(top_df)

    if min_total_plays != max_total_plays:
        total = st.slider(
            "Total playcount",
            min_value = min_total_plays,
            max_value = max_total_plays,
            value = ( min_total_plays, max_total_plays),
            key = f"{display_item}_total_play_slider_{key}"
            )
        sel = top_df[ (top_df >= total[0] ) & (top_df <= total[1]) ]
    else:
        # in case a unique ranking not a range has been selected cannot show a slider for playcount
        st.write(f"Total playcount: {min_total_plays}")
        sel = top_df
    return sel

def multisel_items(filter_sel, df_summary, display_item, key, max_sels=None):
    """
    defines a streamlit multiselect input
    filter_sel: filtered dataframe based on previous choices
    df_summary: contains information about total playcount
    display_item: which of artist, track-artist, album_artist we are interested in
    key: str to ensure the streamlit inputs are uniquely identified
    max_sels: set to limit number of selections that can be made  
    """
    sel = st.multiselect(
        f"{display_item.capitalize()} ({len(filter_sel)} options)",
        filter_sel.index,
        default = filter_sel.index[0:10],
        format_func = lambda x : format_item(x,df_summary[display_item]),
        max_selections = max_sels,
        key = f"{display_item}_select_{key}"
        )

    return sel

# predefined types of plots
calendar_plot_options = {
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
     }
}
relative_plot_options = {
    "Years since first listen": {
    "type": "rel",
     #"period": "YS",   
     "cumulative": False
     },
    "Years since first listen (cumulative)": {
    "type": "rel",
     #"period": "YS",   
     "cumulative": True
     }
}
aggregate_plot_options = {
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
    "Hour aggregated": {
     "type": "agg",
     "agg_period": "hour",   
     "cumulative": False
     },
    "Day and hour aggregated": {
     "type": "agg",
     "agg_period": "day and hour",   
     "cumulative": False
     }
    }   


def show_play_history(df_history, df_summary, filter_sel, display_item):
    """
    controls final selection of previously filtered listening history of display_item for plotting
    """

    # multiselection of content of filter_sel
    selection = multisel_items(
        filter_sel,
        df_summary,
        display_item,
        key=f"{display_item}_select",
        max_sels = 1000)              
    #st.write(f"{len(selection)} selected of {len(filter_df)}")

    # plot options
    plot_options = calendar_plot_options | relative_plot_options | aggregate_plot_options
    # plot option selection
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
    options = plot_options[select_plot_type]

    # only plot if a selection has been made
    if selection:

        # have to handle the artist vs track-artist or album-artist cases differently
        if display_item == "artist":
            grouping = ["artist"]
            filter_col = "artist"
            make_multi = None
        else:
            grouping = [display_item, "artist"]
            filter_col = display_item+"_artist"
            make_multi = grouping
            
        mask = df_history[filter_col].isin(selection)
        filtered = df_history[mask]

        # calendar time filtering
        if options["type"] == "cal":
            plays = calendar_listens(filtered, grouping, df_history, options["period"], make_multi)
        # relative time filtering
        elif options["type"] == "rel":
            plays, _ = relative_listens(filtered, filter_col, make_multi)
        # aggregations
        elif options["type"] == "agg":
            plays = aggregate_listens(filtered, filter_col, options["agg_period"], make_multi)

        # get the plot
        fig = plot_play_histories(plays, options)
        st.pyplot(fig,width='stretch')
        plt.close(fig)
        
def calendar_listens(df, grouping, df_history, period, make_multi=None):
    """
    df: filtered selection of listening history
    grouping: artist, track-artist, album-artist
    df_history: listening history dataframe
    period: calendar period to resample on
    make_multi: unused

    returns a dataframe with the play history in df resampled according to period
    the full listening history index of df_history is used to make sure that all play histories
    are recorded over the full time period
    """
    df = df.copy()
    df = df.set_index("local_datetime")
    full_index = df_history.set_index("local_datetime").resample(period).size().index
    plays = df.groupby(grouping).resample(period).size().unstack(-1, fill_value=0)
    plays = plays.reindex(columns = full_index, fill_value=0)
    #if make_multi:
    #    plays.index = pd.MultiIndex.from_tuples(plays.index, names=make_multi)
    return plays

@st.cache_data
def aggregate_listens(df, filter_col, agg_period, make_multi):
    """
    df: filtered selection of listening history
    filter_col: selects artist, track-artist, album-artist
    agg_period: time period on which to aggregate
    make_multi: use a multiindex in returned df for track-artist, album-artist
    """
    
    df = df.copy()
    df = df.set_index("local_datetime")

    # supported aggregrations
    times = {
        "month": df.index.month,
        "weekday": df.index.weekday,
        "hour": df.index.hour,
        "day and hour": df.index.weekday * 24 + df.index.hour
    }

    # how many "buckets" in each aggregations
    # used below to ensure that we have values in all buckets
    # for all items
    domains = {
    "month": range(1, 13),
    "weekday": range(7),
    "hour": range(24),
    "day and hour": range(168),
    }

    plays = df.groupby([filter_col, times[agg_period]]).size()
    # count zero values across the full domains 
    plays = plays.groupby(level=0).apply(
            lambda x: x.droplevel(0).reindex(domains[agg_period], fill_value=0)
    ).unstack(-1)

    if make_multi:
        plays.index = pd.MultiIndex.from_tuples(plays.index, names=make_multi)
    return plays
    
def show_all_history(df, life_divisions):
    """
    controls selection and plotting of complete listening history
    df: full listening history
    life_divisions: customisable date ranges of interest specified in config.py
    """
    
    df = df.set_index("local_datetime").sort_index()
    min_date = df.index.min().strftime("%Y-%m-%d")
    max_date = df.index.max().strftime("%Y-%m-%d")
    all_range = (min_date, max_date) 

    # if no life divisions are specified we will make a slider based on the full range
    if life_divisions is None:
        dates = all_range
    # otherwise we make a selectbox to easily apply custom ranges to the full range slider
    else:
        life_divisions = {
        k: (min_date if v[0] is None else v[0], max_date if v[1] is None else v[1]) for k,v in life_divisions.items() 
        }
        range_options = {"All": all_range} | life_divisions
    
        sel_range =st.selectbox(
            "Life divisions",
            range_options.keys(),
            format_func = lambda x : f"{x}  ({range_options[x][0]} to  {range_options[x][1]})"
        )
        dates = range_options[sel_range]

    sel_range_val = ( datetime.datetime.strptime(dates[0], '%Y-%m-%d'), datetime.datetime.strptime(dates[1], '%Y-%m-%d'))

    # slider to choose the date range to plot
    start, end = st.slider("Date range",
        min_value = df.index.min().to_pydatetime(),
        max_value = df.index.max().to_pydatetime(),
        value = sel_range_val
        )
        
    # plot options 
    plot_options = calendar_plot_options | aggregate_plot_options

    # plot type selection box
    select_plot_type = st.selectbox(
                        "Time range",
                        plot_options.keys(),
                        key = f"everything_type_select")
    options = plot_options[select_plot_type]

    # if a plot type is selected 
    if select_plot_type:
        # calendar plots
        if options["type"] == "cal":
            fig = plot_time_data(df, options["period"], start, end, options["cumulative"])
        # aggregation plots
        elif options["type"] == "agg":
            agg_period = options["agg_period"]
            fig = plot_time_agg(df, agg_period, start, end)
        st.pyplot(fig,width='stretch')

########################################################################
def agg_play_history(df_history, display_item, key):
    # plot options
    plot_options = aggregate_plot_options
    # plot option selection
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{key}_{display_item}_type_select")
                            
    options = plot_options[select_plot_type]

    # only plot if a selection has been made
    if display_item == "artist":
        grouping = ["artist"]
        filter_col = "artist"
        make_multi = None
    else:
        grouping = [display_item, "artist"]
        filter_col = display_item+"_artist"
        make_multi = grouping

    filtered = df_history
    plays = aggregate_listens(filtered, filter_col, options["agg_period"], make_multi)
    
    return plays, options["agg_period"]

def show_agg_play_history(df, display_item, agg_type, key):

    days =  ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))
    labels = {
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "weekday": days,
        "hour": hours,
        "day and hour": [x+" "+str(h)+"h" for x in days for h in hours]
    }


    df = df.sort_values(by=df.columns[0], ascending=False)
    df.columns = labels[agg_type]
    st.dataframe(df)

    #def agg_label(x):
    #    return (labels[agg_type][int(x) - 1] if agg_type == "month" else str(labels[agg_type][int(x)]))

    cols = df.columns
    select_time_bucket = st.selectbox(
        "Time range",
        cols,
        key = f"{key}_{display_item}_time_select",
    #    format_func= agg_label
    )

    top = df.nlargest(100, select_time_bucket, keep="all")
    to_show = top[select_time_bucket]
    st.write(to_show)

    

########################################################################

def show_power_laws(df_history, df_summary, selection, display_item):
    """
    allows selection and display of power law graphs
    """
    #st.write(selection)
    if display_item == "artist":
        grouping = ["artist"]
        filter_col = "artist"
        make_multi = None
    else:
        grouping = [display_item, "artist"]
        filter_col = display_item+"_artist"
        make_multi = grouping

    mask = df_history[filter_col].isin(selection)
    filtered = df_history[mask]
    rel, _ = relative_listens(filtered, filter_col, make_multi)
    # rel now has a multiindex
    
    df, failures = calculate_fit(rel, None, power_law, shift_to_max = True)

    if not failures.empty:
        with st.expander("Unable to fit the following:"):
            for item in failures.index:
                if isinstance(item, tuple):
                    item = '-'.join(item)
                st.write(item)

    if not df.empty:
        param_name = ["Coefficient", "Exponent"]
        exponents = df["param_1"]
        sliders = []
        if len(df)>1:
            for k in range(2):
                param = df[f"param_{k}"]    
                min_param = min(param)
                max_param = max(param)
                sliders.append( st.slider(param_name[k], min_param, max_param, (min_param, max_param), key=f"{display_item}_PL_slider_any_{k}") )
            filter_df = df[ (df["param_0"] >= sliders[0][0] ) & (df["param_0"] <= sliders[0][1]) &  (df["param_1"] >= sliders[1][0] ) & (df["param_1"] <= sliders[1][1]) ]
        else:
            filter_df = df
        sel = st.multiselect(
                    f"See details for {display_item} ({len(filter_df)} options)",
                    filter_df.index,
                    format_func = lambda x : format_item(x,df_summary[display_item]),
                    key = f"{display_item}_select_any_PL")

        fig_ad = plot_amplitudes_decays_selection(filter_df, sel)
        
        st.pyplot(fig_ad)
        plt.close(fig_ad)
        if sel:
            fig = plot_fit_multi(filter_df, sel, power_law)
            st.pyplot(fig)
            plt.close(fig)

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

########################################################################
def format_item(item, top_df):
    """
    handles formatting of tuples (track/album, artist) as opposed to just artist
    """
    if type(item) == tuple:
        lbl = ' - '.join(item)
    else:
        lbl = item
    return f"{lbl} ({top_df[item]} plays)"
