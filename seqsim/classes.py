from PyQt5.QtCore import QVariant, Qt, QSize, QRect, QModelIndex, \
    QVariantAnimation, QEasingCurve, QAbstractTableModel
from PyQt5.QtWidgets import QWidget, QSizePolicy, QApplication, QHBoxLayout
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics
from pandas import DataFrame
from math import floor
from random import random
from itertools import groupby
from numpy import max as npmax, min as npmin, nan, array as arraynp, isnan
from win32com.client import Dispatch
from time import sleep


class ExtendApp:
    def __init__(self, path=None):
        self.path = path
        self.results = None
        self.logpath = None
        self.cppath = None
        self.COM = Dispatch("Extend.Application")
        sleep(5)
        self.MenuCommand(4)
        self.modelOpened = False
        self.n = 0

    def OpenModel(self, path=None):
        if self.path is None:
            if path is None:
                raise Exception("No model was given.")
            else:
                self.path = path
                p = path
        else:
            if path is None:
                p = self.path
        self.COM.Execute("OpenExtendFile(\""+p+"\");")
        self.modelOpened = True

    def MenuCommand(self, command_number):
        self.COM.Execute("ExecuteMenuCommand("+str(command_number)+");")

    def Quit(self):
        self.__del__()

    def Save(self):
        self.MenuCommand(5)

    def RunSim(self):
        self.COM.Execute("IPCServerAsync(True);")
        self.MenuCommand(6000)

    def StopSim(self):
        # self.MenuCommand(30000)
        self.COM.Execute("currentStep = numSteps;")
        self.COM.Execute("currentSim = numSims;")

    def PauseSim(self):
        self.MenuCommand(30001)

    def isStopped(self):
        return self.getPhase() == "Not currently running a simulation"

    def isPaused(self):
        self.COM.Execute("GlobalInt0 = getSimulationPhase();")
        i = int(self.COM.Request("System", "GlobalInt0+:0:0:0"))
        return i == 0

    def setLogPath(self, logpath=None):
        if logpath is not None:
            self.logpath = logpath
        if self.modelOpened:
            self.COM.Execute(
                "DBDataSetAsString(1,2,2,1,\""+self.logpath+"\");")

    def setCPPath(self, cppath=None):
        if cppath is not None:
            self.cppath = cppath
        if self.modelOpened:
            self.COM.Execute(
                "DBDataSetAsString(1,2,2,2,\""+self.cppath+"\");")

    def getPhase(self):
        self.COM.Execute("GlobalInt0 = getSimulationPhase();")
        i = int(self.COM.Request("System", "GlobalInt0+:0:0:0"))
        return {
            0: "Not currently running a simulation",
            1: "CheckData",
            2: "StepSize",
            3: "InitSim",
            4: "Simulate",
            5: "FinalCalc",
            6: "BlockReport",
            7: "EndSim",
            8: "AbortSim",
            9: "PreCheckData",
            10: "PostInitSim",
            11: "SimStart",
            12: "SimFinish",
            13: "ModifyRunParameter",
            14: "OpenModelPhase"
        }[i]

    def getCurrentTime(self):
        return int(self.fReturn("currentTime"))

    def fReturn(self, f_str, i=None):
        if i is None:
            i = self.n
            if self.n == 9:
                self.n = 0
            else:
                self.n += 1
        self.COM.Execute("Global"+str(i)+" = "+f_str+";")
        return float(self.COM.Request("System", "Global"+str(i)+"+:0:0:0"))

    def getResults(self, s=1):
        # for i in range(1, 11):
        #     fstr = "DBDataGetAsNumber(2,7,"+str(i)+","+str(s)+")"
        #     self.COM.Execute("Global"+str(i-1)+" = "+fstr+";")
        # for i in range(10):
        #     x = float(self.COM.Request("System", "Global"+str(i)+"+:0:0:0"))
        #     r.append(x)

        r = []
        return r

    def __del__(self):
        self.COM.Execute("SetDirty(0);")
        self.MenuCommand(1)
        self.COM = None


