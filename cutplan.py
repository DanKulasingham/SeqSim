# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cutplan.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtGui import QCursor, QBrush, QPen, QColor, QIcon, QFont, \
    QPainter, QMovie
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject, QSize, QRect, Qt, \
    QRectF, QMetaObject, QThread, QPropertyAnimation, QEasingCurve, \
    QCoreApplication
from PyQt5.QtWidgets import QWidget, QApplication, QSizePolicy, QPushButton, \
    QVBoxLayout, QLabel, QGraphicsOpacityEffect, QMessageBox
from subprocess import check_output, CalledProcessError
from addWindow import AddCutplanDialog
from pyodbc import connect as sqlconnect, \
    ProgrammingError as sqlProgrammingError
from pandas import read_sql
from seqsim.helper import DrawCutplan, LogScanner
# from seqsim.simulation import SimSchedule


class CutplanLoader(QObject):
    cutplanloaded = pyqtSignal(int)

    def __init__(self):
        super(CutplanLoader, self).__init__()
        self.id = 0
        self.cutplanid = 0
        self.logcount = None
        self.data = None
        self.des = None

    @pyqtSlot()
    def loadCutplan(self):
        sqlfile = "support\\cpquery2.sql"
        imgfolder = "images\\cps\\"

        conn = sqlconnect(LogScanner)

        f = open(sqlfile, 'r')
        sqltext = f.read()
        sqltext = sqltext.replace("@CPID", str(self.cutplanid))
        self.data = read_sql(sqltext, conn)
        group = self.data.Description[0][2:4]
        length = self.data.Description[0][5:7]
        des = length[0]+"."+length[1]+"m "+group
        self.des = read_sql(
            "Select Description From Logs Where Left(Description,7)=\'"
            + des + "\'", conn)
        DrawCutplan(conn, self.data.iloc[0], self.id+1, folder=imgfolder,
                    logs=self.logcount)

        self.cutplanloaded.emit(self.id)


class CPProgress(QWidget):
    mouseHover = pyqtSignal(bool, int)

    def __init__(self, id, parent=None, size=250):
        super(CPProgress, self).__init__(parent)
        self.id = id
        self.size = size
        self.v = 100
        self.setMouseTracking(True)

    @pyqtSlot()
    def enterEvent(self, event):
        self.mouseHover.emit(True, self.id)

    @pyqtSlot()
    def leaveEvent(self, event):
        self.mouseHover.emit(False, self.id)

    def sizeHint(self):
        return QSize(self.size, self.size)

    def paintEvent(self, e):
        if self.v == 100:
            return

        p = QPainter(self)
        brush = QBrush(QColor(255, 255, 255, 127))
        p.setBrush(brush)
        pen = QPen()
        pen.setStyle(Qt.NoPen)
        p.setPen(pen)

        start = 16*90 - 16*360*(self.v/100)
        span = -16*360*(1-(self.v/100))
        # start = 90*16 - 120*16
        # span = -(360-120)*16
        size = p.device().width()
        rect = QRectF(0, 0, size, size)
        # print(str(self.v)+str(self.val[1])+str(span))

        p.drawPie(rect, start, span)

    def setValue(self, v):
        if v >= 100:
            v = 100
        self.v = v
        self.repaint()

    def heightForWidth(self, w):
        return w


class HoverButton(QPushButton):
    mouseHover = pyqtSignal(bool, int)

    def __init__(self, parent=None, id=0):
        self.id = id
        QPushButton.__init__(self, parent)
        self.setMouseTracking(True)

    @pyqtSlot()
    def enterEvent(self, event):
        self.mouseHover.emit(True, self.id)

    @pyqtSlot()
    def leaveEvent(self, event):
        self.mouseHover.emit(False, self.id)


