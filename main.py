import matplotlib.pyplot as plt

from load_data import *
from organise_data import *
from power_laws import *

history_file = "recenttracks-antiselfdual-1737987394.csv"

excludes = ["Chris Blair", "Super Simple Songs"]

listening_history = history_to_df(history_file, excludes)

yi, yf = min(listening_history['year']), max(listening_history['year'])
calendar_axis = [str(x)[2:] for x in range(yi, yf+1)]

# group uts plays as a list organised by track/artist
song_plays_df = grouped_by_plays(listening_history, ["track","artist"])
album_plays_df = grouped_by_plays(listening_history, ["album","artist"])
artist_plays_df = grouped_by_plays(listening_history, ["artist"])

song_yearly_novelty_df = novelty_in_time( "year", ["track", "artist"], listening_history)
album_yearly_novelty_df = novelty_in_time( "year", ["album", "artist"], listening_history)
artist_yearly_novelty_df = novelty_in_time( "year", "artist", listening_history)

song_power_laws_df = calculate_power_laws(song_plays_df, 100, power_law)
album_power_laws_df = calculate_power_laws(album_plays_df, 100, power_law)
artist_power_laws_df = calculate_power_laws(artist_plays_df, 100, power_law)

#print(song_plays_df.head(10))
#print(album_plays_df.head(10))
#print(artist_plays_df.head(10))






    
