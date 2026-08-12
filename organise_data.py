import pandas as pd
import numpy as np
import streamlit as st
import datetime
from scipy.optimize import curve_fit

def power_law(x,a,b):
  return a*x**(b)

@st.cache_data
def history_to_df(history_file, excludes):
    """
    read csv file and perform some basic data cleanup
    """
    df = pd.read_csv(history_file,usecols=["track","artist","album","uts"])
    df.drop_duplicates(inplace=True)
    df = df[ ~df.artist.isin(excludes) ]
    
    # remove remaster tags wrapped in brackets
    # e.g. " (2009 Remaster)" or " [2011 Remastered Version]"
    # [^(]* (instead of greedy .*) stops at the first ')'
    # so e.g. "Song (feat. Artist) (2011 Remaster)" only loses the remaster part
    df[["track","album"]] = df[["track","album"]].replace(r' \(.*[Rr]emaster[^(]*\)| \[.*[Rr]emaster.*\]','',regex=True)

    # remove remaster tags written as a dash-separated suffix
    # e.g. " - 2015 Remaster" or " - Remastered"
    # anchored to end of string ($)
    df[["track","album"]] = df[["track","album"]].replace(r' -.*[Rr]emaster.*$','',regex=True)

    # add calendar data
    df["datetime_utc"] = pd.to_datetime(df["uts"], unit="s", utc=True)
    #df["year"] = df["datetime_utc"].dt.year
    #df["month"] = df["datetime_utc"].dt.month
    #df["day"] = df["datetime_utc"].dt.day
    #df["weekday"] = df["datetime_utc"].dt.weekday
    #df["hour"] = df["datetime_utc"].dt.hour

    df["track_artist"] = list(zip(df["track"], df["artist"]))
    df["album_artist"] = list(zip(df["album"], df["artist"]))
    
    df = df.set_index('datetime_utc')
    df = df.sort_index()
    return df

@st.cache_data
def analyse_history_csv(history_file, excludes):
    """
    takes csv file and processes it into various dataframes structured to contain interesting information
    """

    print("\nAnalysing CSV file...............\n")
    
    listening_history = history_to_df(history_file, excludes)

    summary_data = {}
    summary_data["artist"] = summarise_playcount(listening_history, "artist")
    summary_data["album"] = summarise_playcount(listening_history, ["album","artist"])
    summary_data["track"] = summarise_playcount(listening_history, ["track","artist"])

    novelty_data = {}
    novelty_data["track"] = novelty_in_time( "year", ["track", "artist"], listening_history)
    novelty_data["album"]= novelty_in_time( "year", ["album", "artist"], listening_history)
    novelty_data["artist"] = novelty_in_time( "year", "artist", listening_history)

    return listening_history, summary_data, novelty_data

    relative_plays, first_times = {}, {}
    # this is overkill as I don't intend to use any except a few of these
    #relative_plays["track"], first_times["track"] = relative_listens(listening_history, "track_artist")
    #relative_plays["album"], first_times["album"] = relative_listens(listening_history, "album_artist")
    #relative_plays["artist"], first_times["artist"] = relative_listens(listening_history, "artist")
    
    #relative_plays["track"] = relative_plays["track"].reindex(summary_data["track"].index)
    #relative_plays["album"] = relative_plays["album"].reindex(summary_data["album"].index)
    #relative_plays["artist"] = relative_plays["artist"].reindex(summary_data["artist"].index)

    #fits = {}
    #fits["track"] = calculate_fit(relative_plays["track"], 250, power_law, shift_to_max = True)
    #fits["album"] = calculate_fit(relative_plays["album"] , 250, power_law)
    #fits["artist"] = calculate_fit(relative_plays["artist"], 250, power_law)
    
    #return listening_history, summary_data, novelty_data, relative_plays, first_times, fits
    

@st.cache_data
def summarise_playcount(df, grouping):
    """
    returns playcount summary grouped by grouping = track-artist, artist, album-artist, etc
    """
    return df.groupby(grouping).size().rename("total_plays").sort_values(ascending=False)

def relative_listens_col(df, col):
    """
    pass a dataframe and return the yearly plays
    """
    # copy the filtered dataframe
    plays = df.copy()
    # extract the first listen for each item in col
    first_listen = df.groupby(col).apply(lambda x: x.index.min())
    # write first listen as a new column
    plays["first_listen"] = plays[col].map(first_listen)

    all_first_listens = plays["first_listen"].unique()
    
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
    return plays, all_first_listens