class CutplanWidget(QWidget):
    newcutplans = pyqtSignal(bool)
    cploadfinish = pyqtSignal()

    def setupUi(self, Form, size=250):
        self.data = None
        self.addData = None
        self.host = "172.16.90.241"
        self.CPWidgets = []
        self.CPImg = []
        self.CPProgress = []
        self.CPLabels = []
        self.CPWidgetsH = []
        self.anims = []
        self.graphics = []
        self.CPLoads = []
        self.CPNum = 0
        self.CPMinSize = 0
        self.size = size

        Form.setObjectName("Form")
        Form.setMaximumWidth(self.size)
        sizePolicy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Expanding)
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumWidth(self.size)
        Form.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.horizontalLayout = QVBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(15)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # CPWidgets
        self.CPLayout = QVBoxLayout()
        self.CPLayout.setContentsMargins(0, 0, 0, 0)
        self.CPLayout.setObjectName("CPLayout")
        self.horizontalLayout.addLayout(self.CPLayout)

        self.AddButton = QPushButton(Form)
        sizePolicy = QSizePolicy(
            QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.AddButton.sizePolicy().hasHeightForWidth())
        self.AddButton.setSizePolicy(sizePolicy)
        self.AddButton.setMinimumSize(QSize(self.size, self.size))
        self.AddButton.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0);")
        self.AddButton.setText("")
        self.AddButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        icon1 = QIcon("images/add.png")
        self.AddButton.setIcon(icon1)
        self.AddButton.setIconSize(QSize(75, 75))
        self.AddButton.setObjectName("AddButton")
        self.horizontalLayout.addWidget(self.AddButton)

        self.setupThread()

        # EVENTS
        # self.AddButton.clicked.connect(self.onClick2)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)
        self.Form = Form

    def setupThread(self):
        self.thread = QThread()
        self.loader = CutplanLoader()
        self.loader.moveToThread(self.thread)
        self.loader.cutplanloaded.connect(self.AddOneCP)
        self.threadconnected = False

    def onClick2(self):
        if self.threadconnected:
            self.thread.started.disconnect()
            self.threadconnected = False

    def onClick(self):
        # Ping to see if can connect, use wait cursor
        QApplication.setOverrideCursor(
            QCursor(Qt.WaitCursor))
        try:
            check_output("ping -n 1 -w 2000 "+self.host, shell=True)
        except CalledProcessError:
            QApplication.restoreOverrideCursor()
            self.ErrorBox(
                "Network Error", "Connection Failed",
                "Check internet connection to Log Scanner Server.")
            return

        QApplication.restoreOverrideCursor()
        if self.threadconnected:
            self.thread.started.disconnect()
            self.threadconnected = False
        self.AddDialog = AddCutplanDialog()
        self.AddDialog.setupUi(
            self.addData, "support/cpquery.sql", self.host)
        self.AddDialog.show()
        self.AddDialog.buttonBox.accepted.connect(self.AddCP)

    def DeleteCP(self):
        for w in self.CPProgress:
            w.deleteLater()
        for w in self.CPLabels:
            w.deleteLater()
        for w in self.CPWidgetsH:
            w.deleteLater()
        for w in self.anims:
            w.deleteLater()
        for w in self.graphics:
            w.deleteLater()
        for w in self.CPLoads:
            w.deleteLater()
        for w in self.CPWidgets:
            widget = w.parent()
            self.CPLayout.removeWidget(widget)
            w.deleteLater()
            widget.deleteLater()
            widget = None
        self.CPWidgets = []
        self.CPImg = []
        self.CPProgress = []
        self.CPLabels = []
        self.CPWidgetsH = []
        self.anims = []
        self.graphics = []
        self.CPLoads = []
        self.data = None

    def AddCP(self, addData=None):
        if addData is not None:
            # this happens when we're in popup read-only mode
            self.addData = addData

        self.DeleteCP()
        if self.addData.shape[0] == 0:
            # just return if no cutplans to add
            self.newcutplans.emit(False)
            return

        try:
            conn = sqlconnect(LogScanner)
        except sqlProgrammingError:
            conn = sqlconnect(LogScanner)

        sqlfile = "support\\cpquery2.sql"
        f = open(sqlfile, 'r')
        sqltext = f.read()
        sqltext = sqltext.replace("@CPID", "-1")
        self.data = read_sql(sqltext, conn)

        self.CPNum = self.addData.shape[0]
        QApplication.setOverrideCursor(
            QCursor(Qt.WaitCursor))
        for id in range(self.CPNum):
            self.CPLoads.append(QLabel(self))
            self.CPLoads[id].setAlignment(Qt.AlignCenter)
            self.CPLoads[id].setMinimumSize(QSize(self.size, self.size))
            self.CPLoads[id].setMaximumSize(QSize(self.size, self.size))
            movie = QMovie("images\\loading.gif")
            movie.setScaledSize(QSize(self.size, self.size))
            self.CPLoads[id].setMovie(movie)
            movie.start()
            self.CPLayout.addWidget(self.CPLoads[id])
        self.loader.id = 0
        self.loader.cutplanid = self.addData.ID[0]
        self.loader.logcount = self.addData['Log Count'][0]
        self.thread.quit()
        self.thread.wait()
        self.thread.started.connect(self.loader.loadCutplan)
        self.threadconnected = True
        self.thread.start()

        # self.SimSchedule = SimSchedule(self.data, "logs//")
        if addData is None:
            # readonly will skip this
            self.newcutplans.emit(True)
        QApplication.restoreOverrideCursor()

    def AddOneCP(self, id):
        imgfolder = "images\\cps\\"
        data = self.loader.data

        widget = QWidget(self)
        widget.setObjectName('CPW'+str(id+1))
        widget.setMinimumSize(QSize(self.size, self.size))
        widget.setMaximumSize(QSize(self.size, self.size))

        self.CPWidgetsH.append(QPushButton(widget))
        self.CPWidgetsH[id].setStyleSheet(
            "background-color: rgba(255, 255, 255, 0);")
        self.CPWidgetsH[id].setText("")
        icon = QIcon(imgfolder+"CP"+str(id+1)+"_h.png")
        self.CPWidgetsH[id].setIcon(icon)
        self.CPWidgetsH[id].setIconSize(QSize(self.size, self.size))
        self.CPWidgetsH[id].setObjectName('CPH'+str(id+1))
        self.CPWidgetsH[id].setGeometry(
            QRect(0, 0, self.size, self.size))

        self.CPWidgets.append(HoverButton(widget, id))
        self.CPWidgets[id].setMinimumSize(QSize(self.size, self.size))
        self.CPWidgets[id].setStyleSheet(
            "background-color: rgba(255, 255, 255, 0);")
        self.CPWidgets[id].setText("")
        icon = QIcon(imgfolder+"CP"+str(id+1)+".png")
        self.CPImg.append('test'+str(id+1))
        self.CPWidgets[id].setIcon(icon)
        self.CPWidgets[id].setIconSize(QSize(self.size, self.size))
        self.CPWidgets[id].setObjectName('CP'+str(id+1))
        self.CPWidgets[id].setGeometry(
            QRect(0, 0, self.size, self.size))

        self.graphics.append(QGraphicsOpacityEffect(widget))
        self.CPWidgets[id].setGraphicsEffect(self.graphics[id])
        self.graphics[id].setOpacity(1)
        self.anims.append(QPropertyAnimation(
            self.graphics[id], b"opacity"))
        self.anims[id].setDuration(400)
        self.anims[id].setEasingCurve(QEasingCurve.InOutSine)
        self.anims[id].finished.connect(self.uiUpdate)

        self.CPProgress.append(CPProgress(id, parent=widget))
        self.CPProgress[id].setObjectName('CPP'+str(id+1))
        self.CPProgress[id].setGeometry(
            QRect(0, 0, self.size, self.size))

        self.CPLabels.append(QLabel(widget))
        self.CPLabels[id].setObjectName('CPL'+str(id+1))
        self.CPLabels[id].setGeometry(QRect(10, 200, 60, 30))
        font = QFont()
        font.setPointSize(7)
        font.setBold(True)
        font.setFamily("Tahoma")
        self.CPLabels[id].setFont(font)
        self.CPLabels[id].setStyleSheet(
            "QLabel {\n"
            "	color: white;\n"
            "	background-color: rgb(0, 115, 119);\n"
            "	border-radius: 15px;\n"
            "}"
        )
        self.CPLabels[id].setAlignment(
            Qt.AlignHCenter | Qt.AlignVCenter)
        group = data.Description[0][2:4]
        length = data.Description[0][5:7]
        des = length[0]+"."+length[1]+"m "+group
        desPD = self.loader.des
        if desPD.shape[0] > 0:
            des = desPD.Description[0]
            self.CPLabels[id].setText(
                des[5:10]+"cm\n{:.1f}m".format(float(des[0:3])-0.1))
            self.CPLayout.insertWidget(id*2, widget)
            self.CPLoads[id].setVisible(False)
            self.setMinimumSize(QSize(
                self.size*(self.CPNum+1), self.size))
            self.CPProgress[id].mouseHover.connect(self.onHover)
            self.data = self.data.append(data.iloc[0], ignore_index=True)
        else:
            des = des + "-" + str(int(group)+1)
            des = des[5:10]+"cm\n{:.1f}m".format(float(des[0:3])-0.1)
            QApplication.restoreOverrideCursor()
            self.ErrorBox(
                "Input Error",
                "Log group "+des+" doesn't exist.",
                "Cutplan \""+data.Description[0]+"\" was skipped.")
            QApplication.setOverrideCursor(
                QCursor(Qt.WaitCursor))

        if id+1 < self.CPNum:
            self.thread.quit()
            self.thread.wait()
            self.loader.id = id+1
            self.loader.cutplanid = self.addData.ID[id+1]
            self.loader.logcount = self.addData['Log Count'][0]
            self.thread.start()
        else:
            self.cploadfinish.emit()

    def onHover(self, hover, id):
        self.anims[id].stop()
        if hover:
            self.anims[id].setStartValue(self.graphics[id].opacity())
            self.anims[id].setEndValue(0)
            # self.CPWidgets[id].setIcon(icon)
        else:
            self.anims[id].setStartValue(self.graphics[id].opacity())
            self.anims[id].setEndValue(1)
            # self.CPWidgets[id].setIcon(icon)
        self.anims[id].start()  # QAbstractAnimation.DeleteWhenStopped)

    def uiUpdate(self):
        for w in self.CPWidgets:
            w.update()

    def ErrorBox(self, errortxt, description, info):
        msgbox = QMessageBox(self)
        msgbox.setWindowTitle(errortxt)
        msgbox.setText(description)
        msgbox.setInformativeText(info)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("#qt_msgbox_label {font-weight: bold;}")
        msgbox.exec()

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = CutplanWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
