from input import *

history_file = "recenttracks-antiselfdual-1737987394.csv"

excludes = ["Chris Blair", "Super Simple Songs"]

listening_history = history_to_df(history_file, excludes)

end_uts = listening_history["uts"].max()
start_uts = listening_history["uts"].min()
diff_uts = end_uts - start_uts


# group uts plays as a list organised by track/artist -
song_plays = listening_history.groupby(["track", "artist"])["uts"].agg(list)
# convert back to a dataframe
song_plays_df = song_plays.reset_index()
# add total plays_colum n and sort
song_plays_df["total_plays"] = song_plays_df["uts"].apply(len)
song_plays_df = song_plays_df.sort_values("total_plays", ascending=False)

song_plays_df["plays_yearly_absolute"] = song_plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "absolute"))
song_plays_df["plays_yearly_relative"] = song_plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "relative"))

print(song_plays_df[["track", "artist", "plays_yearly_relative"]].head(100))
