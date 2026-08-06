import pandas as pd
import datetime

def history_to_df(history_file, excludes):
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

    return df
