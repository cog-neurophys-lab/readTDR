
import os.path
import datetime
import readTDR
import pathlib

def test_read_tdr():
    # use test.tdr in same directory as this file
    # extract path from __file__ and prepend to filename
    
    filename = pathlib.Path(__file__).parent / pathlib.Path("test.tdr")
    tdr = readTDR.read_tdr(filename)
    assert tdr.filename == filename
    assert len(tdr.headers) == 731
    assert isinstance(tdr.headers[0], readTDR.FileStartHeader)

def test_get_trials():    
    filename = pathlib.Path(__file__).parent / pathlib.Path("test.tdr")
    tdr = readTDR.read_tdr(filename)
    trials = tdr.get_trials()
    assert len(trials) == 5
    assert all([isinstance(trial, readTDR.Trial) for trial in trials])

# unit test for readTDR.FileStartHeader
def test_FileStartHeader():
    lines = [
        "$FH1   5   3",
        "1.42                // VStim program version",
        "1.01                // .tdr file format version",
        "03.02.2004  20:14:34        100     // date, start time, refresh rate",
        "d:\\user\\VStim\\startup\\StandardSubject.ini",
    ]
    header = readTDR.FileStartHeader()
    header.from_lines(lines)
    assert header.id == "$FH1"
    assert header.nLines == 5
    assert header.vstimVersion == "1.42"
    assert header.tdrVersion == "1.01"
    assert header.date == datetime.date(2004, 2, 3)
    assert header.startTime == datetime.time(20, 14, 34)
    assert header.refreshRate == 100.0
    assert header.iniFile == "d:\\user\\VStim\\startup\\StandardSubject.ini"

def test_TrialSubheader1():
    lines = ["$TS1   1   3     1  08:59:28   600915      0.0000  2.0000   2.0000  3.8000   3.8000  3.8200   3.8200  7.4700   7.4700  7.6200   7.6200  8.0400  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100   3.8200  8.3400   8.3400 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100   8.0400  3.8000"]
    header = readTDR.TrialSubheader1()
    header.from_lines(lines)
    assert header.id == "$TS1"
    assert header.nLines == 1
    assert header.headerVersion == 3
    assert header.trialNumber == 1
    assert header.tAbsTrialStart == "08:59:28"
    assert header.tRelTrialStartMIN == 600915 / 60.0 / 10000.0
    assert len(header.tPositiveTriggerTransitionMS) == 48
    assert len(header.tNegativeTriggerTransitionMS) == 48

def test_TrialSubheader2():
    lines = ["$TS2   1   1    2.0000   4.6300   0.0200   3.6500   0.1500   0.8000   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200"]
    header = readTDR.TrialSubheader2()
    header.from_lines(lines)
    assert header.id == "$TS2"
    assert header.nLines == 1
    assert header.headerVersion == 1
    assert len(header.tIntendedIntervalDurationMS) == 20

def test_TrialSubheader3():
    lines = ["$TS3   1   1     0    1    0    0    0    3    0    0    0    0    0    0    0    0    0    0    0    0    0    3"]
    header : readTDR.TrialSubheader3 = readTDR.TrialSubheader3()
    header.from_lines(lines)
    assert header.id == "$TS3"
    assert header.nLines == 1
    assert header.headerVersion == 1
    assert len(header.intervalType) == 20
    assert header.intervalType[0] == readTDR.IntervalType.Normal
    assert header.intervalType[1] == readTDR.IntervalType.WaitForStartSignal
    assert header.intervalType[19] == readTDR.IntervalType.ResponseRequired


def test_TrialSubheader4():
    lines = ["$TS4   1   1    2   -1   1  1800.0   1   5   420.0"]
    header : readTDR.TrialSubheader4 = readTDR.TrialSubheader4()
    header.from_lines(lines)
    assert header.id == "$TS4"
    assert header.nLines == 1
    assert header.headerVersion == 1
    assert len(header.signals) == 2
    assert header.signals[0].type == readTDR.StartResponseSignalCode.PressLever1
    assert header.signals[0].interval == 1
    assert header.signals[0].tOccurrenceMS == 1800.0
    assert header.signals[1].type == readTDR.StartResponseSignalCode.ReleaseLever1
    assert header.signals[1].interval == 5
    assert header.signals[1].tOccurrenceMS == 420.0

def test_TrialHeader():
    lines = [
        "$TH1   4   5     368    7    6    0    1    1    1    1    420.00    70    5    0   -1     -0.01",
        "$TS1   1   3     1  08:59:28   600915      0.0000  2.0000   2.0000  3.8000   3.8000  3.8200   3.8200  7.4700   7.4700  7.6200   7.6200  8.0400  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100   3.8200  8.3400   8.3400 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100  -0.0100 -0.0100   8.0400  3.8000",
        "$TS2   1   1    2.0000   4.6300   0.0200   3.6500   0.1500   0.8000   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200   0.5200",
        "$TS3   1   1     0    1    0    0    0    3    0    0    0    0    0    0    0    0    0    0    0    0    0    3",
        "$TS4   1   1    2   -1   1  1800.0   1   5   420.0"
    ]
    header : readTDR.TrialHeader = readTDR.TrialHeader()
    header.from_lines(lines)
    assert header.id == "$TH1"
    assert header.nLines == 5
    assert header.headerVersion == 5
    assert header.trialNumber == 368
    assert header.timeSequence == 6
    assert header.wasPerfectMonkey == False
    assert header.outcome == readTDR.TrialOutcome.Hit
    assert header.manipulandum == readTDR.Manipulandum.ReleaseLever1
    assert header.wasPreciseFixation == True
    assert header.reactionTimeMS == 420.0
    assert header.rewardDurationMS == 70
    assert header.lastInterval == 5
    assert header.eyeControlFlag == False
    assert header.intervalOfFrameLoss == -1
    assert header.timeOfFrameLoss == -0.01
    
    sh1 = readTDR.TrialSubheader1()
    sh1.from_lines([lines[1]])
    assert header.subheader1 == sh1

    sh2 = readTDR.TrialSubheader2()
    sh2.from_lines([lines[2]])
    assert header.subheader2 == sh2

    sh3 = readTDR.TrialSubheader3()
    sh3.from_lines([lines[3]])
    assert header.subheader3 == sh3

    sh4 = readTDR.TrialSubheader4()
    sh4.from_lines([lines[4]])
    assert header.subheader4 == sh4


def test_ObjectHeader():
    lines = ["$OH1  2 01  3  0 -35.63 -13.22   0.00   1.1   1.2   1.3 Morph PDF 1",
             "$OS1  1  05  0  0   1  3    0.00 3500.00 1000.00 1000.00    0.00   -1.00  500.00 -1"]

    header : readTDR.ObjectHeader = readTDR.ObjectHeader()
    header.from_lines(lines)
    assert header.id == "$OH1"
    assert header.nLines == 2
    assert header.headerVersion == 1
    assert header.objectNumber == 3
    assert header.show == False
    assert header.xPos == -35.63
    assert header.yPos == -13.22
    assert header.zPos == 0.0
    assert header.rotX == 1.1
    assert header.rotY == 1.2
    assert header.rotZ == 1.3
    assert header.typeName == "Morph PDF 1"

    # TODO: add tests for ObjectSubheader1

