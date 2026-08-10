import pandas as pd
import numpy as np
import streamlit as st
import datetime
from scipy.optimize import curve_fit

def strip_zeros(x):
    while x[0] == 0:
        x = x[1:]
    return x

def all_plays(history_df):
    stats = {}
    
    plays = history_df["uts"]
    start_uts = min(plays)
    end_uts = max(plays)

    stats["plays_yearly_absolute"] =  playtime(plays, 0, start_uts, end_uts, timespan = "absolute")
    
    #calendar years
    stats["plays_yearly_cal"] = history_df.groupby("year").size().values.tolist()

    #calendar months
    stats["plays_monthly_cal"] = history_df.groupby(["year","month"]).size().values.tolist()

    # months aggregated 
    stats["plays_months"] =  history_df.groupby("month").size().values.tolist()
    # days aggregated
    stats["plays_days"] =  history_df.groupby("weekday").size().values.tolist()
    # days aggregated yearly
    stats["plays_days_yearly"] =  history_df.groupby(["year","weekday"]).size().values.tolist()
    
    return pd.DataFrame([stats])
    
def grouped_by_plays(history_df, grouping):
    """
    returns dataframes grouped by grouping = track-artist, artist, album-artist, etc
    """
    plays = history_df.groupby(grouping)["uts"].agg(list)
    
    # convert back to a dataframe
    plays_df = plays.to_frame()
    
    # yearly plays
    start_uts = history_df["uts"].min()
    end_uts = history_df["uts"].max()
    # plays by year counting from start of data 
    plays_df["plays_yearly_absolute"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "absolute"))
    # plays by year counting from first listen of particular artist/track/album
    plays_df["plays_yearly_relative"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "relative"))

    #calendar years
    plays_by_cal_year = history_df.groupby("year")[grouping].value_counts()    
    plays_df["plays_yearly_cal"] = plays_by_cal_year.unstack("year", fill_value=0).reindex(plays_df.index).values.tolist()
    #calendar months
    plays_by_cal_month = history_df.groupby(["year","month"])[grouping].value_counts()    
    plays_df["plays_monthly_cal"] = plays_by_cal_month.unstack(["year","month"], fill_value=0).reindex(plays_df.index).values.tolist()
    # relative calendar_months
    plays_df["plays_monthly_relative"] = plays_df["plays_monthly_cal"].apply(strip_zeros)

    # months aggregated 
    plays_by_month = history_df.groupby("month")[grouping].value_counts()    
    plays_df["plays_months"] = plays_by_month.unstack("month", fill_value=0).reindex(plays_df.index).values.tolist()
    # days aggregated
    plays_by_day = history_df.groupby("weekday")[grouping].value_counts()    
    plays_df["plays_days"] = plays_by_day.unstack("weekday", fill_value=0).reindex(plays_df.index).values.tolist()

    # add total plays_column and sort    
    plays_df["total_plays"] = plays_df["uts"].apply(len)
    plays_df = plays_df.sort_values("total_plays", ascending=False)

    return plays_df

def playtime (list_of_plays, numberYears, start_uts, end_uts, timespan):
    """
    returns a list of plays per year for a given item
    """
    Y = 60*60*24*365
    Npresent = (end_uts-start_uts)/Y   

    earliest = min(list_of_plays)
    latest = max(list_of_plays)

    # how many years of listens are there
    N = (latest - earliest)/Y
    # how many years since first listen
    Nsince = (end_uts-earliest)/Y
    
    # if want all listening information from start of records
    if timespan == 'absolute':
        Nwhich, start = Npresent, start_uts
    # if just want listening information from first listen of item
    elif timespan == 'relative':
        Nwhich, start = Nsince, earliest
           
    ppy = []

    # only take items which have been listened to for more than numberYears
    #if N>numberYears:
    # only take items whose first listen is sufficiently long ago
    if Nsince>numberYears:
        # range is int part of Nwhich to exclude incomplete year at the end
        for n in range(int(Nwhich)):
            ppy.append( sum(1 for x in list_of_plays if start + n*Y <= x < start + (n+1)*Y ))
            
    return ppy

