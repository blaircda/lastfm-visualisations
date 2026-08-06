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

def plot_play_histories(df, items, options):
    col = options["column"]
    #fig, ax = plt.subplots(figsize=(30, 20))
    fig, ax = plt.subplots()

    for item in items:
        plays = df.loc[item, col]
        if options["x"] == None:
            x =range(len(plays))
        else:
            x = options["x"]
        if options["cumulative"] == True:
            plays = [ sum(plays[:i+1]) for i in range(len(plays)) ] 
            ax.set_ylabel("Plays (cumulative)")
        else:
            ax.set_ylabel("Plays")
        ax.plot(x, plays, label=item)
    ax.set_xlabel("Years")
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.05, 1)
    )
    return fig

def plot_power_laws(df, items):
    col = "plays_yearly_relative"
    #fig, ax = plt.subplots(figsize=(30, 20))
    fig, ax = plt.subplots()

    for item in items:
        plays = df.loc[item, col]
        ax.plot(range(len(plays)), plays, label=item)
    ax.set_ylabel("Plays")
    ax.set_xlabel("Years")
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.05, 1)
    )
    return fig

def plot_novelty_in_time( df, title, col_old, col_new, type_label, is_ratio):
    fig, ax = plt.subplots()

    x = df["time"][1:]
    y_old = df[col_old][1:]
    y_new = df[col_new][1:]

    #ax.set_title(title)
    ax.set_xticks(x)
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_xlabel("Years")
    ax.set_ylabel(type_label)
    ax.bar(x,y_old, label=f"Known")
    ax.bar(x,y_new,bottom=y_old,label=f"Novel")

    ax.legend()
    return fig

def plot_novelties_in_time( df ):
    cols = ["items", "plays"]
    figs = []
    
    for c in cols:
        if c == "items":
            type_label = "distinct"
        else:
            type_label = "total plays"
        figs.append( plot_novelty_in_time(df, type_label, "old_"+c, "new_"+c, type_label, is_ratio=False) )
        figs.append( plot_novelty_in_time(df, type_label, "old_"+c+"_ratio", "new_"+c+"_ratio", type_label="fraction "+type_label, is_ratio=True) )
        
    return figs
