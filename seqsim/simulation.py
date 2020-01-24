"""
@author: Daniel Kulasingham

Main Cutplan File
"""
from numpy import array, isnan
from pandas import DataFrame, read_csv, Series, set_option
from os.path import dirname, realpath
from time import time
from pathos.multiprocessing import ProcessingPool as Pool, cpu_count
# import matplotlib.pyplot as plt
from statistics import mean
# from random import randint

from seqsim.classes import Recovery
from seqsim.helper import Timer, GetLogCoords, CalcBoardVol

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


def RecoveryRunner(r, coords):
    return r.RunRecovery(coords)


class SimSchedule(QObject):
    finished = pyqtSignal()
    # finishedSim = pyqtSignal()
    cp_progress = pyqtSignal(int)
    l_progress = pyqtSignal(float)

    def __init__(self, data, log_path=""):
        super().__init__()
        self.abort = False

        if log_path == "":
            log_path = dirname(realpath(__file__)) + "//logs//"

        self.logPath = log_path
        self.Cutplans = data
        self.ActVol = array(self.Cutplans.BoardVol)
        self.Recoveries = [None]*self.Cutplans.shape[0]
        self.completed = [False]*self.Cutplans.shape[0]
        self.progress = 0

    @pyqtSlot()
    def RunCutplan(self, timer=True):
        # initialisations
        id = []
        t = time()
        start_id = 0
        if id == []:
            start_id = sum(self.completed)
            id = list(range(start_id, self.Cutplans.shape[0]))
        numproc = cpu_count() - 2
        p = Pool(processes=numproc)
        # cpSched = self.Cutplans.iloc[id]

        # NumLogs = min(
        #     [self.Cutplans.LogCount[id]*1.5, [1000]*len(id)], axis=0)
        iterLog = []
        iterC = []
        lens = []
        descs = []
        rs = []
        for cID in id:
            c = self.Cutplans.iloc[cID]
            # find desc to be used to open the correct log data file
            desc = c.Description[2:4]+"-"+str(int(c.Description[5:7])-1)
            descs.append(desc)
            # get data from log data file
            FullLD = read_csv(self.logPath+desc+'.csv')
            # total = NumLogs[id.index(cID)]
            # lMax = int(min([total, FullLD.shape[0]]))
            # lID = randint(0, FullLD.shape[0]-lMax)
            # LD =
            # FullLD.iloc[lID:lID+lMax].reset_index().drop('index', axis=1)
            lens.append(FullLD.shape[0])

            # Set up lists for multiprocessing
            for i in range(FullLD.shape[0]):
                log = FullLD.iloc[i]
                iterLog.append(log)
                iterC.append(c)
                descs.append(desc)
                rs.append(Recovery(c))

