from enum import Enum
import pathlib
import abc
import warnings
from dataclasses import dataclass, field
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
    date: datetime.date = None
    startTime: datetime.time = None
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
        self.date = datetime.datetime.strptime(self.date, '%d.%m.%Y').date()
        self.startTime = datetime.datetime.strptime(self.startTime, "%H:%M:%S").time()
        self.refreshRate = float(self.refreshRate)

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


class StartResponseSignalCode(Enum):
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


class IntervalType(Enum):
    Normal = 0
    WaitForStartSignal = 1
    ResponseAllowed = 2
    ResponseRequired = 3


@dataclass(kw_only=True)
class TrialSubheader1(Header):
    id: str = "$TS1"
    nLines: int = 1
    headerVersion: int = 3
    trialNumber: int = None
    tAbsTrialStart: str = None
    tRelTrialStartMIN: float = None
    tPositiveTriggerTransitionMS: list[float] = None
    tNegativeTriggerTransitionMS: list[float] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.trialNumber = int(tokens[3])
        self.tAbsTrialStart = tokens[4]
        self.tRelTrialStartMIN = float(tokens[5]) / 60.0 / 10000.0

        self.tPositiveTriggerTransitionMS = [float(t) * 1000 for t in tokens[6::2]]
        self.tNegativeTriggerTransitionMS = [float(t) * 1000 for t in tokens[7::2]]


@dataclass(kw_only=True)
class TrialSubheader2(Header):
    id: str = "$TS2"
    nLines: int = 1
    headerVersion: int = 1
    tIntendedIntervalDurationMS: list[float] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.tIntendedIntervalDurationMS = [float(t) * 1000 for t in tokens[3:]]


@dataclass(kw_only=True)
class TrialSubheader3(Header):
    id: str = "$TS3"
    nLines: int = 1
    headerVersion: int = 1
    intervalType: IntervalType = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.intervalType = [IntervalType(int(code)) for code in tokens[3:]]


@dataclass(kw_only=True)
class TrialSubheader4(Header):
    id: str = "$TS4"
    nLines: int = 1
    headerVersion: int = 1
    signals: list[StartResponseSignalCode] = None

    @dataclass
    class StartStopSignal:
        type: StartResponseSignalCode
        # interval of occurrence
        interval: int
        # time of occurrence relative to begin of interval
        tOccurrenceMS: float

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        nSignals = int(tokens[3])

        self.signals = []
        for iSignal in range(nSignals):
            type = StartResponseSignalCode(int(tokens[4 + iSignal * 3]))
            interval = int(tokens[5 + iSignal * 3])
            tOccurrenceMS = float(tokens[6 + iSignal * 3])
            self.signals.append(
                TrialSubheader4.StartStopSignal(type, interval, tOccurrenceMS)
            )


@dataclass(kw_only=True)
class TrialHeader(Header):
    id: str = "$TH1"
    nLines: int = 5
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
    subheader1: TrialSubheader1 = None
    subheader2: TrialSubheader2 = None
    subheader3: TrialSubheader3 = None
    subheader4: TrialSubheader4 = None

    def from_lines(self, lines: list[str]):
        # line 1
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.headerVersion == int(version)
        if int(version) >= 6:
            assert self.nLines == int(nLines)

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
            match subheaderId:
                case "$TS1":
                    self.subheader1 = subheader
                case "$TS2":
                    self.subheader2 = subheader
                case "$TS3":
                    self.subheader3 = subheader
                case "$TS4":
                    self.subheader4 = subheader


@dataclass(kw_only=True)
class ObjectHeader(Header):
    # // header / # of lines / version / object# / show-hide / Xpos / Ypos / Zpos / RotX / RotY / RotZ / ObjTypeName
    id: str = "$OH1"
    nLines: int = None  # including subheader
    headerVersion: int = 1
    objectNumber: int = None
    show: bool = None
    xPos: float = None
    yPos: float = None
    zPos: float = None
    rotX: float = None
    rotY: float = None
    rotZ: float = None
    typeName: str = None
    subheaders: list[Header] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]
        self.nLines = int(nLines)
        self.headerVersion = int(version)

        assert self.headerVersion == int(version)

        self.objectNumber = int(tokens[3])
        self.show = bool(int(tokens[4]))
        self.xPos = float(tokens[5])
        self.yPos = float(tokens[6])
        self.zPos = float(tokens[7])
        self.rotX = float(tokens[8])
        self.rotY = float(tokens[9])
        self.rotZ = float(tokens[10])
        self.typeName = " ".join(tokens[11:])

        # process subheaders
        lines = lines[1:]
        self.subheaders = []
        for iLine, line in enumerate(lines):
            if not line.startswith("$OS"):
                continue
            subheaderId, nLines, subheaderVersion = line.split()[:3]
            if not self.typeName in ObjectTypeNameMap.keys():
                continue
            nLines = int(nLines)
            subheader = ObjectTypeNameMap[self.typeName]()
            subheader.from_lines(lines[iLine : iLine + nLines])
            self.subheaders.append(subheader)


@dataclass(kw_only=True)
class FixationPoint1(Header):
    id: str = "$OS1"
    nLines: int = 1
    headerVersion: int = 1
    isActive: bool = None
    tAppearanceMS: list[float] = None
    tDisappearanceMS: list[float] = None

    def from_lines(self, lines: list[str]):
        tokens = lines[0].split()
        id, nLines, version = tokens[0:3]

        assert self.id == id
        assert self.nLines == int(nLines)
        assert self.headerVersion == int(version)

        self.isActive = bool(int(tokens[3]))
        self.tAppearanceMS = [float(t) * 1000 for t in tokens[4::2]]
        self.tDisappearanceMS = [float(t) * 1000 for t in tokens[5::2]]


