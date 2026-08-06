import pandas as pd

def grouped_by_plays(history_df, grouping):
    """
    returns dataframes grouped by grouping = track-artist, artist, album-artist, etc
    """
    plays = history_df.groupby(grouping)["uts"].agg(list)
    
    # convert back to a dataframe
    plays_df = plays.to_frame()

    #calendar years
    plays_by_cal_year = history_df.groupby("year")[grouping].value_counts()    
    #plays_df["plays_yearly_cal"] = plays_by_cal_year.unstack("year", fill_value=0).values.tolist()

    plays_df["plays_yearly_cal"] = plays_by_cal_year.unstack("year", fill_value=0).reindex(plays_df.index).values.tolist()

    #plays_df["plays_yearly_cal"] = plays_df["uts"].apply(lambda x: playtime(x, start_uts, end_uts, timespan = "calendar") 

    # yearly plays
    start_uts = history_df["uts"].min()
    end_uts = history_df["uts"].max()
    # plays by year counting from start of data 
    plays_df["plays_yearly_absolute"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "absolute"))
    # plays by year counting from first listen of particular artist/track/album
    plays_df["plays_yearly_relative"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "relative"))

    # add total plays_column and sort    
    plays_df["total_plays"] = plays_df["uts"].apply(len)
    plays_df = plays_df.sort_values("total_plays", ascending=False)

    # reset index
    plays_df = plays_df.reset_index()

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

    
