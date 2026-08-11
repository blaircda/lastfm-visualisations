import matplotlib.pyplot as plt
import numpy as np
#from adjustText import adjust_text
from organise_data import power_law
import pandas as pd

def plot_play_histories(df, options):
    """
    for each item in items, extracts and plots data about item from df
    dict options specifies which data and what type of graph
    """
    if isinstance(df, pd.Series):
        df = df.to_frame().T

    fig, ax = plt.subplots(figsize=(15, 10))
    #fig, ax = plt.subplots()
    if options["cumulative"]:
        data = df.cumsum(axis=1) 
        ax.set_ylabel("Plays (cumulative)")
    else:
        data = df
        ax.set_ylabel("Plays")

    if isinstance(df.index, pd.MultiIndex):
        data.index = [f"{item} – {artist}" for item, artist in df.index]
    elif type(df.index[0]) == tuple:
        data.index = [f"{item} – {artist}" for item, artist in df.index]


    if "agg_period" in options.keys():
        agg = options["agg_period"]
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours_div = [0,6,12,18]

        labels = {
            "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            "weekday": days,
            "hour": list(range(24)),
        }
        
        if agg == "day and hour":
            ticks = range(0, 168, 6)
            tick_labels = [f"{d} {h}h" for d in days for h in hours_div]
            ax.tick_params(axis="x", labelrotation=90)
        else:
            ticks = data.columns
            tick_labels = labels[agg]
        ax.set_xticks(ticks)
        ax.set_xticklabels(tick_labels)


    #data.T.plot(ax=ax, marker="o")
    ax.plot(data.columns, data.T, marker="o")
    ax.legend(
        data.index,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncols=4
    )
    ax.margins(x=0.05)
    #ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncols=4)

    return fig
    
    for item in items:
        x = df.columns
        
        if options["cumulative"] == True:
            y = df.loc[item].cumsum()
            ax.set_ylabel("Plays (cumulative)")
        else:
            y = df.loc[item]
            ax.set_ylabel("Plays")

        if type(item) == tuple:
            lbl = ' - '.join(item)
        else:
            lbl = item

        ax.plot(x,y,marker="o",label=lbl)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncols=4)
        
    return fig
