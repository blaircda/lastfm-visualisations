import matplotlib.pyplot as plt
import numpy as np
#from adjustText import adjust_text
from organise_data import power_law


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
    """
    for each item in items, extracts and plots data about item from df
    dict options specifies which data and what type of graph
    """
    col = options["column"]
    #fig, ax = plt.subplots(figsize=(15, 10))
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
        if type(item) == tuple:
            lbl = ' - '.join(item)
        else:
            lbl = item
        ax.plot(x, plays, label= lbl, marker='o')
    ax.set_xlabel("Years")
    ax.legend(
        loc="upper left",
        bbox_to_anchor=(1.05, 1)
    )
    return fig

########################################################################
# Power laws
########################################################################

def plot_fit(df, selection, fit_function):
    """
    for a specific selection, extracts the plays_yearly_relative data from df
    and plots both this and the graph of fit_function fitted to that data
    """
    y_data = df.loc[selection, "plays_yearly_relative"]
    fit_vars = df.loc[selection,"fit_vars"]
    shift = df.loc[selection,"shift"]
    
    x_data = [float(y) for y in range(1,len(y_data)+1)]

    x_model = np.linspace(1+shift, len(y_data), 100)
    y_model = fit_function(x_model-shift,*fit_vars)

    fig, ax = plt.subplots()

    ax.scatter(x_data, y_data)
    ax.plot(x_model, y_model, color='r')
    ax.set_xlabel("Years")
    ax.set_ylabel("Listens")
    ptitle = ""
    if fit_function == power_law:
        a = str(int(round(fit_vars[0],0)))
        b = str(round(fit_vars[1],2))
        ptitle += f"{a} t**(-{b})"
    #ptitle = t[0][0]+' - '+t[0][1]
    #ptitle = ptitle + '\n Decay: '+str(int(round(a_opt,0)))+'*t**(-'+str(round(b_opt,2))+')'
    #ptitle = ptitle + '\n Error in decay: '+str(round(perr[1],2))
    ax.set_title(ptitle)

    return fig

def plot_fit_multi(df, items, fit_function):
    """
    for each item in items, extracts the plays_yearly_relative data from df
    and plots both this and the graph of fit_function fitted to that data
    """
    fig, ax = plt.subplots(layout="constrained")

    ax.set_xlabel("Years")
    ax.set_ylabel("Listens")

    for item in items:
        y_data = df.loc[item, "plays_yearly_relative"]
        fit_vars = df.loc[item,"fit_vars"]
        shift = df.loc[item,"shift"]
        x_data = [float(y) for y in range(1,len(y_data)+1)]

        x_model = np.linspace(1+shift, len(y_data), 100)
        y_model = fit_function(x_model-shift,*fit_vars)

        if type(item) == tuple:
            lbl = ' - '.join(item)
        else:
            lbl = item
            
        if fit_function == power_law:
            a = str(int(round(fit_vars[0],0)))
            b = str(round(fit_vars[1],2))
            lbl += f"\n{a} t**(-{b})"

        ax.scatter(x_data, y_data)
        ax.plot(x_model, y_model, label=lbl)

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncols=4
    )
    return fig
    
def plot_amplitudes_decays(df):
    """
    for power law fits At^*(b)
    plots b against A and annotates with the name of the associated item
    """
    fit_vars = df["fit_vars"]

    amplitudes = [i[0] for i in fit_vars]
    decays = [-i[1] for i in fit_vars]

    names = df.index
    
    fig, ax = plt.subplots()
    
    ax.scatter(amplitudes, decays)
    # the average
    #ax.scatter(sum(amplitudes)/len(amplitudes),sum(decays)/len(decays),color='red')
    
    for i, name in enumerate(names):
        if type(name) == tuple:
            name = name[0]
        ax.text(amplitudes[i]-5,decays[i]+0.025,"   "+name)
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Exponent")
    return fig

def plot_amplitudes_decays_selection(df,items):
    """
    for power law fits At^*(b)
    plots b against A and annotates with the name of the associated item
    """
    fit_vars = df["fit_vars"]
    amplitudes = [i[0] for i in fit_vars]
    decays = [-i[1] for i in fit_vars]
    
    fig, ax = plt.subplots(layout="constrained")
    
    ax.scatter(amplitudes, decays, color="gray")

    names = []
    for item in items:
        A,b = df.loc[item,"fit_vars"]
        ax.plot([A],[-b], marker="o")
        if type(item) == tuple:
            name = item[0]
        else:
            name = item
        names.append(ax.text(A-5,-b-0.025,"   "+name))
    ax.set_xlabel("Coefficient")
    ax.set_ylabel("Exponent")
    #adjust_text(names)

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
