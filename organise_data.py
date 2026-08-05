import pandas as pd

def grouped_by_plays(history_df, grouping):
    plays = history_df.groupby(grouping)["uts"].agg(list)
    # convert back to a dataframe
    plays_df = plays.reset_index()
    # add total plays_column and sort
    plays_df["total_plays"] = plays_df["uts"].apply(len)
    plays_df = plays_df.sort_values("total_plays", ascending=False)

    end_uts = history_df["uts"].max()
    start_uts = history_df["uts"].min()
    plays_df["plays_yearly_absolute"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "absolute"))
    plays_df["plays_yearly_relative"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "relative"))

    return plays_df

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
