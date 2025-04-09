# readTDR

**Note: Development of the code for reading TDR files will continue [here](https://github.com/brain-bremen/vstim-python-tools). As of 2025, this repository is archived.**

Python tools for reading the Trial Descriptor Record created by VStim.

[![ReadTDR Tests](https://github.com/cog-neurophys-lab/readTDR/actions/workflows/run_tests.yml/badge.svg)](https://github.com/cog-neurophys-lab/readTDR/actions/workflows/run_tests.yml)

## Install `readTDR` into your Python environment

For the moment, the `readTDR` package can only be installed via `pip`. Either by cloning the repository and installing from the local files:

```
git clone https://github.com/cog-neurophys-lab/readTDR.git
python -m pip install -e readTDR
```

or directly from GitHub

```
python -m pip install git+https://github.com/cog-neurophys-lab/readTDR.git
```

## Read TDR files in your Python code

After installation, you can use the `readTDR.read_tdr(filename)` function to load a TDR file. the `get_trials` method will give you a `list` of `readTDR.Trial`s, which you can use to extract information about all the trials. For example, to get the trial durations of all hits, you can do to the following:

```python
import readTDR
tdr = readTDR.read_tdr('test.tdr')
trials = tdr.get_trials()

# get trial durations of all hits
trial_duration = [trial.get_trial_duration()
    for trial in trials if trial.outcome == readTDR.TrialOutcome.Hit
    ]
```

## Plot TDR file

[`plotTDR.py`](/readTDR/plotTDR.py) gives an example of how to use `readTDR` to plot a behavioral summary using the Python libraries [Matplotlib](https://matplotlib.org) and [pandas](https://pandas.pydata.org). `plotTDR` is also provided as a stand-alone executable on the [releases page](https://github.com/cog-neurophys-lab/readTDR/releases) and provides an easy to use way for online plotting of behavioral data such as the following:

![Example behavioral plot created with plotTDR](/docs/plotTDR.png?raw=true "Optional Title")

## Packaging plotTDR into an executable on Windows

1. Adjust the version of plotTDR in `file_version_info.txt`.

2. Create an environment with only the requirements of `plotTDR`.
   ```powershell
   python -m venv env
   .\env\Scripts\activate.bat
   python -m pip install -r requirements_plotTDR.txt
   python -m pip install pyinstaller
   ```
3. Run pyinstaller on `plotTDR.py`
   ```powershell
   pyinstaller --onefile --windowed --version-file file_version_info.txt .\readTDR\plotTDR.py
   ```
4. Find the `plotTDR.exe` for distribution in the `dist` folder.
