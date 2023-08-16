import matplotlib
from matplotlib import gridspec
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
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
}


if __name__ == "__main__":
    filename = filedialog.askopenfilename()

    # filename = "test.tdr"
    tdr = readTDR.read_tdr(filename)
    hits = tdr.get_hits()
    eyeerr = tdr.get_eyeerr()

    fig = plt.Figure()  # figure(tight_layout=False)
    gs = gridspec.GridSpec(3, 2, height_ratios=[3, 1, 2])
    ax1_trialDuration = plt.subplot(gs[0, :])
    ax2_stimulusnumber = plt.subplot(gs[1, :], sharex=ax1_trialDuration)
    ax3_reactionTime = plt.subplot(gs[2, 0])

    # plot trial durations
    for outcome in readTDR.TrialOutcome:
        trials = tdr.get_trials_with_outcome([outcome])
        ax1_trialDuration.plot(
            [trial.subheader1.tRelTrialStartMIN for trial in trials],
            [trial.get_trial_duration() for trial in trials],
            "s",
            markeredgecolor=colors.get(outcome, None),
            markerfacecolor=colors.get(outcome, None),
            markersize=2,
            label=outcome.name,
        )

    ax1_trialDuration.legend(fontsize="small", ncol=2, frameon=False)    
    ax1_trialDuration.set_ylabel("trial duration [ms]")

    
    ax2_stimulusnumber.step([trial.subheader1.tRelTrialStartMIN for trial in tdr.get_trials()], 
             [trial.stimulusNumber for trial in tdr.get_trials()])
    ax2_stimulusnumber.set_ylabel("stimulus number")
    ax2_stimulusnumber.set_xlabel("time [min]")
    

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

    # maximize window
    mng = plt.get_current_fig_manager()
    mng.window.state('zoomed')

    plt.show()