class MyArc:
    def __init__(self, id, val, total, color=(0, 115, 119), highlighted=False,
                 targets=(0.4, 0.5)):
        super(MyArc, self).__init__()
        self.color = color
        self.highlighted = highlighted
        self.id = id
        self.val = (val[0]/total, val[1]/total)
        self.v = 0
        self.targets = targets

    def PaintArc(self, p):
        if self.v == 0:
            return
        size = p.device().width()
        if self.highlighted:
            linewidth = 0.275 * size
            rec = QRect(
                linewidth / 2, linewidth / 2,
                size - linewidth,
                size - linewidth
            )
        else:
            linewidth = 0.225 * size
            rec = QRect(
                linewidth / 2 + 0.05 * size, linewidth / 2 + 0.05 * size,
                size - linewidth - 0.1 * size,
                size - linewidth - 0.1 * size
            )

        span = min(self.v, self.val[1])
        # print(str(self.v)+str(self.val[1])+str(span))

        pen = QPen(self.GetColor())
        pen.setWidth(linewidth)
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        p.drawArc(rec, -16*360*self.val[0] + 16*90, -16*360*span + 16)

        if not self.highlighted and self.v > 0:
            rec = QRect(0, 0, size, 0.05*size)
            font = QFont("Tahoma")
            font.setBold(True)
            font.setPixelSize(0.045*size)
            if self.v > 0.075:
                rec2 = QRect(0, 0.05 * size, size, 0.225 * size)
                font2 = QFont("Tahoma")
                font2.setBold(True)
                font2.setPixelSize(0.05 * size)

            angle = self.val[0]*360 + self.v*180
            p.save()
            p.translate(size/2, size/2)
            p.rotate(angle)
            p.translate(-size / 2, -size / 2)
            p.setFont(font)
            p.drawText(rec, Qt.AlignCenter, self.id)
            if self.v > 0.075:
                p.setPen(QPen(QColor("white")))
                p.setFont(font2)
                p.drawText(
                    rec2, Qt.AlignCenter, "{:.1f}%".format(self.v*100))
            p.restore()

    def GetColor(self):
        if self.highlighted:
            if self.v < self.targets[0]:
                # red
                r = 250
                g = 70
                b = 65
            elif self.v < self.targets[1]:
                # orange
                r = 245
                g = 170
                b = 40
            else:
                # green
                r = 150
                g = 220
                b = 90
        else:
            r = self.color[0]
            g = self.color[1]
            b = self.color[2]
        return QColor(r, g, b)


class QtPyChart(QWidget):
    def __init__(self, dict, targets, parent=None, size=200):
        super(QtPyChart, self).__init__(parent)
        self.a = False
        self.size = size
        sizepolicy = QSizePolicy(
            QSizePolicy.Preferred,
            QSizePolicy.Preferred
        )
        sizepolicy.setHeightForWidth(True)
        sizepolicy.setWidthForHeight(True)
        self.setSizePolicy(sizepolicy)
        self.setMinimumSize(self.size, self.size)
        self.setMaximumSize(200, 200)
        self.dict = dict
        self.targets = targets
        self.v = 0
        self.anim = QVariantAnimation(self)
        self.anim.setEasingCurve(QEasingCurve.OutBounce)
        self.anim.setDuration(2000)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.valueChanged.connect(self.animationEvent)
        self.anim.finished.connect(self.animFinished)

        total = sum(dict.values())
        items = list(dict.items())
        start = items[0][1]
        self.arcs = [MyArc(
            items[0][0], (0, start), total,
            highlighted=True,
            targets=self.targets)]
        # self.arcs[0].anim.start()
        for k, v in items[1:]:
            arc = MyArc(k, (start, v), total)
            # arc.anim.start()
            self.arcs.append(arc)
            start += v

        # self.anim.start()

    def animStart(self):
        self.a = True
        self.anim.start()

    def animFinished(self):
        self.a = False

    def animationEvent(self, v):
        total = sum(self.dict.values())
        vals = [i/total for i in self.dict.values()]
        x = 0
        for i in range(len(vals)):
            if v > x+vals[i]:
                self.arcs[i].v = vals[i]
            elif v <= x:
                self.arcs[i].v = 0
            else:
                self.arcs[i].v = v - x
            x += vals[i]
        self.repaint()

    def sizeHint(self):
        return QSize(self.size, self.size)

    def paintEvent(self, e):
        p = QPainter(self)

        for a in self.arcs:
            a.PaintArc(p)

        p.setPen(QPen(QColor(0, 115, 119)))

        rectW = self.width()*0.45
        rectX = self.width()*0.275
        rect = QRect(rectX, rectX, rectW, rectW/2)
        font = QFont("Tahoma")
        font.setBold(True)
        font.setPixelSize(50)
        fontM = QFontMetrics(font)
        fontSize = fontM.size(0, "Recovery").width() + 20
        font.setPixelSize(50*(rectW/fontSize))
        p.setFont(font)
        p.drawText(
            rect,
            Qt.AlignHCenter | Qt.AlignBottom,
            self.arcs[0].id)

        rect = QRect(rectX, rectX+rectW/2, rectW, rectW/2)
        font.setBold(False)
        p.setFont(font)
        p.drawText(
            rect,
            Qt.AlignHCenter | Qt.AlignTop,
            "{:.1f}%".format(self.arcs[0].v*100))

    def heightForWidth(self, w):
        return w

    def updateResults(self, results):
        sumr = sum(results)
        keys = list(self.dict.keys())
        if sumr > 0:
            start = 0
            for i in range(len(results)):
                r = results[i]/sumr
                self.arcs[i].val = (start, r)
                start += r
                self.dict[keys[i]] = r
                if not self.a:
                    self.arcs[i].v = r
                # print(keys[i]+": "+str(r))
        else:
            self.arcs[0].val = (1, 0)
            self.dict[keys[0]] = 1
            for i in range(1, len(results)):
                self.arcs[i].val = (0, 0)
                self.dict[keys[i]] = 0
        if not self.a:
            self.repaint()
        return


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    layout = QHBoxLayout(Form)
    dict = {'Uptime': 5, 'MSL': 0.6, 'BSL': 2.4, 'TSL': 2}
    w = QtPyChart(dict, (0.3, 0.4), parent=Form, size=200)
    layout.addWidget(w)
    Form.setLayout(layout)

    Form.show()

    w.anim.start()
    sys.exit(app.exec_())