ObjectTypeNameMap = {
    "Fixation Point 1": FixationPoint1,
}

HeaderIdMap = {
    "$FH1": FileStartHeader,
    "$FH2": FileEndHeader,
    "$TH1": TrialHeader,
    "$OH1": ObjectHeader,
}
SubHeaderIdMap = {
    "$TS1": TrialSubheader1,
    "$TS2": TrialSubheader2,
    "$TS3": TrialSubheader3,
    "$TS4": TrialSubheader4,
}


@dataclass
class Trial:
    # from $TH1
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

    # from $TS1
    tAbsTrialStart: str = None
    tRelTrialStartMIN: float = None
    tPositiveTriggerTransitionMS: list[float] = None
    tNegativeTriggerTransitionMS: list[float] = None

    # from $TS2
    tIntendedIntervalDurationMS: list[float] = None

    # from $TS3
    intervalType: IntervalType = None

    # from $TS4
    signals: list[TrialSubheader4.StartStopSignal] = None

    # from $OH1
    stimulusObjects: list[ObjectHeader] = field(default_factory=list)

    def from_trial_header(self, header: TrialHeader):
        self.trialNumber = header.trialNumber
        self.stimulusNumber = header.stimulusNumber
        self.timeSequence = header.timeSequence
        self.wasPerfectMonkey = header.wasPerfectMonkey
        self.wasHit = header.wasHit
        self.outcome = header.outcome
        self.manipulandum = header.manipulandum
        self.wasPreciseFixation = header.wasPreciseFixation
        self.reactionTimeMS = header.reactionTimeMS
        self.rewardDurationMS = header.rewardDurationMS
        self.lastInterval = header.lastInterval
        self.eyeControlFlag = header.eyeControlFlag
        self.intervalOfFrameLoss = header.intervalOfFrameLoss
        self.timeOfFrameLoss = header.timeOfFrameLoss

        self.tAbsTrialStart = header.subheader1.tAbsTrialStart
        self.tRelTrialStartMIN = header.subheader1.tRelTrialStartMIN
        self.tPositiveTriggerTransitionMS = (
            header.subheader1.tPositiveTriggerTransitionMS
        )
        self.tNegativeTriggerTransitionMS = (
            header.subheader1.tNegativeTriggerTransitionMS
        )

        self.tIntendedIntervalDurationMS = header.subheader2.tIntendedIntervalDurationMS

        self.intervalType = header.subheader3.intervalType

        self.signals = header.subheader4.signals

    def get_trial_duration(self) -> float:
        """Returns the duration of the trial in milliseconds."""
        return self.tNegativeTriggerTransitionMS[self.lastInterval]


@dataclass
class TDR:
    filename: pathlib.Path
    headers: list[Header]

    def get_trials(self) -> list[Trial]:
        trials: list[Trial] = []
        for header in self.headers:
            if isinstance(header, TrialHeader):
                trial = Trial()
                trial.from_trial_header(header)
                trials.append(trial)
            if isinstance(header, ObjectHeader):
                trials[-1].stimulusObjects.append(header)

        return trials

    def get_trials_with_outcome(self, outcomes: list[TrialOutcome]) -> list[Trial]:
        return [trial for trial in self.get_trials() if trial.outcome in outcomes]

    def get_hits(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.Hit])

    def get_wrongresponses(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.WrongResponse])

    def get_earlyhits(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.EarlyHit])

    def get_earlywrongresponses(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.EarlyWrongResponse])

    def get_earlies(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.Early])

    def get_lates(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.Late])

    def get_eyeerr(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.EyeErr])

    def get_inexpectedstartsignal(self) -> list[Trial]:
        return self.get_trials_with_outcome([TrialOutcome.InexpectedStartSignal])

    def get_wrongstartsignal(self) -> list[TrialHeader]:
        return self.get_trials_with_outcome([TrialOutcome.WrongStartSignal])

    def get_outcome_counts(self) -> dict[str, int]:
        return {
            outcome.name: len(self.get_trials_with_outcome([outcome]))
            for outcome in TrialOutcome
        }

    def get_trials_as_dataframe(self):
        import pandas as pd

        df = pd.DataFrame([vars(trial) for trial in self.get_trials()])
        df.tRelTrialStartMIN = pd.to_timedelta(df.tRelTrialStartMIN, unit="min")
        df.set_index("tRelTrialStartMIN", inplace=True)

        # change dtype of outcome column to categorical
        df["outcome"] = df["outcome"].astype("category")

        # add column with trial duration
        df["trialDurationMS"] = [
            trial.get_trial_duration() for trial in self.get_trials()
        ]

        return df


def read_tdr(filename: pathlib.Path) -> TDR:
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

        # workaround for VStim bug #210: reported nLines is in fact 5, not 4 as reported
        if headerId == "$TH1" and int(headerVersion) == 5:
            nLines = 5

        # subheaders are handled within header objects
        if headerId in SubHeaderIdMap.keys():
            continue

        if headerId not in HeaderIdMap.keys():
            warnings.warn(f"Unknown header {headerId}", category=UserWarning)
            continue

        header = HeaderIdMap[headerId]()
        header.from_lines(lines[iLine : iLine + nLines])
        headers.append(header)

    return TDR(
        headers=headers,
        filename=filename,
    )


if __name__ == "__main__":
    filename = "test.tdr"
    tdr = read_tdr(filename)
    trials = tdr.get_trials_as_dataframe()
    a = 1
