
def strip_zeros(x):
    while x[0] == 0:
        x = x[1:]
    return x

def all_plays(history_df):
    stats = {}
    
    plays = history_df["uts"]
    start_uts = min(plays)
    end_uts = max(plays)

    stats["plays_yearly_absolute"] =  playtime(plays, 0, start_uts, end_uts, timespan = "absolute")
    
    #calendar years
    stats["plays_yearly_cal"] = history_df.groupby("year").size().values.tolist()

    #calendar months
    stats["plays_monthly_cal"] = history_df.groupby(["year","month"]).size().values.tolist()

    # months aggregated 
    stats["plays_months"] =  history_df.groupby("month").size().values.tolist()
    # days aggregated
    stats["plays_days"] =  history_df.groupby("weekday").size().values.tolist()
    # days aggregated yearly
    stats["plays_days_yearly"] =  history_df.groupby(["year","weekday"]).size().values.tolist()
    
    return pd.DataFrame([stats])
    
def grouped_by_plays(history_df, grouping):
    """
    returns dataframes grouped by grouping = track-artist, artist, album-artist, etc
    """
    plays = history_df.groupby(grouping)["uts"].agg(list)
    
    # convert back to a dataframe
    plays_df = plays.to_frame()
    
    # yearly plays
    start_uts = history_df["uts"].min()
    end_uts = history_df["uts"].max()
    # plays by year counting from start of data 
    plays_df["plays_yearly_absolute"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "absolute"))
    # plays by year counting from first listen of particular artist/track/album
    plays_df["plays_yearly_relative"] = plays_df["uts"].apply(lambda x: playtime(x, 0, start_uts, end_uts, timespan = "relative"))

    #calendar years
    plays_by_cal_year = history_df.groupby("year")[grouping].value_counts()    
    plays_df["plays_yearly_cal"] = plays_by_cal_year.unstack("year", fill_value=0).reindex(plays_df.index).values.tolist()
    #calendar months
    plays_by_cal_month = history_df.groupby(["year","month"])[grouping].value_counts()    
    plays_df["plays_monthly_cal"] = plays_by_cal_month.unstack(["year","month"], fill_value=0).reindex(plays_df.index).values.tolist()
    # relative calendar_months
    plays_df["plays_monthly_relative"] = plays_df["plays_monthly_cal"].apply(strip_zeros)

    # months aggregated 
    plays_by_month = history_df.groupby("month")[grouping].value_counts()    
    plays_df["plays_months"] = plays_by_month.unstack("month", fill_value=0).reindex(plays_df.index).values.tolist()
    # days aggregated
    plays_by_day = history_df.groupby("weekday")[grouping].value_counts()    
    plays_df["plays_days"] = plays_by_day.unstack("weekday", fill_value=0).reindex(plays_df.index).values.tolist()

    # add total plays_column and sort    
    plays_df["total_plays"] = plays_df["uts"].apply(len)
    plays_df = plays_df.sort_values("total_plays", ascending=False)

    return plays_df

def playtime (list_of_plays, numberYears, start_uts, end_uts, timespan):
    """
    returns a list of plays per year for a given item
    """
    Y = 60*60*24*365
    Npresent = (end_uts-start_uts)/Y   

    earliest = min(list_of_plays)
    latest = max(list_of_plays)

    # how many years of listens are there
    N = (latest - earliest)/Y
    # how many years since first listen
    Nsince = (end_uts-earliest)/Y
    
    # if want all listening information from start of records
    if timespan == 'absolute':
        Nwhich, start = Npresent, start_uts
    # if just want listening information from first listen of item
    elif timespan == 'relative':
        Nwhich, start = Nsince, earliest
           
    ppy = []

    # only take items which have been listened to for more than numberYears
    #if N>numberYears:
    # only take items whose first listen is sufficiently long ago
    if Nsince>numberYears:
        # range is int part of Nwhich to exclude incomplete year at the end
        for n in range(int(Nwhich)):
            ppy.append( sum(1 for x in list_of_plays if start + n*Y <= x < start + (n+1)*Y ))
            
    return ppy

