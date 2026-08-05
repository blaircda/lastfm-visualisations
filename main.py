import matplotlib.pyplot as plt

from load_data import *
from organise_data import *

history_file = "recenttracks-antiselfdual-1737987394.csv"

excludes = ["Chris Blair", "Super Simple Songs"]

listening_history = history_to_df(history_file, excludes)

# group uts plays as a list organised by track/artist
song_plays_df = grouped_by_plays(listening_history, ["track","artist"])
album_plays_df = grouped_by_plays(listening_history, ["album","artist"])
artist_plays_df = grouped_by_plays(listening_history, ["artist"])

#print(song_plays_df.head(10))
#print(album_plays_df.head(10))
#print(artist_plays_df.head(10))

def plot_plays_top( play_df, Ntop = 10 ):
    top_df = play_df.head(Ntop).copy()
    for x in top_df.itertuples():
        print(x)
        fig = plot_play_history(x)
        st.pyplot(fig)
        plt.close(fig)
        
def plot_play_history(x):
    fig, ax = plt.subplots()    
    ax.plot(x)
    return fig




    
