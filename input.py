import pandas as pd

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
    
    return df

def playtime (list_of_plays, numberYears, start_uts, end_uts, timespan):
# returns a list of plays per year for a given item
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
