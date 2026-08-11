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

    return listening_history, summary_data
    
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
    data["everything"] = all_plays(listening_history)

    data["track_novelty"] = novelty_in_time( "year", ["track", "artist"], listening_history)
    data["album_novelty"] = novelty_in_time( "year", ["album", "artist"], listening_history)
    data["artist_novelty"] = novelty_in_time( "year", "artist", listening_history)

    data["track_pl"] = calculate_fit(data["track_plays"], 250, power_law, shift_to_max = True)
    data["album_pl"] = calculate_fit(data["album_plays"] , 250, power_law)
    data["artist_pl"] = calculate_fit(data["artist_plays"], 250, power_law)

    print("\nDone")
    return data


def summarise_playcount(df, grouping):
    """
    returns playcount summary grouped by grouping = track-artist, artist, album-artist, etc
    """
    return df.groupby(grouping).size().rename("total_plays").sort_values(ascending=False)
