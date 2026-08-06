import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def power_law(x,a,b):
  return a*x**(-b)

def get_fit(y_data, fit_function, shift_to_max = False):
    shift = 0 
    if shift_to_max:
        while y_data[0] <  max(y_data):
            y_data =  y_data[1:]
            shift += 1
        
    if len(y_data)>1:
        x_data = [float(y) for y in range(1,len(y_data)+1)]
        popt, pcov = curve_fit(fit_function, x_data, y_data, p0=[50,2])
        perr = np.sqrt(np.diag(pcov))
        return popt, shift

    else:
        return (y_data, 0), shift
        

def plot_fit(df, selection, fit_function):

    y_data = df.loc[selection, "plays_yearly_relative"]
    fit_vars = df.loc[selection,"fit_vars"]
    shift = df.loc[selection,"shift"]
    
    x_data = [float(y) for y in range(1,len(y_data)+1)]
    
    x_model = np.linspace(min(x_data), max(x_data), 100)
    y_model = fit_function(x_model,*fit_vars)

    fig, ax = plt.subplots(figsize=(10, 5))

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

def plot_amplitudes_decays(df, display_item):

    fit_vars = df["fit_vars"]

    amplitudes = [i[0] for i in fit_vars]
    decays = [i[1] for i in fit_vars]

    names = df.index
    
    fig, ax = plt.subplots(figsize=(15,15))


    ax.scatter(amplitudes, decays)
    ax.scatter(sum(amplitudes)/len(amplitudes),sum(decays)/len(decays),color='red')
    
    for i, name in enumerate(names):
        #if display_item != 'artist':
        #    label = name+ " - "+ df.loc[name, "artist"]
        #else:
        #    label = name
        ax.text(amplitudes[i]-5,decays[i]+0.025,"   "+name)

    return fig


def calculate_power_laws(df, Ntop, fit_function):
    top_df = df.head(Ntop).drop(columns=["uts", "plays_yearly_absolute", "plays_yearly_cal"])
    top_df["get_fit_info"] = top_df["plays_yearly_relative"].apply(lambda x: get_fit(x, fit_function))
    top_df["fit_vars"] = top_df["get_fit_info"].apply(lambda x: x[0])
    top_df["shift"] = top_df["get_fit_info"].apply(lambda x: x[1])
    top_df = top_df.drop(columns=["get_fit_info"])
    return top_df

