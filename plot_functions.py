import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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

    ax.plot(data.columns, data.T, marker="o")

    if options["type"] == "cal":
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    
    ax.legend(
        data.index,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncols=4
    )
    ax.margins(x=0.05)
 

    return fig
    
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
        ax.set_ylabel("Plays (cumulative)")
    else:
        y_vals = plays
        ax.set_ylabel("Plays")

        
    ax.plot(plays.index,y_vals, marker="o")
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

########################################################################
# Power law fits
########################################################################

def plot_fit_multi(df, items, fit_function):
    """
    for each item in items, extracts the plays_yearly_relative data from df
    and plots both this and the graph of fit_function fitted to that data
    """
    fig, ax = plt.subplots(layout="constrained")

    ax.set_xlabel("Years")
    ax.set_ylabel("Listens")
    
    year_cols = [c for c in df.columns if isinstance(c,int)]
    param_cols = [c for c in df.columns if isinstance(c, str) and c.startswith("param_")]

    for item in items:
        if isinstance(item, tuple):
            lbl = ' - '.join(item)
        else:
            lbl = item

        y_data = df.loc[item, year_cols].dropna()

        fit_params = df.loc[item, param_cols].to_list()
        shift = df.loc[item,"shift"]
        
        x_data = [float(y) for y in range(1,len(y_data)+1)]

        x_model = np.linspace(1+shift, len(y_data), 100)
        y_model = fit_function(x_model-shift,*fit_params)
            
        if fit_function == power_law:
            a = str(int(round(fit_params[0],0)))
            b = str(round(fit_params[1],2))
            lbl += f"\n{a} t**({b})"

        ax.scatter(x_data, y_data)
        ax.plot(x_model, y_model, label=lbl)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncols=4
    )
    return fig


def plot_fit(df, selection, fit_function):
    """
    for a specific selection, extracts the plays_yearly_relative data from df
    and plots both this and the graph of fit_function fitted to that data
    """

    year_cols = [c for c in df.columns if isinstance(c,int)]
    param_cols = [c for c in df.columns if isinstance(c, str) and c.startswith("param_")]
    y_data = df.loc[selection, year_cols].dropna()
    
    fit_params = df.loc[selection, param_cols].to_list()
    shift = df.loc[selection,"shift"]
    
    x_data = [float(y) for y in range(1,len(y_data)+1)]

    x_model = np.linspace(1+shift, len(y_data), 100)
    y_model = fit_function(x_model-shift,*fit_params)

    fig, ax = plt.subplots()

    ax.scatter(x_data, y_data)
    ax.plot(x_model, y_model, color='r')
    ax.set_xlabel("Years")
    ax.set_ylabel("Listens")
    ptitle = ""
    if fit_function == power_law:
        a = str(int(round(fit_params[0],0)))
        b = str(round(fit_params[1],2))
        ptitle += f"{a} t**({b})"
    ax.set_title(ptitle)

    return fig

########################################################################
# New vs old
########################################################################

def plot_novelty_in_time( df, col_old, col_new, type_label, is_ratio):
    """
    plots a bar graph of new and old plays by year
    optionally, as a ratio
    """
    fig, ax = plt.subplots(figsize=(10,5))

    x = df["time"][1:]
    y_old = df[col_old][1:]
    y_new = df[col_new][1:]

    ax.set_xticks(x)
    ax.tick_params(axis="x", labelrotation=90)
    ax.set_xlabel("Years")
    ax.set_ylabel(type_label.capitalize())
    ax.bar(x,y_old, label=f"Old")
    ax.bar(x,y_new,bottom=y_old,label=f"New")

    ax.legend()
    return fig

def plot_novelties_in_time( df ):
    """
    returns new vs old plots for distinct items, distinct items ratio, total plays, total plays ratio
    """
    cols = ["items", "plays"]
    figs = {}
    
    for c in cols:
        if c == "items":
            type_label = "distinct"
        else:
            type_label = "total plays"
        figs[c] =  plot_novelty_in_time(df, "old_"+c, "new_"+c, type_label, is_ratio=False) 
        figs[c+"_ratio"] = plot_novelty_in_time(df, "old_"+c+"_ratio", "new_"+c+"_ratio", type_label="fraction "+type_label, is_ratio=True) 
        
    return figs
    
def plot_amplitudes_decays(df):
    """
    for power law fits At^*(b)
    plots b against A and annotates with the name of the associated item
    """
    amplitudes = df["param_0"]
    decays = df["param_1"]

    names = df.index
    
    fig, ax = plt.subplots()
    
    ax.scatter(amplitudes, decays)
    # the average
    #ax.scatter(sum(amplitudes)/len(amplitudes),sum(decays)/len(decays),color='red')
    xshift=0
    yshift=0
    for i, name in enumerate(names):
        if type(name) == tuple:
            name = name[0]
        ax.text(amplitudes[i]+xshift,decays[i]+yshift," -"+name)
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Exponent")
    return fig

def plot_amplitudes_decays_selection(df,items):
    """
    for power law fits At^*(b)
    plots b against A and annotates with the name of the associated item
    """
    amplitudes = df["param_0"]
    decays = df["param_1"]
    fig, ax = plt.subplots(layout="constrained")
    
    ax.scatter(amplitudes, decays, color="gray")

    names = []
    xshift=0
    yshift=0
    for item in items:
        A = df.loc[item,"param_0"]
        b = df.loc[item,"param_1"]
        ax.plot([A],[b], marker="o")
        if type(item) == tuple:
            name = item[0]
        else:
            name = item
        names.append(ax.text(A+xshift,b+yshift,""+name))
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Exponent")
    #adjust_text(names)

    return fig