def novelty_in_time( time_grouping, item_grouping, history_df):
    """
    accumulate a record of novel vs old listens of item_grouping
    per time interval time_grouping
    """
    stats = []
    already_listened = set()

    dfy = history_df.groupby(time_grouping)[item_grouping]
    
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

def power_law(x,a,b):
  return a*x**(b)

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

    shift = 0 
    if shift_to_max:
        while y_data[0] <  max(y_data):
            shift += 1
            y_data =  y_data[1:]
    #if shift:
    #    print("shifted to:")
    #    print(y_data, "\n")
        
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
        return None

def calculate_fit(df, Ntop, fit_function, shift_to_max = False):
    """
    takes the first Ntop entries of dataframe df
    and fits the function fit_function to the the relatively yearly plays of each entry
    where fitting is not possible, the entries are dropped and an error message is logged to the terminal
    returns the new dataframe with fit information
    optionally, apply shift to fit only starting with max value of relatively yearly plays
    """
    top_df = df.head(Ntop).drop(columns=["uts", "plays_yearly_absolute", "plays_yearly_cal"])
    
    result = top_df["plays_yearly_relative"].apply(lambda x: get_fit(x, fit_function, shift_to_max))
    names = [f"param_{i}" for i in range(len(result.iloc[0])-1)] + ["shift"]
    top_df[names] = pd.DataFrame(result.tolist(), index=top_df.index)

    # drop cases where fitting is not possible
    # alternatively: keep them as null and don't drop them in st power laws tab selectbox
    # this would allow the same df to be used for both play histories and power laws
    print("\nUnable to make a fit for the following:")
    print( top_df[ top_df.isna().any(axis=1) ])
    print("\n")    
    top_df.dropna(inplace=True)
    return top_df

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
    df['year'] = df['uts'].apply(lambda x: datetime.datetime.fromtimestamp(x).year)
    df['month'] = df['uts'].apply(lambda x: datetime.datetime.fromtimestamp(x).month)
    df['day'] = df['uts'].apply(lambda x: datetime.datetime.fromtimestamp(x).day)
    df['weekday'] = df['uts'].apply(lambda x: datetime.datetime.fromtimestamp(x).isoweekday())
    return df

@st.cache_data
def analyse_history_csv(history_file, excludes):
    """
    takes csv file and processes it into various dataframes structured to contain interesting information
    """

    print("\nAnalysing CSV file...............\n")
    
    listening_history = history_to_df(history_file, excludes)

    data = {}

    data["total_plays"] = len(listening_history)

    start_uts = min(listening_history["uts"])
    end_uts = max(listening_history["uts"])

    start = datetime.datetime.fromtimestamp(start_uts)
    end = datetime.datetime.fromtimestamp(end_uts)

    data["start"] = start
    data["end"] = end 
    #data["start_date"] = start.strftime("%Y-%m-%d")
    #data["end_date"] = end.strftime("%Y-%m-%d")

    num_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

    yi, yf = min(listening_history['year']), max(listening_history['year'])
    data["calendar_axis"] = [str(x)[2:] for x in range(yi, yf+1)]
    data["monthly_axis"] = [x for x in range(num_months)]

    # group uts plays as a list organised by track/artist
    data["track_plays"] = grouped_by_plays(listening_history, ["track","artist"])
    data["album_plays"] = grouped_by_plays(listening_history, ["album","artist"])
    data["artist_plays"] = grouped_by_plays(listening_history, ["artist"])
    group_all = lambda _: 0
    data["everything"] = all_plays(listening_history)

    data["track_novelty"] = novelty_in_time( "year", ["track", "artist"], listening_history)
    data["album_novelty"] = novelty_in_time( "year", ["album", "artist"], listening_history)
    data["artist_novelty"] = novelty_in_time( "year", "artist", listening_history)

    data["track_pl"] = calculate_fit(data["track_plays"], 250, power_law, shift_to_max = True)
    data["album_pl"] = calculate_fit(data["album_plays"] , 250, power_law)
    data["artist_pl"] = calculate_fit(data["artist_plays"], 250, power_law)

    print("\nDone")
    return data
