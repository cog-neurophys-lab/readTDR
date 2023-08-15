from enum import Enum
import pathlib
import abc
import warnings
from dataclasses import dataclass
import datetime

def remove_comment(line: str):
    return line.split(sep="//", maxsplit=1)[0].rstrip()


@dataclass(kw_only=True)
class Header(abc.ABC):
    id: str
    headerVersion: int
    nLines: int

    def from_lines(self, lines: list[str]):
        pass


@dataclass(kw_only=True)
class FileStartHeader(Header):
    id: str = "$FH1"
    nLines: int = 5
    headerVersion: int = 3
    vstimVersion: str = None
    tdrVersion: str = None
    date: str = None
    startTime: str = None
    refreshRate: float = None
    iniFile: str = None

    def from_lines(self, lines: list[str]):
        # line 1
        id, nLines, version = lines[0].split()
        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        # line 2
        self.vstimVersion = remove_comment(lines[1])

        # line 3
        self.tdrVersion = remove_comment(lines[2])

        # line 4
        self.date, self.startTime, self.refreshRate = remove_comment(lines[3]).split()

        # line 5
        self.iniFile = remove_comment(lines[4])


@dataclass(kw_only=True)
class FileEndHeader(Header):
    ...


class TrialOutcome(Enum):
    NotStarted = 0
    Hit = 1
    WrongResponse = 2
    EarlyHit = 3
    EarlyWrongResponse = 4
    Early = 5
    Late = 6
    EyeErr = 7
    InexpectedStartSignal = 8
    WrongStartSignal = 9


class Manipulandum(Enum):
    NoManipulandum = 0
    PressLever1 = -1
    ReleaseLever1 = 1
    PressLever2 = -2
    ReleaseLever2 = 2
    PressLever3 = -3
    ReleaseLever3 = 3
    EyeResponseField0 = 11
    EyeResponseField1 = 12
    EyeResponseField2 = 13
    EyeResponseField3 = 14
    EyeResponseField4 = 15
    EyeResponseField5 = 16
    EyeResponseField6 = 17
    EyeResponseField7 = 18
    EyeResponseField8 = 19


class StartResponseSignal(Enum):
    PressLever1 = -1
    ReleaseLever1 = 1
    PressLever2 = -2
    ReleaseLever2 = 2
    PressLever3 = -3
    ReleaseLever3 = 3
    LookRF1 = 11
    LookRF2 = 12
    LookRF3 = 13
    LookRF4 = 14
    LookRF5 = 15
    LookRF6 = 16
    LookRF7 = 17
    LookRF8 = 18
    StartFixating = 20
    IsFixating = 21


@dataclass(kw_only=True)
class TrialHeader(Header):
    id: str = "$TH1"
    nLines: int = 4
    headerVersion: int = 5
    trialNumber: int = None
    stimulusNumber: int = None
    timeSequence: int = None
    wasPerfectMonkey: bool = None
    wasHit: bool = None
    outcome: TrialOutcome = None
    manipulandum: Manipulandum = None
    wasPreciseFixation: bool = None
    reactionTimeMS: float = None
    rewardDurationMS: float = None
    lastInterval: int = None
    eyeControlFlag: bool = None
    intervalOfFrameLoss: int = None
    timeOfFrameLoss: float = None
    subheaders : list[Header] = None

    def from_lines(self, lines: list[str]):
        # line 1
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]        

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.trialNumber = int(tokens[3])
        self.stimulusNumber = int(tokens[4])
        self.timeSequence = int(tokens[5])
        self.wasPerfectMonkey = bool(int(tokens[6]))
        self.wasHit = bool(int(tokens[7]))
        self.outcome = TrialOutcome(int(tokens[8]))
        self.manipulandum = Manipulandum(int(tokens[9]))
        self.wasPreciseFixation = bool(int(tokens[10]))
        self.reactionTimeMS = float(tokens[11])
        self.rewardDurationMS = float(tokens[12])
        self.lastInterval = int(tokens[13])
        self.eyeControlFlag = bool(int(tokens[14]))
        self.intervalOfFrameLoss = int(tokens[15])
        self.timeOfFrameLoss = float(tokens[16])

        # process subheaders
        lines = lines[1:]
        self.subheaders = []
        for iLine, line in enumerate(lines):
            if not line.startswith("$"):
                continue
            subheaderId, nLines, subheaderVersion = line.split()[:3]
            if not subheaderId in SubHeaderIdMap.keys():
                continue
            nLines = int(nLines)
            subheader = SubHeaderIdMap[subheaderId]()
            subheader.from_lines(lines[iLine : iLine + nLines])
            self.subheaders.append(subheader)

@dataclass(kw_only=True)
class TrialSubheader1(Header):
    id: str = "$TS1"
    nLines: int = 1
    headerVersion: int = 3
    trialNumber: int = None
    tAbsTrialStart : str = None
    tRelTrialStartMIN : float = None
    tPositiveTriggerTransitionMS : list[float] = None
    tNegativeTriggerTransitionMS : list[float] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]
        
        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.tTrialStart = tokens[4]
        self.tRelTrialStartMIN = float(tokens[5])/600.0

        self.tPositiveTriggerTransitionMS = [float(t)*1000 for t in tokens[6::2]]
        self.tNegativeTriggerTransitionMS = [float(t)*1000 for t in tokens[7::2]]
        
@dataclass(kw_only=True)
class TrialSubheader2(Header):
    id: str = "$TS2"
    nLines: int = 1
    headerVersion: int = 1
    tIntendedIntervalDurationMS : list[float] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]
        
        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.tIntendedIntervalDurationMS = [float(t)*1000 for t in tokens[4:]]


HeaderIdMap = {"$FH1": FileStartHeader, "$FH2": FileEndHeader, "$TH1": TrialHeader}
SubHeaderIdMap = {"$TS1": TrialSubheader1, "$TS2": TrialSubheader2}


def read_tdr(filename: pathlib.Path) -> list[Header]:
    with open(filename, "r") as file:
        lines: list[str] = file.readlines()
        
    headers: list[Header] = []
    for iLine, line in enumerate(lines):

        # only handle start of headers
        if not line.startswith("$"):
            continue

        line = remove_comment(line)

        headerId, nLines, headerVersion = line.split()[:3]
        nLines = int(nLines)

        # subheaders are handled within header objects
        if headerId in SubHeaderIdMap.keys():
            continue

        if headerId not in HeaderIdMap.keys():
            warnings.warn(f"Unknown header {headerId}", category=UserWarning)
            continue

        header = HeaderIdMap[headerId]()
        header.from_lines(lines[iLine : iLine + nLines])
        headers.append(header)

    return headers


if __name__ == "__main__":
    filename = "test.tdr"
    headers = read_tdr(filename)

    a = 1
