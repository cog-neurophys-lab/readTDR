import sys
import time
import tkinter as tk
from tkinter import filedialog

import matplotlib
import matplotlib.animation as animation
import matplotlib.dates as md
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec

import readTDR
from readTDR import TrialOutcome

# colors
from enum import Enum
class Color(Enum):
    RED = (0.8, 0.0, 0.0)
    GREEN = (0.0, 0.5, 0.0)
    BLUE = (0.0, 0.0, 1.0)
    YELLOW = (1.0, 1.0, 0.0)
    CYAN = (0.0, 1.0, 1.0)
    MAGENTA = (1.0, 0.0, 1.0)
    ORANGE = (1.0, 165/255, 0)
    PURPLE = (128/255, 0, 128/255)
    PINK = (255/255, 192/255, 203/255)
    BROWN = (165/255, 42/255, 42/255)
    LIGHTGRAY = (0.7, 0.7, 0.7)
    GRAY = (0.5, 0.5, 0.5)
    DARKGRAY = (0.33, 0.33, 0.33)

colors = {
    TrialOutcome.Hit: Color.GREEN.value,
    TrialOutcome.EyeErr: Color.RED.value,
    TrialOutcome.Late: Color.ORANGE.value,
    TrialOutcome.Early: Color.PURPLE.value,
    TrialOutcome.NotStarted: Color.LIGHTGRAY.value,
    TrialOutcome.WrongResponse: Color.MAGENTA.value,
    TrialOutcome.WrongStartSignal: Color.GRAY.value,
    TrialOutcome.EarlyHit: Color.CYAN.value,
    TrialOutcome.EarlyWrongResponse: Color.PINK.value,
    TrialOutcome.InexpectedStartSignal: Color.DARKGRAY.value,
}

symbols = {
    TrialOutcome.Hit: "o",
    TrialOutcome.EyeErr: "+",
    TrialOutcome.Late: "x",
    TrialOutcome.Early: "v",
    TrialOutcome.NotStarted: ".",
    TrialOutcome.WrongResponse: "^",
    TrialOutcome.WrongStartSignal: "+",
    TrialOutcome.EarlyHit: "o",
    TrialOutcome.EarlyWrongResponse: "o",
    TrialOutcome.InexpectedStartSignal: "d",
}

# setup tkinter for file selection dialog
root = tk.Tk()
root.withdraw()

# setup matplotlib to use tkinter backend
matplotlib.use("TKAgg")
plt.ioff()