def novelty_in_time( time_grouping, item_grouping, history_df):
    """
    accumulate a record of novel vs old listens of item_grouping
    per time interval time_grouping
    """
    stats = []
    already_listened = set()

    dfy = history_df.groupby(time_grouping)[item_grouping]
    
    for time, time_data in dfy:
        new_items, old_items = 0,0
        new_plays, old_plays = 0,0
        time_counts = time_data.value_counts()
        for item, count in time_counts.items():
            if item not in already_listened:
                already_listened.add(item)
                new_plays +=  count
                new_items += 1
            else:
                old_plays += count
                old_items += 1
        stats.append( 
        {
        "time": time, "new_items": new_items, "old_items": old_items,
            "new_plays": new_plays, "old_plays": old_plays
        }
        )
    
    stats_df = pd.DataFrame(stats)
    
    stats_df["new_items_ratio"] = stats_df["new_items"]/(stats_df["new_items"]+stats_df["old_items"])
    stats_df["old_items_ratio"] = stats_df["old_items"]/(stats_df["new_items"]+stats_df["old_items"])
    
    stats_df["new_plays_ratio"] = stats_df["new_plays"]/(stats_df["new_plays"]+stats_df["old_plays"])
    stats_df["old_plays_ratio"] = stats_df["old_plays"]/(stats_df["new_plays"]+stats_df["old_plays"])
    
    return stats_df


def get_fit(y_data, fit_function, shift_to_max = False):
    """
    fits the function fit_function to the data y_data
    viewed as a function of timesteps [1,2,3,...]
    optionally, start the fit from the max value of y_data
    returns the fit parameters and the shift if possible
    otherwise returns None
    """
    if len(y_data) == 0:
        return None

    shift = 0 
    if shift_to_max:
        while y_data[0] <  max(y_data):
            shift += 1
            y_data =  y_data[1:]
    #if shift:
    #    print("shifted to:")
    #    print(y_data, "\n")
        
    if len(y_data)>1:
        try:
            x_data = [float(y) for y in range(1,len(y_data)+1)]
            popt, pcov = curve_fit(fit_function, x_data, y_data, p0=[max(y_data),2])
            perr = np.sqrt(np.diag(pcov))
            return (*popt, shift)
        except (RuntimeError, TypeError, ValueError):
            print ("Error:", y_data)
            return None
    else:
        return None

def calculate_fit(df, Ntop, fit_function, shift_to_max = False):
    """
    takes the first Ntop entries of dataframe df
    and fits the function fit_function to the the relatively yearly plays of each entry
    where fitting is not possible, the entries are dropped and an error message is logged to the terminal
    returns the new dataframe with fit information
    optionally, apply shift to fit only starting with max value of relatively yearly plays
    """
    top_df = df.head(Ntop).drop(columns=["uts", "plays_yearly_absolute", "plays_yearly_cal"])
    
    result = top_df["plays_yearly_relative"].apply(lambda x: get_fit(x, fit_function, shift_to_max))
    names = [f"param_{i}" for i in range(len(result.iloc[0])-1)] + ["shift"]
    top_df[names] = pd.DataFrame(result.tolist(), index=top_df.index)

    # drop cases where fitting is not possible
    # alternatively: keep them as null and don't drop them in st power laws tab selectbox
    # this would allow the same df to be used for both play histories and power laws
    print("\nUnable to make a fit for the following:")
    print( top_df[ top_df.isna().any(axis=1) ])
    print("\n")    
    top_df.dropna(inplace=True)
    return top_df

def format_item(item, top_df):
    """
    handles formatting of tuples (track/album, artist) as opposed to just artist
    """
    if type(item) == tuple:
        lbl = ' - '.join(item)
    else:
        lbl = item
    return f"{lbl} ({top_df.at[item,'total_plays']} plays)"
            