class PandasModel(QAbstractTableModel):
    def __init__(self, df=None, parent=None, completed=None):
        QAbstractTableModel.__init__(self, parent)
        self._df = df
        if completed is None:
            self._completed = [False]*df.shape[0]
        else:
            self._completed = completed

    def setCompleted(self, id, val=True):
        self._completed[id] = val

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.FontRole:
            font = QFont()
            font.setBold(self._completed[index.row()])
            return QVariant(font)
        elif role == Qt.TextAlignmentRole:
            return QVariant(
                Qt.AlignRight | Qt.AlignVCenter)
        elif role != Qt.DisplayRole:
            return QVariant()

        if not index.isValid():
            return QVariant()

        return QVariant(str(self._df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.iloc[index.row(), index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        flags = super(PandasModel, self).flags(index)
        if index.column() == 1:
            flags |= Qt.ItemIsEditable
            flags |= Qt.ItemIsSelectable
            flags |= Qt.ItemIsEnabled
            flags |= Qt.ItemIsDragEnabled
            flags |= Qt.ItemIsDropEnabled
        return flags

    def rowCount(self, parent=QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(
            colname,
            ascending=(order == Qt.AscendingOrder),
            inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


# class for how coordinates will be stored
class Coordinates():
    def __init__(self, X=0, Y=0, Z=0, Offset=[0, 0]):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Offset = Offset

    def __repr__(self):
        return (
            "X = "+str(self.X)+"\n"
            "Y = "+str(self.Y)+"\n"
            "Z = "+str(self.Z)+"\n"
            "Offset = "+str(self.Offset)
        )


# class for how recovery will be stored
class Recovery():
    def __init__(self, c):
        self.Cutplan = c
        self.CBNum = 0
        self.CB = [[]]*c.CBNum
        self.WB = {
            "SecOutT": [],
            "SecOutB": [],
            "SecInT": [],
            "SecInB": [],
            "PrimOutL": [],
            "PrimOutR": [],
            "PrimInL": [],
            "PrimInR": [],
            "CentreWB": [0]*c.CBNum
        }
        self.CheckCB()
        self.CheckWB()
        self.CheckSplit()

    def CheckSplit(self):
        c = self.Cutplan
        if c.SecOutSplitT:
            self.WB["SecOutT"].append(0)
        if c.SecOutSplitB:
            self.WB["SecOutB"].append(0)
        if c.SecInSplitT:
            self.WB["SecInT"].append(0)
        if c.SecInSplitB:
            self.WB["SecInB"].append(0)
        if c.PrimOutSplit:
            self.WB["PrimOutL"].append(0)
            self.WB["PrimOutR"].append(0)
        if c.PrimInSplit:
            self.WB["PrimInL"].append(0)
            self.WB["PrimInR"].append(0)
        self.WBNum = sum([len(i) for i in self.WB.values()]) - self.CBNum
        return

    def CheckCB(self):
        cbs = list(self.Cutplan[14:(14+self.Cutplan.CBNum)])
        count = [sum(1 for i in g) for _, g in groupby(cbs)]
        index = [i for i in range(len(count)) if count[i] == npmax(count)]
        start = sum(count[i] for i in range(index[floor(len(index)/2)]))
        for i in range(start, (start+npmax(count))):
            self.CB[i] = [0]*(self.Cutplan.HSNum+1)
        self.WB["CentreWB"][start:(start+npmax(count))] = [nan]*npmax(count)
        self.CBNum = npmax(count)
        return

    def CheckWB(self):
        c = self.Cutplan
        if c.PrimInThick > 0:
            self.WB["PrimInL"].append(0)
            self.WB["PrimInR"].append(0)
        if c.PrimOutThick > 0:
            self.WB["PrimOutL"].append(0)
            self.WB["PrimOutR"].append(0)
        if c.SecOutThickT:
            self.WB["SecOutT"].append(0)
        if c.SecOutThickB:
            self.WB["SecOutB"].append(0)
        if c.SecInThickT:
            self.WB["SecInT"].append(0)
        if c.SecInThickB:
            self.WB["SecInB"].append(0)
        return

    def RunRecovery(self, coords):
        # initialisations
        c = self.Cutplan
        cbNum = c.CBNum
        cbT = arraynp(c[14:(14+cbNum)])  # CB Thicknesses

        # cant calculations
        cantH = sum(cbT) + (sum(cbT > 0)-1)*c.SecK  # centreboards
        cantH += (c.SecInSplitT+1) * \
            (c.SecInThickT+c.SecK*(c.SecInThickT > 0))  # secondary in top
        cantH += (c.SecInSplitB+1) * \
            (c.SecInThickB+c.SecK*(c.SecInThickB > 0))  # secondary in bot
        cantH += (c.SecOutSplitT+1) * \
            (c.SecOutThickT+c.SecK*(c.SecOutThickT > 0))  # secondary out top
        cantH += (c.SecOutSplitB+1) * \
            (c.SecOutThickB+c.SecK*(c.SecOutThickB > 0))  # secondary out bot

        cH = cantH/2

        # find group length
        if c.Description[5:7] == '41':
            bL = 4000
        elif c.Description[5:7] == '46':
            bL = 4500
        else:
            bL = 4600

        # SECONDARY OUT TOP
        cH = self.FindRecovery(
            "SecOutT", coords, cH, bL,
            c.SecOutThickT, c.SecOutWidth/2, c.SecOutSplitT, c.SecK
        )

        # SECONDARY IN TOP
        cH = self.FindRecovery(
            "SecInT", coords, cH, bL,
            c.SecInThickT, c.SecInWidth/2, c.SecInSplitT, c.SecK
        )

        # CENTREBOARDS
        w = c.CBWidth/2  # CB Width
        hNum = c.HSNum + 1  # Number of horizontal saws
        hW = arraynp(c[37:(37+hNum)])  # HoriSaw board widths
        hK = list(c[41:(41+hNum-1)])  # Horizontal saw kerfs
        hK.append(0)
        for i in range(cbNum):
            t = cbT[i]
            if hNum > 1 and isnan(self.WB["CentreWB"][i]):
                hsW = -c.CBWidth/2 + hW[0]/2
                for j in range(hNum):
                    wane = self.GetWane(coords, cH, t, hW[j]/2)
                    self.CB[i][j] = npmin(wane) + 0.0  # recovery 0 if any wane
                    hsW = hsW + hW[j] + hK[j]
            else:
                wane = self.GetWane(coords, cH, t, w)
                if isnan(self.WB["CentreWB"][i]):
                    self.CB[i][0] = npmin(wane) + 0.0  # recovery 0 if any wane
                else:
                    self.WB["CentreWB"][i] = self.BoardRecovery(
                        wane, coords.Z, bL)

            cH = cH - t - c.SecK

        # SECONDARY IN BOTTOM
        cH = self.FindRecovery(
            "SecInB", coords, cH, bL,
            c.SecInThickB, c.SecInWidth/2, c.SecInSplitB, c.SecK
        )

        # SECONDARY OUT BOTTOM
        cH = self.FindRecovery(
            "SecOutB", coords, cH, bL,
            c.SecOutThickB, c.SecOutWidth/2, c.SecOutSplitB, c.SecK
        )

        # PRIMARY IN
        cW = c.CBWidth/2
        t = c.PrimInThick
        w = c.PrimInWidth/2
        split = c.PrimInSplit
        if t > 0:
            cW = cW + c.PrimInK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimInR"][0] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimInL"][0] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t
        if split:
            cW = cW + c.PrimInK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimInR"][1] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimInL"][1] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t

        # PRIMARY OUT
        cW = c.CBWidth/2
        t = c.PrimOutThick
        w = c.PrimOutWidth/2
        split = c.PrimOutSplit
        if t > 0:
            cW = cW + c.PrimOutK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimOutR"][0] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimOutL"][0] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t
        if split:
            cW = cW + c.PrimOutK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimOutR"][1] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimOutL"][1] = self.BoardRecovery(wane, coords.Z, bL)

        return

    def RunRecoveryRand(self, coordsOri, offS=3):
        # initialisations
        c = self.Cutplan
        cbNum = c.CBNum
        cbT = arraynp(c[14:(14+cbNum)])  # CB Thicknesses
        # off = (offS + npmax(coordsOri.X[0])/100 - 1)/25
        off = offS/25
        off = npmax(coordsOri.X[0])*off
        rX = random()*off - off/2
        rY = random()*off - off/2
        coords = Coordinates(
            coordsOri.X,
            coordsOri.Y,
            coordsOri.Z,
            (coordsOri.Offset[0] + rX, coordsOri.Offset[1] + rY)
        )

        # cant calculations
        cantH = sum(cbT) + (sum(cbT > 0)-1)*c.SecK  # centreboards
        cantH += (c.SecInSplitT+1) * \
            (c.SecInThickT+c.SecK*(c.SecInThickT > 0))  # secondary in top
        cantH += (c.SecInSplitB+1) * \
            (c.SecInThickB+c.SecK*(c.SecInThickB > 0))  # secondary in bot
        cantH += (c.SecOutSplitT+1) * \
            (c.SecOutThickT+c.SecK*(c.SecOutThickT > 0))  # secondary out top
        cantH += (c.SecOutSplitB+1) * \
            (c.SecOutThickB+c.SecK*(c.SecOutThickB > 0))  # secondary out bot

        cH = cantH/2

        # find group length
        if c.Description[5:7] == '41':
            bL = 4000
        elif c.Description[5:7] == '46':
            bL = 4500
        else:
            bL = 4600

        # SECONDARY OUT TOP
        cH = self.FindRecovery(
            "SecOutT", coords, cH, bL,
            c.SecOutThickT, c.SecOutWidth/2, c.SecOutSplitT, c.SecK
        )

        # SECONDARY IN TOP
        cH = self.FindRecovery(
            "SecInT", coords, cH, bL,
            c.SecInThickT, c.SecInWidth/2, c.SecInSplitT, c.SecK
        )

        # CENTREBOARDS
        w = c.CBWidth/2  # CB Width
        hNum = c.HSNum + 1  # Number of horizontal saws
        hW = arraynp(c[37:(37+hNum)])  # HoriSaw board widths
        hK = list(c[41:(41+hNum-1)])  # Horizontal saw kerfs
        hK.append(0)
        for i in range(cbNum):
            t = cbT[i]
            if hNum > 1 and isnan(self.WB["CentreWB"][i]):
                hsW = -c.CBWidth/2 + hW[0]/2
                for j in range(hNum):
                    wane = self.GetWane(coords, cH, t, hW[j]/2)
                    self.CB[i][j] = npmin(wane) + 0.0  # recovery 0 if any wane
                    hsW = hsW + hW[j] + hK[j]
            else:
                wane = self.GetWane(coords, cH, t, w)
                if isnan(self.WB["CentreWB"][i]):
                    self.CB[i][0] = npmin(wane) + 0.0  # recovery 0 if any wane
                else:
                    self.WB["CentreWB"][i] = self.BoardRecovery(
                        wane, coords.Z, bL)

            cH = cH - t - c.SecK

        # SECONDARY IN BOTTOM
        cH = self.FindRecovery(
            "SecInB", coords, cH, bL,
            c.SecInThickB, c.SecInWidth/2, c.SecInSplitB, c.SecK
        )

        # SECONDARY OUT BOTTOM
        cH = self.FindRecovery(
            "SecOutB", coords, cH, bL,
            c.SecOutThickB, c.SecOutWidth/2, c.SecOutSplitB, c.SecK
        )

        # PRIMARY IN
        cW = c.CBWidth/2
        t = c.PrimInThick
        w = c.PrimInWidth/2
        split = c.PrimInSplit
        if t > 0:
            cW = cW + c.PrimInK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimInR"][0] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimInL"][0] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t
        if split:
            cW = cW + c.PrimInK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimInR"][1] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimInL"][1] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t

        # PRIMARY OUT
        cW = c.CBWidth/2
        t = c.PrimOutThick
        w = c.PrimOutWidth/2
        split = c.PrimOutSplit
        if t > 0:
            cW = cW + c.PrimOutK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimOutR"][0] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimOutL"][0] = self.BoardRecovery(wane, coords.Z, bL)

            cW = cW + t
        if split:
            cW = cW + c.PrimOutK

            wane = self.GetWane(coords, cW+t, t, w, True)
            self.WB["PrimOutR"][1] = self.BoardRecovery(wane, coords.Z, bL)
            wane = self.GetWane(coords, -cW, t, w, True)
            self.WB["PrimOutL"][1] = self.BoardRecovery(wane, coords.Z, bL)

        return

    def FindRecovery(self, board, coords, cH, bL, t, w, split, k):
        if t > 0:
            wane = self.GetWane(coords, cH, t, w)
            self.WB[board][0] = self.BoardRecovery(wane, coords.Z, bL)
            cH = cH - t - k
        if split:
            wane = self.GetWane(coords, cH, t, w)
            self.WB[board][1] = self.BoardRecovery(wane, coords.Z, bL)
            cH = cH - t - k
        return cH

    def AddRecovery(self, r):
        # Get sum of WB
        for k in r.WB.keys():
            if len(r.WB[k]) > 0:
                for i in range(len(r.WB[k])):
                    self.WB[k][i] += r.WB[k][i]
        # Get sum of CB
        for i in range(len(r.CB)):
            if isnan(r.WB['CentreWB'][i]):
                for j in range(len(r.CB[i])):
                    self.CB[i][j] += r.CB[i][j]

    def AverageRecovery(self, numR):
        # Get average of WB
        for k in self.WB.keys():
            if len(self.WB[k]) > 0:
                for i in range(len(self.WB[k])):
                    self.WB[k][i] /= numR
        # Get average of CB
        for i in range(len(self.CB)):
            if isnan(self.WB['CentreWB'][i]):
                for j in range(len(self.CB[i])):
                    self.CB[i][j] /= numR

    # finding the where board falls outside of log
    def GetWane(self, coords, cH, t, w, prim=False):
        allowance = 0.025
        a = 1-allowance
        if prim:
            Y = coords.X
            X = coords.Y
            Offset = [coords.Offset[1], coords.Offset[0]]
        else:
            Y = coords.Y
            X = coords.X
            Offset = [coords.Offset[0], coords.Offset[1]]
        if cH > t/2:
            wane = (
                sum(
                    (Y >= cH+Offset[1]-t*allowance)
                    * (X <= (-a*w+Offset[0]))
                ) * sum(
                    (Y >= cH+Offset[1]-t*allowance)
                    * (X >= (a*w+Offset[0]))
                )
            ) > 0
        else:
            wane = (
                sum(
                    (Y <= cH+Offset[1]-a*t)
                    * (X <= (-a*w+Offset[0]))
                ) * sum(
                    (Y <= cH+Offset[1]-a*t)
                    * (X >= (a*w+Offset[0]))
                )
            ) > 0
        return wane

    # given the affect of wane, determine cutback as percentage of board length
    def BoardRecovery(self, wane, fullZ, bL):
        # Initialisations
        Z = fullZ[0]
        noWane = [0]
        startZ = 0
        for i in range(len(wane)):
            if not wane[i]:
                noWane.append(Z[i]-startZ)
                startZ = Z[i]
        noWane.append(Z[i]-startZ)

        newL = npmax(noWane)
        if bL == 4600:
            cutbacks = [4600, 3600, 3300, 3000, 2700]
        if bL == 4500:
            cutbacks = [4500, 3600, 3300, 3000, 2700]
        else:
            cutbacks = [4000, 3600, 3300, 3000, 2700]
        for i in range(len(cutbacks)):
            if newL >= cutbacks[i]:
                return cutbacks[i]/bL
        return 0

    def __repr__(self):
        return (
            "{:d} Centreboard(s) and {:d} Wingboard(s)".format(
                self.CBNum, self.WBNum)
        )