def plot_tdr(tdr: readTDR.TDR, fig=None):
    df = tdr.get_trials_as_dataframe()
    df.set_index("tAbsTrialStart", inplace=True)
    df.index = pd.to_datetime(df.index)
    trials = tdr.get_trials()

    # fig = plt.Figure()
    if fig is None:
        fig = plt.figure()

    fig.clf()

    # add filename at top of figure
    plt.figtext(0.5, 0.95, filename, ha="center", fontsize=10)

    # subplot layout
    gs = gridspec.GridSpec(3, 2, height_ratios=[3, 1, 2])
    gs.tight_layout(fig, rect=[0.0, 0, 0.5, 1])
    ax1_trialDuration = plt.subplot(gs[0, :])
    ax2_performance = plt.subplot(gs[1, :], sharex=ax1_trialDuration)
    ax3_reactionTime = plt.subplot(gs[2, 0])
    ax4_timing = plt.subplot(gs[2, 1])

    ax1_trialDuration.clear()
    ax2_performance.clear()
    ax3_reactionTime.clear()
    ax4_timing.clear()

    # plot trial durations as dots agains time
    for outcome in readTDR.TrialOutcome:
        ax1_trialDuration.plot(
            [
                pd.to_datetime(trial.tAbsTrialStart)
                for trial in trials
                if trial.outcome == outcome
            ],
            [
                trial.get_trial_duration()
                for trial in trials
                if trial.outcome == outcome
            ],
            markeredgecolor=colors.get(outcome, None),
            markerfacecolor=colors.get(outcome, None),
            markersize=3,
            marker=symbols.get(outcome, 'o'),
            linestyle="none",
            label=outcome.name,
        )

    ax1_trialDuration.legend(fontsize="small", ncol=2, frameon=False)
    ax1_trialDuration.set_ylabel("trial duration [ms]")

    # add stimulus number to scatter plot
    ax1_stimulusNumber = ax1_trialDuration.twinx()
    ax1_stimulusNumber.step(
        [pd.to_datetime(trial.tAbsTrialStart) for trial in trials],
        [trial.stimulusNumber for trial in trials],
        linewidth=0.5,
        color="k",
        alpha=0.5,
    )
    ax1_stimulusNumber.set_ylabel("stimulus number")

    # add text at bottom of figure with overall counts
    overallCountsStr = ""
    for key, value in tdr.get_outcome_counts().items():
        overallCountsStr += key + ": " + str(value) + " | "

    totalRewardMS = sum([trial.rewardDurationMS for trial in tdr.get_hits()])
    overallCountsStr += f"Reward = {totalRewardMS} ms"
    plt.figtext(0.95, 0.01, overallCountsStr, ha="right", fontsize=8)

    # add moving average of performance
    freq = df.groupby(level="tAbsTrialStart")["outcome"].value_counts(normalize=True)
    freq = freq.unstack(level=1)
    movingAvg = freq.rolling(window="5min", min_periods=10).mean()
    for outcome in readTDR.TrialOutcome:
        if outcome not in movingAvg.keys():
            continue
        ax2_performance.plot(
            movingAvg.index,
            movingAvg[outcome],
            color=colors.get(outcome, None),
            label=outcome.name,
        )
    ax2_performance.legend(fontsize="small", ncol=2, frameon=False)

    # set the locator and formatter for the x-axis
    ax2_performance.xaxis.set_major_formatter(md.DateFormatter("%H:%M"))

    # add reaction time histogram
    rt = [trial.reactionTimeMS for trial in tdr.get_hits() if trial.reactionTimeMS>0.0]
    avgRt = np.median(rt)
    ax3_reactionTime.hist(
        rt,
        bins=50,
        color=colors[readTDR.TrialOutcome.Hit],
        edgecolor="k",
        linewidth=0.5,
    )
    ax3_reactionTime.axvline(x=avgRt, color="k", linestyle="--")
    ax3_reactionTime.annotate(text=f"median = {avgRt:.1f} ms",
                              xy=(0.95, 0.95), xycoords="axes fraction", ha="right")
    ax3_reactionTime.set_xlabel("reaction time [ms]")
    ax3_reactionTime.set_ylabel("count")
    ax3_reactionTime.set_xlim(xmin=0.0)

    # add timing histogram
    includedOutcomes = [
        readTDR.TrialOutcome.Hit,
        readTDR.TrialOutcome.EyeErr,
        readTDR.TrialOutcome.Late,
        readTDR.TrialOutcome.Early,
        readTDR.TrialOutcome.WrongResponse,
    ]
    for outcome in includedOutcomes:
        ax4_timing.hist(
            [
                trial.get_trial_duration_after_start_signal()
                for trial in trials
                if trial.outcome == outcome
            ],
            bins=50,
            color=colors[outcome],
            label=outcome.name,
            alpha=0.5,
            edgecolor="k",
            linewidth=0.5,
        )
    ax4_timing.set_xlabel("trial duration since start signal [ms]")
    ax4_timing.set_ylabel("count")
    ax4_timing.set_xlim(xmin=0.0)
    ax4_timing.legend(fontsize="small", ncol=2, frameon=False)


if __name__ == "__main__":
    filetypes = (
        ("Trial Descriptor Record files (*.tdr)", "*.tdr"),
        ("All files", "*.*"),
    )
    filename = filedialog.askopenfilename(
        title="Pick a TDR file for plotting",
        defaultextension=".tdr",
        filetypes=filetypes,
    )

    if filename is None or filename == "":
        sys.exit()

    finished = False

    def on_close(event):
        global finished
        finished = True
        sys.exit()

    # fig = plt.Figure()
    fig = plt.figure(num=1, visible=False)
    fig.canvas.mpl_connect("close_event", on_close)
    mng: matplotlib.backends._backend_tk.FigureManagerTk = plt.get_current_fig_manager()
    mng.window.state("withdrawn")
    mng.window.title(filename)

    while not finished and plt.fignum_exists(fig.number):
        tdr = readTDR.read_tdr(filename)
        plot_tdr(tdr, fig)
        # maximize window
        # fig.canvas.manager.window.state("zoomed")
        fig.set_visible(True)
        mng.window.state("zoomed")

        plt.pause(15)

    sys.exit()