def show_play_history(df, display_item, calendar_axis, monthly_axis):
    """
    function to manage display of play_histories (calendar year, absolute, relative)
    for different display_item
    which can be one of: track, artist, album
    """
    min_ranking = 1
    max_ranking = len(df)
    ranking = st.slider("Ranking", min_ranking, max_ranking, (1, 50), key = f"{display_item}_ranking_slider")
    top_df = df.iloc[ranking[0]-1:ranking[1]]

    min_total_plays = min(top_df["total_plays"])
    max_total_plays = max(top_df["total_plays"])

    if min_total_plays != max_total_plays:
        total = st.slider("Total playcount", min_value = min_total_plays,  max_value = max_total_plays, value = ( min_total_plays, max_total_plays), key = f"{display_item}_total_play_slider")
        filter_df = top_df[ (top_df["total_plays"] >= total[0] ) & (top_df["total_plays"] <= total[1]) ]
    else:
        st.write(f"Total playcount: {min_total_plays}")
        filter_df = top_df

    selection = st.multiselect(
                f"{display_item.capitalize()} ({len(filter_df)} options)",
                filter_df.index,
                format_func = lambda x : format_item(x,top_df),
                key = f"{display_item}_select")
    #st.write(f"{len(selection)} selected of {len(filter_df)}")

    plot_options = {
        "Calendar years": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": False
         },
         "Years since start of data": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": False
         },
         f"Years since first listen of {display_item}": {
         "column": "plays_yearly_relative",
         "x": None,
         "xlabel": "Years since first listen",
         "cumulative": False,
         },
        "Calendar years (cumulative)": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": True,
         },
         "Years since start of data (cumulative)": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": True,
         },
         f"Years since first listen of {display_item} (cumulative)": {
         "column": "plays_yearly_relative",
         "x": None,
         "xlabel": "Years since first listen",
         "cumulative": True,
        },
        "Calendar months": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months (cumulative)": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": True
         },
        "Calendar months since first listen": {
         "column": "plays_monthly_relative",
         "x": None,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months since first listen (cumulative)": {
         "column": "plays_monthly_relative",
         "x": None,
         "xlabel": "Month",
         "cumulative": True
         },
        "Months of the year aggregated": {
         "column": "plays_months",
         "x": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
         "xlabel": "Month ",
         "cumulative": False
         },
        "Days of the week aggregated": {
         "column": "plays_days",
         "x": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
         "xlabel": "Day",
         "cumulative": False
         },
    }
    
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
                            
    options = plot_options[select_plot_type]

    if selection:
        fig = plot_play_histories(top_df, selection, options)
        st.pyplot(fig,width='stretch')
        
    #plays = top_df.at[selection,  sel_type]
    #st.pyplot(fig)

def show_everything_history(df, display_item, calendar_axis, monthly_axis):
    """
    function to manage display of play_histories (calendar year, absolute, relative)
    for different display_item
    which can be one of: track, artist, album
    """
    plot_options = {
        "Calendar years": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": False
         },
         "Years since start of data": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": False
         },
        "Calendar years (cumulative)": {
         "column": "plays_yearly_cal",
         "x": calendar_axis,
         "xlabel": "Year",
         "cumulative": True,
         },
         "Years since start of data (cumulative)": {
         "column": "plays_yearly_absolute",
         "x": None,
         "xlabel": "Years since start of data",
         "cumulative": True,
         },
        "Calendar months": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": False
         },
        "Calendar months (cumulative)": {
         "column": "plays_monthly_cal",
         "x": monthly_axis,
         "xlabel": "Month",
         "cumulative": True
         },
        "Months of the year aggregated": {
         "column": "plays_months",
         "x": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
         "xlabel": "Month ",
         "cumulative": False
         },
        "Days of the week aggregated": {
         "column": "plays_days",
         "x": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
         "xlabel": "Day",
         "cumulative": False
         },
    }
    
    select_plot_type = st.selectbox(
                            "Time range",
                            plot_options.keys(),
                            key = f"{display_item}_type_select")
                            
    options = plot_options[select_plot_type]

    if select_plot_type:
        fig = plot_play_history(df, options)
        st.pyplot(fig,width='stretch')


