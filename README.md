# readTDR
Python tools for reading the Trial Descriptor Record created by VStim.


## Packaging plotTDR into an executable on Windows
Create an environment with only the requirements of `plotTDR`
```
python -m venv env
.\env\Scripts\activate.bat
python -m pip install -r requirements_plotTDR.txt
python -m pip install pyinstaller
```
Run pyinstaller on `plotTDR.py`
```
pyinstaller --onefile --windowed --version-file file_version_info.txt .\readTDR\plotTDR.py
```