def relative_listens(df, grouping_col, make_multi=None):
    """
    pass a dataframe and return the yearly plays
    """
    # copy the filtered dataframe
    plays = df.copy()
    # extract the first listen for each item in grouping_col
    first_listen = df.groupby(grouping_col).apply(lambda x: x.index.min())
    # write first listen as a new column
    plays["first_listen"] = plays[grouping_col].map(first_listen)

    all_first_listens = plays["first_listen"].unique()
    
    # compute years elapsed since first listen and write as a new column
    plays["years_since_first_listen"] = (plays.index - plays["first_listen"]).dt.days // 365
    # aggregate the number of plays in each year since first listen
    plays = plays.groupby([grouping_col,"years_since_first_listen"]).size()
    # reindex within each item to fill in missing zeros within the range we have listening data for
    # NOT adding extra zeros at the end
    # finally unstack to get a dataframe where the index is the item and the columns are the years since first listen
    plays = plays.groupby(level=0).apply(
            lambda x: x.droplevel(0).reindex(range(x.index.get_level_values(1).max()+1), fill_value=0)
    ).unstack("years_since_first_listen")
    
    if make_multi:
        plays.index = pd.MultiIndex.from_tuples(plays.index, names=make_multi)
    
    return plays, all_first_listens

def get_fit(y_data, fit_function, shift_to_max = False):
    """
    fits the function fit_function to the data y_data
    viewed as a function of timesteps [1,2,3,...]
    optionally, start the fit from the max value of y_data
    returns the fit parameters and the shift if possible
    otherwise returns None
    """   
    if len(y_data) == 0:
        return None
    print(y_data)
    shift = 0 
    if shift_to_max:
        while y_data[0] <  max(y_data):
            shift += 1
            y_data =  y_data[1:]
    if shift:
        print("shifted to:")
        print(y_data, "\n")
        
    if len(y_data)>1:
        try:
            x_data = [float(y) for y in range(1,len(y_data)+1)]
            popt, pcov = curve_fit(fit_function, x_data, y_data, p0=[max(y_data),2])
            perr = np.sqrt(np.diag(pcov))
            return (*popt, shift)
        except (RuntimeError, TypeError, ValueError):
            print ("Error:", y_data)
            return None
    else:
        print ("Error:", y_data)
        return None

def calculate_fit(df, Ntop, fit_function, shift_to_max = False):
    """
    takes the first Ntop entries of dataframe df
    and fits the function fit_function to the the relatively yearly plays of each entry
    where fitting is not possible, the entries are dropped and an error message is logged to the terminal
    returns the new dataframe with fit information
    optionally, apply shift to fit only starting with max value of relatively yearly plays
    """
    if Ntop:
        top_df = df.head(Ntop)
    else:
        top_df = df
    result = top_df.apply(lambda row: get_fit(row.dropna().tolist(), fit_function, shift_to_max), axis=1)

    valid = result.notna()

    failures = top_df[~valid]
    top_df = top_df[valid]
    result = result[valid]

    if not top_df.empty:
        names = [f"param_{i}" for i in range(len(result.iloc[0])-1)] + ["shift"]
        top_df[names] = pd.DataFrame(result.tolist(), index=top_df.index)
        if not failures.empty:
            print("\nUnable to make a fit for the following:")
            print(failures)
    else:
        print("\nUnable to make any fits!")
        print(failures)

    return top_df, failures

    # drop cases where fitting is not possible
    if len( top_df[ top_df["shift"].isna() ] ) > 0:
        print("\nUnable to make a fit for the following:")
        print( top_df[ top_df["shift"].isna()].index )
        print( top_df[ top_df["shift"].isna() ])
        print("\n")    
        top_df = top_df[ ~top_df["shift"].isna() ]
    return top_df

def novelty_in_time( time_grouping, item_grouping, history_df):
    """
    accumulate a record of novel vs old listens of item_grouping
    per time interval time_grouping
    """
    stats = []
    already_listened = set()

    groupings = {
    "year": history_df.index.year,
    "month": [history_df.index.year, history_df.index.month]
    }
    
    dfy = history_df.groupby(groupings[time_grouping])[item_grouping]
    
    for time, time_data in dfy:
        new_items, old_items = 0,0
        new_plays, old_plays = 0,0
        time_counts = time_data.value_counts()
        for item, count in time_counts.items():
            if item not in already_listened:
                already_listened.add(item)
                new_plays +=  count
                new_items += 1
            else:
                old_plays += count
                old_items += 1
        stats.append( 
        {
        "time": time, "new_items": new_items, "old_items": old_items,
            "new_plays": new_plays, "old_plays": old_plays
        }
        )
    
    stats_df = pd.DataFrame(stats)
    
    stats_df["new_items_ratio"] = stats_df["new_items"]/(stats_df["new_items"]+stats_df["old_items"])
    stats_df["old_items_ratio"] = stats_df["old_items"]/(stats_df["new_items"]+stats_df["old_items"])
    
    stats_df["new_plays_ratio"] = stats_df["new_plays"]/(stats_df["new_plays"]+stats_df["old_plays"])
    stats_df["old_plays_ratio"] = stats_df["old_plays"]/(stats_df["new_plays"]+stats_df["old_plays"])
    
    return stats_df
