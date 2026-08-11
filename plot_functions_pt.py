import matplotlib.pyplot as plt
import numpy as np
from organise_data import power_law


def plot_time_data(df, freq, start, end, cumulative = False):
    label = {
        "YS": "year",
        "ME": "month",
        "W": "week",
        "D": "day"
    }
    
    fig, ax = plt.subplots(figsize=(15, 10))

    df = df.loc[start:end]

    plays = df.resample(freq).size()

    if cumulative:
        y_vals = plays.cumsum()
    else:
        y_vals = plays
        
    ax.plot(plays.index,y_vals, marker="o")
    ax.set_ylabel("Plays")
    ax.set_title(f"Plays per {label.get(freq, "time")}")
    
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    return fig

def plot_time_agg(df, agg, start, end,):
    
    df = df.loc[start:end]

    times = {
        "month": df.index.month,
        "weekday": df.index.weekday,
        "hour": df.index.hour,
        "day and hour": df.index.weekday * 24 + df.index.hour
    }

    domains = {
        "month": range(1, 13),
        "weekday": range(7),
        "hour": range(24),
        "day and hour": range(168),
    }

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours_div = [0,6,12,18]

    labels = {
        "month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "weekday": days,
        "hour": list(range(24)),
    }

    plays = df.groupby(times[agg]).size()
    # count zero values
    plays = plays.reindex(domains[agg], fill_value=0)    
    
    fig, ax = plt.subplots(figsize=(15, 10)) 
    ax.plot(plays.index, plays.values, marker="o")

    if agg == "day and hour":
        ticks = range(0, 168, 6)
        tick_labels = [f"{d} {h}h" for d in days for h in hours_div]
        ax.tick_params(axis="x", labelrotation=90)
    else:
        ticks = plays.index
        tick_labels = labels[agg]
        
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.set_ylabel("Plays")
    ax.set_title(f"Plays divided into {agg}")
    return fig
