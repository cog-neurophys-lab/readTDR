import matplotlib
from matplotlib import gridspec
import matplotlib.dates as md
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import readTDR

root = tk.Tk()
root.withdraw()

matplotlib.use("TKAgg")

# colors
colors = {
    readTDR.TrialOutcome.Hit: "r",
    readTDR.TrialOutcome.EyeErr: [0.5, 0.5, 0.5],
    readTDR.TrialOutcome.Late: "b",
    readTDR.TrialOutcome.Early: "g",
    readTDR.TrialOutcome.NotStarted: [0.8, 0.8, 0.8]
}


if __name__ == "__main__":

    filetypes = (
        ('TDR files', '*.tdr'),
        ('All files', '*.*')
    )
    filename = filedialog.askopenfilename(defaultextension=".tdr", filetypes=filetypes)

    if filename is None or filename == "":
        exit()
    
    # filename = "test.tdr"
    tdr = readTDR.read_tdr(filename)
    df = tdr.get_trials_as_dataframe()
    df.set_index("tAbsTrialStart", inplace=True)
    df.index = pd.to_datetime(df.index)

    trials = tdr.get_trials()
    hits = tdr.get_hits()
    eyeerr = tdr.get_eyeerr()

    fig = plt.Figure()  # figure(tight_layout=False)
    gs = gridspec.GridSpec(3, 2, height_ratios=[3, 1, 2])
    ax1_trialDuration = plt.subplot(gs[0, :])
    ax2_performance = plt.subplot(gs[1, :], sharex=ax1_trialDuration)
    ax3_reactionTime = plt.subplot(gs[2, 0])
    

    # plot trial durations in data frame grouped by outcome    
    # # df.reset_index().plot(x=df.index.values.astype("float64") y="trialDurationMS", kind="scatter")
    # for key, group in df.groupby("outcome"):
    #     group.plot(y="trialDurationMS", 
    #         ax=ax1_trialDuration, legend=True, label=key.name,
    #         marker='o', linestyle='none')

    for outcome in readTDR.TrialOutcome:
        trials = tdr.get_trials_with_outcome([outcome])
        
        ax1_trialDuration.plot(
            [pd.to_datetime(trial.tAbsTrialStart) for trial in trials],
            [trial.get_trial_duration() for trial in trials],            
            markeredgecolor=colors.get(outcome, None),
            markerfacecolor=colors.get(outcome, None),
            markersize=2,
            marker="o",
            linestyle="none",
            label=outcome.name,
        )


    
    ax1_trialDuration.legend(fontsize="small", ncol=2, frameon=False)    
    ax1_trialDuration.set_ylabel("trial duration [ms]")

    
    # ax2_stimulusnumber.step([trial.tRelTrialStartMIN for trial in tdr.get_trials()], 
    #          [trial.stimulusNumber for trial in tdr.get_trials()])
    # ax2_stimulusnumber.set_ylabel("stimulus number")
    # ax2_stimulusnumber.set_xlabel("time [min]")
    

    # add text at bottom of figure with outcome counts using get_outcome_counts
    overallCountsStr = ""
    for key, value in tdr.get_outcome_counts().items():
        overallCountsStr += key + ": " + str(value) + " | "
    
    totalRewardMS = sum([trial.rewardDurationMS for trial in tdr.get_hits()])
    overallCountsStr += f"Reward = {totalRewardMS}"
    plt.figtext(0.5, 0.01, overallCountsStr, ha="center", fontsize=8)

    # add filename at top of figure
    plt.figtext(0.5, 0.9, filename, ha="center", fontsize=10)

    ax3_reactionTime.hist(
        [trial.reactionTimeMS for trial in hits],
        bins=20,
        color=colors[readTDR.TrialOutcome.Hit],
    )

    


    freq = df.groupby(level="tAbsTrialStart")["outcome"].value_counts(normalize=True)
    freq = freq.unstack(level=1)
    moving_avg = freq.rolling("5min").mean()
    moving_avg.plot(ax=ax2_performance, legend=True)
    # df.groupby("outcome")["outcome"].count().plot(legend=True, subplots=False)
    

    # create a locator object that specifies 10-minute intervals
    locator = md.MinuteLocator(byminute=[0,10,20,30,40,50])

    # set the locator and formatter for the x-axis
    # ax1.xaxis.set_major_locator(locator)
    ax2_performance.xaxis.set_major_formatter(md.DateFormatter('%M'))
    

    # maximize window
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.show()