def show_novelties_in_time(df, display_item):
    """
    displays graphs of old vs new plays by year
    """
    figs= plot_novelties_in_time(df)

    st.subheader(f"Number of distinct old vs new {display_item}s played")
    st.pyplot(figs["items"])
    st.pyplot(figs["items_ratio"])
    st.subheader(f"Total plays of old vs new {display_item}s")
    st.pyplot(figs["plays"])
    st.pyplot(figs["plays_ratio"])

def show_power_laws(df, display_item):
    """
    allows selection and display of power law graphs
    """
    exponents = df["param_1"]

    sliders = []
    param_name = ["Coefficient", "Exponent"]
    for k in range(2):
        param = df[f"param_{k}"]    
        min_param = min(param)
        max_param = max(param)
        sliders.append( st.slider(param_name[k], min_param, max_param, (min_param, max_param), key=f"{display_item}_PL_slider_{k}") )

    filter_df = df[ (df["param_0"] >= sliders[0][0] ) & (df["param_0"] <= sliders[0][1]) &  (df["param_1"] >= sliders[1][0] ) & (df["param_1"] <= sliders[1][1]) ] 

    selection = st.multiselect(
                f"{display_item.capitalize()} ({len(filter_df)} options)",
                filter_df.index,
                format_func = lambda x : format_item(x,df),
                key = f"{display_item}_select_PL")

    fig_ad = plot_amplitudes_decays_selection(filter_df, selection)
    st.pyplot(fig_ad)
    if selection:
        fig = plot_fit_multi(filter_df, selection, power_law)
        st.pyplot(fig)



def plot_plays_top( play_df, Ntop = 10 ):
    top_df = play_df.head(Ntop).copy()
    for x in top_df.itertuples():
        print(x)
        fig = plot_play_history(x)
        st.pyplot(fig)
        plt.close(fig)
        
def plot_play_history(df, options):
    col = options["column"]
    fig, ax = plt.subplots(figsize=(15, 10))
    plays=df.iloc[0][col]
    if options["x"] == None:
        x = range(len(plays))
    else:
        x = options["x"]
    if options["cumulative"] == True:
        plays = [ sum(plays[:i+1]) for i in range(len(plays)) ] 
        ax.set_ylabel("Plays (cumulative)")
    else:
        ax.set_ylabel("Plays")
    ax.plot(x, plays, label= "all plays", marker='o')
    if options["xlabel"]=="Month":
        ax.set_xticks(np.arange(0, len(plays), 12))
    ax.set_xlabel(options["xlabel"])
    return fig

def plot_play_histories(df, items, options):
    """
    for each item in items, extracts and plots data about item from df
    dict options specifies which data and what type of graph
    """
    col = options["column"]
    fig, ax = plt.subplots(figsize=(15, 10))
    #fig, ax = plt.subplots()

    for item in items:
        plays = df.loc[item, col]
        if options["x"] == None:
            x = range(len(plays))
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
    if options["xlabel"]=="Month":
        ax.set_xticks(np.arange(0, len(plays), 12))
    ax.set_xlabel(options["xlabel"])
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncols=4
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
    fit_params = [df.loc[selection, c] for c in df.columns if c.startswith("param_")]
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
        fit_params = [df.loc[item, c] for c in df.columns if c.startswith("param_")]
        shift = df.loc[item,"shift"]
        x_data = [float(y) for y in range(1,len(y_data)+1)]

        x_model = np.linspace(1+shift, len(y_data), 100)
        y_model = fit_function(x_model-shift,*fit_params)

        if type(item) == tuple:
            lbl = ' - '.join(item)
        else:
            lbl = item
            
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
    


