import pandas as pd
import streamlit as st
import datetime as datetime
from plot_functions import *
from organise_data import relative_listens, calculate_fit, summarise_playcount

def filter_play_history_old(df_summary, display_item, key):
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

def filter_play_history(df_summary, display_item, key):
    """
    controls the selection of items of type display_item (artist, track-artist, album-artist)
    reading total playcount and ranking from df_summary
    key is a str to ensure the streamlit inputs are uniquely identified
    """
    df = df_summary[display_item].to_frame()
    df["ranking"] = df["total_plays"].rank(method="min", ascending=False).astype(int)
        
    ranking_key = f"{display_item}_ranking_slider_{key}"
    total_play_key =  f"{display_item}_total_play_slider_{key}"

    poss_plays = list( df["total_plays"].unique() )
    poss_ranks = list( df["ranking"].unique() )
     
    def update_play_slider():
        min_rk, max_rk = st.session_state[ranking_key]
        mask = (df["ranking"] >= min_rk) & ( df["ranking"] <= max_rk)
        filter_df = df[mask]["total_plays"]
        min_val = min(filter_df)
        max_val = max(filter_df)
        st.session_state[total_play_key] = (max_val, min_val)

    def update_ranking_slider():
        max_play, min_play = st.session_state[total_play_key]
        mask = (df["total_plays"] >= min_play) & ( df["total_plays"] <= max_play)
        filter_df = df[mask]["ranking"]
        min_val = min(filter_df)
        max_val = max(filter_df)
        st.session_state[ranking_key] = (min_val, max_val)
    
    ranking = st.select_slider(
        "Ranking", options  = poss_ranks,
        value = (poss_ranks[0], poss_ranks[47]),
        key = ranking_key,
        on_change = update_play_slider
    )

    total = st.select_slider(
        "Total playcount",
        options = poss_plays,
        value = (poss_plays[0], poss_plays[50]),
        key = total_play_key,
        on_change = update_ranking_slider
    )   

    sel = df[ (df["total_plays"] <= total[0] ) & (df["total_plays"] >= total[1]) & (df["ranking"] >= ranking[0]) &  (df["ranking"] <= ranking[1]) ]
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
    "Years aggregated": {
     "type": "agg",
     "agg_period": "year",   
     "cumulative": False
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

    min_year = min(df.index.year)
    max_year = max(df.index.year)
    
    # supported aggregrations
    times = {
        "year": df.index.year,
        "month": df.index.month,
        "weekday": df.index.weekday,
        "hour": df.index.hour,
        "day and hour": df.index.weekday * 24 + df.index.hour
    }

    # how many "buckets" in each aggregations
    # used below to ensure that we have values in all buckets
    # for all items
    domains = {
        "year": range(min_year, max_year+1),
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

    start, end = get_time_range(df, life_divisions, key="all")
        
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


def get_time_range(df, life_divisions, key=None):
    """
    creates a slider based on the time range of the listening history in df
    with customisable data ranges for selection in life_divisions
    """
    min_date = df.index.min().strftime("%Y-%m-%d")
    max_date = df.index.max().strftime("%Y-%m-%d")
    all_range = (min_date, max_date)

    life_div_key = f"{key}_life_div"
    slider_key = f"{key}_time_range_slider"
    # if no life divisions are specified we will make a slider based on the full range
    if life_divisions is None:
        dates = all_range
    # otherwise we make a selectbox to easily apply custom ranges to the full range slider
    else:
        life_divisions = {
        k: (
            min_date if v[0] is None else v[0],
            max_date if v[1] is None else v[1]
        )
        for k,v in life_divisions.items() 
        }
        
        range_options = {"All": all_range} | life_divisions

        def date_prepare(dates):
            return ( datetime.datetime.strptime(dates[0], '%Y-%m-%d'), datetime.datetime.strptime(dates[1], '%Y-%m-%d'))
            
        def update_slider():
            st.session_state[slider_key] = date_prepare( range_options[st.session_state[life_div_key]] )

        sel_range =st.selectbox(
            "Life divisions",
            range_options.keys(),
            format_func = lambda x : f"{x}  ({range_options[x][0]} to  {range_options[x][1]})",
            key = life_div_key,
            on_change=update_slider
        )

        dates = range_options[sel_range]

    sel_range_val = date_prepare(dates)

    # slider to choose the date range to plot
    start, end = st.slider("Date range",
        min_value = df.index.min().to_pydatetime(),
        max_value = df.index.max().to_pydatetime(),
        value = sel_range_val,
        key= slider_key
        )
    return start, end 
########################################################################

def show_summary_rankings( df, display_item, life_divisions):

    st.subheader("Complete play counts by date range")
    
    df = df.copy()
    df = df.set_index("local_datetime").sort_index()
    
    start, end = get_time_range(df, life_divisions, key = "summary_"+display_item)
    filter_df = df.loc[start:end]

    if display_item == "artist":
        grouping = ["artist"]
    else:
        grouping = [display_item, "artist"]
        
    df = summarise_playcount(filter_df, grouping).to_frame()
    df = df.rename(columns={"total_plays":"Total plays"})
    df["Ranking"] = df["Total plays"].rank(method="min", ascending=False)
    df = df.reset_index()
    df = df.set_index("Ranking")
    st.dataframe(df)

    return start, end

def get_filter_grouping(display_item):
    """
    helper function for selecting artist vs track-artist, album-artist
    """
    if display_item == "artist":
        grouping = ["artist"]
        filter_col = "artist"
        make_multi = None
    else:
        grouping = [display_item, "artist"]
        filter_col = display_item+"_artist"
        make_multi = grouping

    return grouping, filter_col, make_multi

    
def truncate(df_history, summary, display_item, min_plays = 5):
    """
    truncates df_history to items with a minimum play count 
    """
    s = summary[display_item]
    selection = s[ s>= min_plays]
    _, filter_col, _ = get_filter_grouping(display_item)
    mask = df_history[filter_col].isin(selection.index)
    filtered = df_history[mask]
    return filtered

    
def agg_play_history(df_history, start, end, display_item, key):
    """
    allows selection of aggregation of df_history by different time buckets
    """
    st.subheader("Detailed aggregated play counts for chosen date range")
    st.write("Only including items with at least 5 play counts total")

    # reuse plot options although we only show tabular data here
    plot_options = aggregate_plot_options
    # plot option selection
    select_plot_type = st.selectbox(
                            "Choose time aggregation for which to generate rankings:",
                            plot_options.keys(),
                            key = f"{key}_{display_item}_type_select"
                        )
                            
    options = plot_options[select_plot_type]

    grouping, filter_col, make_multi = get_filter_grouping(display_item)

    # passing the whole history for now
    # imposing a cutoff would speed up
    # else generate all these aggregations at first load?
    
    df = df_history.set_index("local_datetime").sort_index()
    filtered = df.loc[start: end].reset_index()
    plays = aggregate_listens(filtered, filter_col, options["agg_period"], make_multi)
    
    return plays, options["agg_period"]

def show_agg_play_history(df, display_item, agg_type, key):
    """
    given a previous choice of agg_type and aggregated listening history in df
    outputs tabular data of df
    """
    
    days =  ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))
    labels = {
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "weekday": days,
        "hour": hours,
        "day and hour": [x+" "+str(h)+"h" for x in days for h in hours]
    }


    df = df.sort_values(by=df.columns[0], ascending=False)
    df.columns = labels.get(agg_type, df.columns)
    
    st.dataframe(df)

    #def agg_label(x):
    #    return (labels[agg_type][int(x) - 1] if agg_type == "month" else str(labels[agg_type][int(x)]))

    cols = df.columns
    select_time_bucket = st.selectbox(
        "See ranking for a specific time aggregation",
        cols,
        key = f"{key}_{display_item}_time_select",
    #    format_func= agg_label
    )

    max_rank = st.number_input(label = "Show top how many?", min_value = 10, max_value = len(df), 
        key = f"{key}_{display_item}_N_select",
    )

    top = df.nlargest(max_rank, select_time_bucket, keep="all")
    top["Ranking"] = df[select_time_bucket].rank(method="min", ascending=False)
    to_show = top[["Ranking", select_time_bucket]]
    to_show = to_show.rename(columns={select_time_bucket:"Total plays"})
    to_show = to_show.reset_index().set_index("Ranking")
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