# =============================================================================
#             completed = []
#             for lID in range(len(iterLog)):
#                 log = iterLog[lID]
#                 coords = GetLogCoords(log, c)
#                 completed.append(coords)
#                 Timer(id, cID, lID, time()-t)
# =============================================================================
        # if id.index(cID) > 0:
        #     p.restart()
        data = []
        data = p.imap(GetLogCoords, iterLog, iterC)
        completed = []
        i = 0
        j = 0
        LogRecoveries = self.CreateRecoveriesDF(lens[i])
        while j < len(iterLog):
            # try:
            j += 1
            res = next(iter(data))
            completed.append(res)
            if self.abort:
                self.abort = False
                return
            if timer:
                cur = j - sum(lens[0:i])
                rs[j-1].RunRecovery(res)
                self.LogTransfer(iterLog[j-1], LogRecoveries, cur-1)
                self.RecoveryTransfer(
                    rs[j-1], LogRecoveries, cur-1, descs[j-1])
                Timer((i+1, len(id)), j, len(iterLog), time()-t)
                self.l_progress.emit(cur/lens[i])
                if cur == lens[i]:
                    self.completed[cID] = True
                    self.cp_progress.emit(i)
                    self.Recoveries[i] = DataFrame(LogRecoveries)
                    i += 1
                    if i < len(lens):
                        LogRecoveries = self.CreateRecoveriesDF(lens[i])
            # except BaseException:
            #     print("fail")
            #     break
        # self.finishedSim.emit()
        # start = 0
        # for l in lens:
        #     LogRecoveries = self.CreateRecoveriesDF(l)
        #     for i in range(l):
        #         self.LogTransfer(iterLog[i], LogRecoveries, i)
        #         self.RecoveryTransfer(
        #             rs[start+i], LogRecoveries, lID, descs[start+i])
        #     self.Recoveries[cID] = DataFrame(LogRecoveries)
        #     start += l
        self.finished.emit()

    def AddNewRow(self, newCP):
        temp = self.Cutplans
        self.Cutplans = temp.append(newCP, True)
        self.Recoveries.append(None)
        self.completed.append(False)
        self.ActVol = array(self.Cutplans.BoardVol)

    def DeleteRow(self, row):
        self.Cutplans = self.Cutplans.drop(
            [row], axis=0
        ).reset_index().drop('index', axis=1)
        self.ActVol = array(self.Cutplans.BoardVol)
        del self.completed[row]
        del self.Recoveries[row]

    def AverageLog(self, id):
        c = self.Cutplans.iloc[id]
        # find desc to be used to open the correct log data file
        desc = c.Description[2:4]+"-"+str(int(c.Description[5:7])-1)
        # get data from log data file
        LD = read_csv(self.logPath+desc+'.csv')

        log = Series({
            "Length": mean(LD.Length),
            "SED": mean(LD.SED),
            "MinSED": mean(LD.MinSED),
            "LED": mean(LD.LED),
            "MaxLED": mean(LD.MaxLED),
            "Sweep": mean(LD.Sweep),
            "CompSweep": mean(LD.CompSweep),
            "Vol": mean(LD.Vol)
        })

        return log

    def GetTimberVolume(self, id):
        avgLog = self.AverageLog(id)
        c = self.Cutplans.iloc[id]
        r = Recovery(c)
        # Set to 1 for each WB
        for k in r.WB.keys():
            if len(r.WB[k]) > 0:
                for i in range(len(r.WB[k])):
                    r.WB[k][i] = 1
        # Set to 1 for each CB
        for i in range(len(r.CB)):
            if isnan(r.WB['CentreWB'][i]):
                for j in range(len(r.CB[i])):
                    r.CB[i][j] = 1
        TimVol = CalcBoardVol(avgLog, c, r)
        return TimVol

    def LogTransfer(self, log, LR, id):
        set_option('mode.chained_assignment', None)
        LR["Length"][id] = log.Length
        LR["SED"][id] = log.SED
        LR["MinSED"][id] = log.MinSED
        LR["LED"][id] = log.LED
        LR["MaxLED"][id] = log.MaxLED
        LR["Sweep"][id] = log.Sweep
        LR["CompSweep"][id] = log.CompSweep
        LR["Vol"][id] = log.Vol
        set_option('mode.chained_assignment', 'warn')

    def RecoveryTransfer(self, r, LR, id, desc):
        set_option('mode.chained_assignment', None)
        L = int(desc[-2:])*100
        # WINGBOARDS
        for k in r.WB.keys():
            if k == "CentreWB":
                continue
            if len(r.WB[k]) > 0:
                LR[k][id] = r.WB[k][0]*L
            if len(r.WB[k]) > 1:
                LR[k] = r.WB[k][1]*L
        # CENTREBOARDS
        for i in range(len(r.CB)):
            if isnan(r.WB['CentreWB'][i]):
                k1 = "CB"+str(i+1)+"-"
                for j in range(len(r.CB[i])):
                    LR[k1+str(j+1)] = r.CB[i][j]*L
            else:
                k1 = "CB"+str(i+1)
                LR[k1+"-1"][id] = r.WB['CentreWB'][i]*L
                LR[k1+"-WB"][id] = 1
        set_option('mode.chained_assignment', 'warn')

    def CreateRecoveriesDF(self, numLogs):
        return DataFrame({
            "Length": [0]*numLogs,
            "SED": [0]*numLogs,
            "MinSED": [0]*numLogs,
            "LED": [0]*numLogs,
            "MaxLED": [0]*numLogs,
            "Sweep": [0.0]*numLogs,
            "CompSweep": [0.0]*numLogs,
            "Vol": [0.0]*numLogs,
            "SecOutT": [0.0]*numLogs,
            "SecOutB": [0.0]*numLogs,
            "SecInT": [0.0]*numLogs,
            "SecInB": [0.0]*numLogs,
            "PrimOutL": [0.0]*numLogs,
            "PrimOutR": [0.0]*numLogs,
            "PrimInL": [0.0]*numLogs,
            "PrimInR": [0.0]*numLogs,
            "SecOutTS": [0.0]*numLogs,
            "SecOutBS": [0.0]*numLogs,
            "SecInTS": [0.0]*numLogs,
            "SecInBS": [0.0]*numLogs,
            "PrimOutLS": [0.0]*numLogs,
            "PrimOutRS": [0.0]*numLogs,
            "PrimInLS": [0.0]*numLogs,
            "PrimInRS": [0.0]*numLogs,
            "CB1-1": [0.0]*numLogs,
            "CB2-1": [0.0]*numLogs,
            "CB3-1": [0.0]*numLogs,
            "CB4-1": [0.0]*numLogs,
            "CB5-1": [0.0]*numLogs,
            "CB6-1": [0.0]*numLogs,
            "CB7-1": [0.0]*numLogs,
            "CB8-1": [0.0]*numLogs,
            "CB9-1": [0.0]*numLogs,
            "CB10-1": [0.0]*numLogs,
            "CB1-2": [0.0]*numLogs,
            "CB2-2": [0.0]*numLogs,
            "CB3-2": [0.0]*numLogs,
            "CB4-2": [0.0]*numLogs,
            "CB5-2": [0.0]*numLogs,
            "CB6-2": [0.0]*numLogs,
            "CB7-2": [0.0]*numLogs,
            "CB8-2": [0.0]*numLogs,
            "CB9-2": [0.0]*numLogs,
            "CB10-2": [0.0]*numLogs,
            "CB1-3": [0.0]*numLogs,
            "CB2-3": [0.0]*numLogs,
            "CB3-3": [0.0]*numLogs,
            "CB4-3": [0.0]*numLogs,
            "CB5-3": [0.0]*numLogs,
            "CB6-3": [0.0]*numLogs,
            "CB7-3": [0.0]*numLogs,
            "CB8-3": [0.0]*numLogs,
            "CB9-3": [0.0]*numLogs,
            "CB10-3": [0.0]*numLogs,
            "CB1-4": [0.0]*numLogs,
            "CB2-4": [0.0]*numLogs,
            "CB3-4": [0.0]*numLogs,
            "CB4-4": [0.0]*numLogs,
            "CB5-4": [0.0]*numLogs,
            "CB6-4": [0.0]*numLogs,
            "CB7-4": [0.0]*numLogs,
            "CB8-4": [0.0]*numLogs,
            "CB9-4": [0.0]*numLogs,
            "CB10-4": [0.0]*numLogs,
            "CB1-WB": [0]*numLogs,
            "CB2-WB": [0]*numLogs,
            "CB3-WB": [0]*numLogs,
            "CB4-WB": [0]*numLogs,
            "CB5-WB": [0]*numLogs,
            "CB6-WB": [0]*numLogs,
            "CB7-WB": [0]*numLogs,
            "CB8-WB": [0]*numLogs,
            "CB9-WB": [0]*numLogs,
            "CB10-WB": [0]*numLogs,
        })

    def __repr__(self):
        return (
            "Simulation Schedule with "+str(len(self.Cutplans))+" cutplans")
