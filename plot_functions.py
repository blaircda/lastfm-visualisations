import matplotlib.pyplot as plt

def plot_plays_top( play_df, Ntop = 10 ):
    top_df = play_df.head(Ntop).copy()
    for x in top_df.itertuples():
        print(x)
        fig = plot_play_history(x)
        st.pyplot(fig)
        plt.close(fig)
        
def plot_play_history(x, y):
    fig, ax = plt.subplots()

    ax.plot(x, y)
    ax.set_ylabel("Plays")
    ax.set_xlabel("Years")
        
    return fig
