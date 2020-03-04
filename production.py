# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simulation.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QToolButton, \
    QLabel, QLineEdit, QSpacerItem, QSizePolicy, QDialogButtonBox, QFrame, \
    QScrollArea, QApplication, QStackedLayout
from PyQt5.QtCore import QThread, QSize, Qt, QTimer, QMetaObject, \
    QCoreApplication
from PyQt5.QtGui import QCursor, QIcon
from cutplan import CutplanWidget
from results import ResultsWidget
from os import getcwd
from pandas import DataFrame, read_sql
from mysql import connector
from addWindow import AddCutplanDialog
from settings import SettingsWindow


class SimulationPage(QWidget):
    def setupUi(self, Form, username=None, userid=1, host='192.168.2.171',
                simid=None, reset=False):
        self.host = host
        self.username = username
        self.userid = userid
        self.simid = simid
        self.readonly = (simid is not None)
        self.showsettings = False
        self.currentindex = 0
        self.usedefaultsettings = True

        self.db = connector.connect(
            host=self.host, user="root", passwd="Sequal1234",
            database="simulation", use_pure=True
        )
        self.db.autocommit = True
        self.simrunning = False
        # self.esrunning = False
        if not reset:
            self.thread = None
            self.thread = QThread()
        self.cppath = getcwd()+"\\cutplans\\"
        self.logpath = getcwd()+"\\logs\\"
        self.shifts = 2
        self.simShift = 1
        index = []
        for i in range(1, self.shifts+1):
            index.append(str(i))
        index.append("Total")
        cols = ["RunTime", "LogsCut", "Production", "LogVolume",
                "Recovery", "LogRate", "Uptime", "MSLDT", "BSLDT", "TSLDT",
                "SawdustVol"]
        self.results = DataFrame(index=index, columns=cols)

        # self.OpenExtendSim()

        Form.setObjectName("Form")
        Form.resize(900, 750)
        Form.setMinimumSize(QSize(900, 750))
        Form.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                           "color: rgb(0, 115, 119);")
        if Form.layout() is not None:
            QWidget().setLayout(Form.layout())
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")

        ss = \
            """
            QToolButton {
                background-color: qlineargradient(spread:pad,
                    x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 115,
                    119, 255), stop:1 rgb(4, 147, 131));
                color: white;
                border: None;
                border-radius: 2px;
                font: 11pt "Tahoma";
                padding: 5px;
                margin-right: 20px;
            }
            """
        self.detailsLayout = QHBoxLayout()
        self.closeButton = QToolButton(Form)
        self.closeButton.setObjectName("closeButton")
        self.closeButton.setStyleSheet(ss)
        self.closeButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        icon1 = QIcon("images/close.png")
        self.closeButton.setIcon(icon1)
        self.closeButton.setVisible(self.readonly)
        self.detailsLayout.addWidget(self.closeButton)
        self.nameLabel = QLabel(Form)
        self.nameLabel.setText("Name: ")
        self.nameLabel.setStyleSheet(
            "QLabel {"
            "background: none; font: 15pt \"Tahoma\";font-weight: bold;"
            "}")
        self.detailsLayout.addWidget(self.nameLabel)
        self.nameTextbox = QLineEdit(Form)
        self.nameTextbox.setText("Simulation")
        self.nameTextbox.setStyleSheet(
            "QLineEdit {\n"
            "background: none; font: 15pt \"Tahoma\";"
            "border: 1px solid rgb(0,115,119);\n"
            "}\n"
            "QLineEdit:disabled {border: none;}")
        self.detailsLayout.addWidget(self.nameTextbox)
        h = self.nameTextbox.size().height()
        self.closeButton.setMinimumSize(QSize(h, h))
        self.closeButton.setIconSize(QSize(h-10, h-10))
        self.PlayButton = QToolButton(Form)
        self.PlayButton.setObjectName("PlayButton")
        self.PlayButton.setStyleSheet(ss)
        self.PlayButton.setMinimumSize(QSize(h, h))
        self.PlayButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        icon1 = QIcon("images/play.png")
        self.PlayButton.setIcon(icon1)
        self.PlayButton.setIconSize(QSize(h-10, h-10))
        self.PlayButton.setVisible(False)
        self.detailsLayout.addWidget(self.PlayButton)
        hSpacer = QSpacerItem(
            40, 20,
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.detailsLayout.addItem(hSpacer)
        self.CreateNewButton = QToolButton(Form)
        self.CreateNewButton.setObjectName("CreateNewButton")
        self.CreateNewButton.setStyleSheet(ss)
        self.CreateNewButton.setMinimumSize(QSize(h, h))
        self.CreateNewButton.setText("Create New")
        self.CreateNewButton.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon)
        icon1 = QIcon("images/new.png")
        self.CreateNewButton.setIcon(icon1)
        self.CreateNewButton.setIconSize(QSize(h-10, h-10))
        self.CreateNewButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.CreateNewButton.setVisible(False)
        self.detailsLayout.addWidget(self.CreateNewButton)
        self.SettingsButton = QToolButton(Form)
        self.SettingsButton.setObjectName("SettingsButton")
        self.SettingsButton.setStyleSheet(ss)
        self.SettingsButton.setMinimumSize(QSize(h, h))
        self.SettingsButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        icon1 = QIcon("images/settings.png")
        self.SettingsButton.setIcon(icon1)
        self.SettingsButton.setIconSize(QSize(h-10, h-10))
        self.detailsLayout.addWidget(self.SettingsButton)
        self.detailsLayout.setSpacing(5)
        self.verticalLayout.addLayout(self.detailsLayout)

        self.mainhorilayout = QHBoxLayout()
        self.ResultsArea = QScrollArea(Form)
        self.ResultsWidget = ResultsWidget()
        self.ResultsWidget.setupUi(self.ResultsArea)
        self.ResultsWidget.setObjectName("ResultsWidget")
        self.ResultsArea.setWidget(self.ResultsWidget)
        self.ResultsArea.setWidgetResizable(True)
        self.ResultsArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.ResultsArea.setFrameShape(QFrame.NoFrame)
        self.mainhorilayout.addWidget(self.ResultsArea)

        self.StackedWidget = QWidget(Form)
        self.StackedLayout = QStackedLayout(self.StackedWidget)
        self.CutplanArea = QScrollArea(self.StackedWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.CutplanArea.sizePolicy().hasHeightForWidth())
        self.CutplanArea.setSizePolicy(sizePolicy)
        self.CutplanArea.setMinimumSize(QSize(0, 250))
        self.CutplanArea.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # self.CutplanArea.setSizeAdjustPolicy(
        #    QAbstractScrollArea.AdjustToContents)
        self.CutplanArea.setWidgetResizable(True)
        self.CutplanArea.setFrameShape(QFrame.NoFrame)
        self.CutplanArea.setObjectName("CutplanArea")
        self.CPWidget = QWidget()
        self.Cutplans = CutplanWidget()
        self.Cutplans.setupUi(self.CPWidget)
        self.Cutplans.setObjectName("Cutplans")
        self.CutplanArea.setWidget(self.CPWidget)
        self.StackedLayout.addWidget(self.CutplanArea)
        self.StackedLayout.setSpacing(0)
        self.StackedLayout.setContentsMargins(0, 0, 0, 0)
        self.StackedWidget.setStyleSheet('background-color:rhba(0,0,0,0);')
        self.StackedWidget.setMaximumWidth(250)
        self.AddWindow = AddCutplanDialog(self.StackedWidget)
        self.AddWindow.setupUi(None, "support/cpquery.sql", self.Cutplans.host)
        self.StackedLayout.addWidget(self.AddWindow)
        self.SettingsWidget = QWidget(self.StackedWidget)
        self.SettingsUI = SettingsWindow(self.SettingsWidget)
        self.SettingsUI.setupUi(self.SettingsWidget)
        self.GetDefaultSettings()
        self.StackedLayout.addWidget(self.SettingsWidget)
        self.StackedLayout.setCurrentIndex(0)
        self.mainhorilayout.addWidget(self.StackedWidget)

        self.verticalLayout.addLayout(self.mainhorilayout)
        self.verticalLayout.setContentsMargins(50, 30, 50, 30)
        self.verticalLayout.setSpacing(50)
        self.timer = QTimer(self)
        self.timer.setInterval(100)

        self.timer.timeout.connect(self.UpdateGUI)
        self.PlayButton.clicked.connect(self.OnPlay)
        self.SettingsButton.clicked.connect(self.OnSettings)
        self.Cutplans.newcutplans.connect(self.ThreadSetup)
        self.Cutplans.AddButton.clicked.connect(self.AddClick)
        self.Cutplans.cploadfinish.connect(self.showPlayButton)
        self.AddWindow.buttonBox.rejected.connect(self.AddReject)
        self.AddWindow.buttonBox.accepted.connect(self.AddAccept)
        self.SettingsUI.buttonbox.accepted.connect(self.GetSettings)
        self.SettingsUI.buttonbox.rejected.connect(self.SendSettings)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))

    def ThreadSetup(self, show):
        self.PlayButton.setVisible(False)
        self.cpid = 0
        self.cpfinish = False
        for i in range(self.results.shape[0]):
            for j in range(self.results.shape[1]):
                self.results.iloc[i, j] = 0

    def showPlayButton(self):
        if not self.readonly:
            self.PlayButton.setVisible(True)

    def AddClick(self):
        self.Cutplans.onClick2()
        if self.Cutplans.addData is not None:
            self.AddWindow.addData = self.Cutplans.addData
        else:
            self.AddWindow.addData = DataFrame(
                columns=['ID', 'Log Count', 'Description'])
        self.AddWindow.onDateChange()
        self.AddWindow.RTVSetUp()
        self.StackedLayout.setCurrentIndex(1)
        self.currentindex = 1

    def AddReject(self):
        self.StackedLayout.setCurrentIndex(0)
        self.currentindex = 0

    def AddAccept(self):
        self.Cutplans.addData = self.AddWindow.addData
        self.StackedLayout.setCurrentIndex(0)
        self.currentindex = 0
        self.Cutplans.AddCP()

    def OnPlay(self):
        self.PlayButton.setVisible(False)
        self.Cutplans.AddButton.setVisible(False)
        self.nameTextbox.setDisabled(True)
        self.simrunning = True
        self.cpfinish = False
        self.SendData()
        self.timer.start()
        # if self.esrunning:
        #     # self.esa.RunSim()
        #     self.timer.start()

    def SendData(self):
        try:
            cursor = self.db.cursor()
        except connector.Error:
            self.db = connector.connect(
                host=self.host, user="root", passwd="Sequal1234",
                database="simulation", use_pure=True
            )
            self.db.autocommit = True
            cursor = self.db.cursor()

        f = open('support\\initResults.sql', 'r')
        query = f.read()
        cursor.execute(query)

        # Simulations query
        query = "INSERT INTO simulations (Name, UserID) VALUES " \
            "(\'" + self.nameTextbox.text() + "\', " + str(self.userid) + ");"

        cursor.execute(query)
        cursor.execute("SELECT LAST_INSERT_ID();")
        (sid, ) = cursor.fetchone()
        self.simid = sid

        # check for downtime setting
        if sum(self.downtime_setting) == 0:
            # all downtime off
            dt = 0
        elif sum(self.downtime_setting) == len(self.downtime_setting):
            # all downtime on
            dt = 1
        else:
            # custom downtime so insert downtime into downtimesettings
            dt = 2
            temp = self.SettingsUI.downtimeCBtexts.copy()
            temp.insert(0, 'SimID')
            tstr = str(temp).replace('\'', '').replace('[', '(').replace(
                ']', ')')
            query = "INSERT INTO DowntimeSettings " + tstr
            temp = self.downtime_setting.copy()
            temp.insert(0, self.simid)
            tstr = str(temp).replace('[', '(').replace(']', ')')
            query = query + " VALUES " + tstr + ";"
            cursor.execute(query)

        # check for cutback default setting
        defcb = self.SettingsUI.defaultcutbacks
        cbtext = self.SettingsUI.cutbackCBtexts
        cb = True
        for tstr in defcb:
            if not self.cutback_setting[cbtext.index(tstr)]:
                cb = False
        if cb and sum(self.cutback_setting) == len(defcb):
            cb = 1
        else:
            cb = 0
            temp = cbtext.copy()
            temp.insert(0, 'SimID')
            tstr = str(temp).replace('\'', '`').replace('[', '(').replace(
                ']', ')')
            query = "INSERT INTO CutbackSettings " + tstr
            temp = self.cutback_setting.copy()
            temp.insert(0, self.simid)
            tstr = str(temp).replace('[', '(').replace(']', ')')
            query = query + " VALUES " + tstr + ";"
            cursor.execute(query)

        # SimHistory Query
        f = open('support\\simHistQuery.sql', 'r')
        sqltext = f.read()
        query = sqltext.replace('@SimID', str(self.simid))
        query = query.replace('@Name', str(self.nameTextbox.text()))
        query = query.replace('@UserID', str(self.userid))
        query = query.replace('@LogGap', str(self.loggap_setting))
        query = query.replace('@Downtime', str(dt))
        query = query.replace('@NumBins', str(self.numbins_setting))
        query = query.replace('@LineSpeed', str(self.linespeed_setting))
        query = query.replace('@Cutbacks', str(cb))
        cursor.execute(query)

        # Cutplans Query
        f = open('support\\simQuery.sql', 'r')
        sqltext = f.read()
        for i in range(self.Cutplans.addData.shape[0]):
            sqltext_full = sqltext.replace("@SimID", str(sid))
            sqltext_full = sqltext_full.replace("@CutplanID", str(
                self.Cutplans.addData.ID[i]))
            sqltext_full = sqltext_full.replace("@Description", str(
                self.Cutplans.addData.Description[i]))
            sqltext_full = sqltext_full.replace("@NumLogs", str(
                self.Cutplans.addData['Log Count'][i]))

            cursor.execute(sqltext_full)

    def GetDefaultSettings(self):
        self.loggap_setting = self.SettingsUI.default[0]
        self.downtime_setting = []
        for cb in self.SettingsUI.downtimeCBs:
            self.downtime_setting.append(cb.isChecked())
        self.numbins_setting = self.SettingsUI.default[2]
        self.linespeed_setting = self.SettingsUI.default[3]
        self.cutback_setting = []
        for cb in self.SettingsUI.cutbackCBs:
            self.cutback_setting.append(cb.isChecked())

    def GetSettings(self):
        s = self.SettingsUI
        if s.loggapAuto.isChecked():
            self.loggap_setting = -1
        else:
            self.loggap_setting = s.loggapTB.value()
        self.downtime_setting = []
        for cb in s.downtimeCBs:
            self.downtime_setting.append(cb.isChecked())
        self.numbins_setting = s.numbinsTB.value()
        if s.highspeedRB.isChecked():
            self.linespeed_setting = 55.0
        elif s.lowspeedRB.isChecked():
            self.linespeed_setting = 35.0
        elif s.autospeedRB.isChecked():
            self.linespeed_setting = -1.0
        else:
            self.linespeed_setting = s.customspeedTB.value()
        self.cutback_setting = []
        for cb in s.cutbackCBs:
            self.cutback_setting.append(cb.isChecked())

        self.usedefaultsettings = not s.resetbutton.isVisible()

        self.showsettings = False
        speed = int(self.linespeed_setting)
        if speed == -1:
            speed = 55
        self.Cutplans.speedsetting = speed
        self.Cutplans.onClick2()
        self.Cutplans.AddCP()
        self.StackedLayout.setCurrentIndex(self.currentindex)

    def SendSettings(self):
        s = self.SettingsUI
        if self.loggap_setting == -1:
            s.loggapAuto.setChecked(True)
        else:
            s.loggapAuto.setChecked(False)
            s.loggapTB.setValue(self.loggap_setting)
        for i in range(len(s.downtimeCBs)):
            s.downtimeCBs[i].setChecked(self.downtime_setting[i])
        s.numbinsTB.setValue(self.numbins_setting)
        if self.linespeed_setting == 55.0:
            s.highspeedRB.setChecked(True)
        elif self.linespeed_setting == 35.0:
            s.lowspeedRB.setChecked(True)
        elif self.linespeed_setting == -1.0:
            s.autospeedRB.setChecked(True)
        else:
            s.customspeedRB.setChecked(True)
            s.customspeedTB.setValue(self.linespeed_setting)
        for i in range(len(s.cutbackCBs)):
            s.cutbackCBs[i].setChecked(self.cutback_setting[i])

        if self.usedefaultsettings:
            s.resetbutton.setVisible(False)

        self.showsettings = False
        self.StackedLayout.setCurrentIndex(self.currentindex)

    def OnSettings(self):
        if not self.showsettings:
            self.SettingsUI.resetbutton.setVisible(not self.usedefaultsettings)
            self.StackedLayout.setCurrentIndex(2)
            self.showsettings = True

    def UpdateGUI(self):
        if not self.cpfinish:
            f = open('support\\cpProgress.sql', 'r')
            sqltext = f.read().replace('@SimID', str(self.simid))
            try:
                cursor = self.db.cursor()
            except connector.Error:
                self.db = connector.connect(
                    host=self.host, user="root", passwd="Sequal1234",
                    database="simulation", use_pure=True
                )
                self.db.autocommit = True
                cursor = self.db.cursor()
            complete = 0
            for i in range(self.Cutplans.addData.shape[0]):
                query = sqltext.replace(
                    '@CPID', str(self.Cutplans.addData.ID[i]))
                cursor.execute(query)
                (v, ) = cursor.fetchone()
                self.Cutplans.CPProgress[i].setValue(v)
                if v >= 100:
                    complete += 1
            if complete == self.Cutplans.addData.shape[0]:
                self.cpfinish = True
        else:
            f = open('support\\getResults.sql', 'r')
            sqltext = f.read()
            self.results = read_sql(sqltext, self.db)
            self.ResultsWidget.updateResults(self.results)
            if self.results['RunTime'][2] >= 17.66:
                self.timer.stop()
                self.simrunning = False
                self.setupPostSimulation()

    def setupPostSimulation(self):
        self.Cutplans.AddButton.setVisible(False)
        self.nameTextbox.setDisabled(True)
        self.CreateNewButton.setVisible(True)

        ss = "    background-color: ;\n" \
             "    background-color: qlineargradient(spread:pad, x1:0, y1:0, " \
             "x2:1, y2:1, stop:0 rgba(0, 115, 119, 255), stop:1 rgb(4, 147, " \
             "131));\n" \
             "    color: white;\n" \
             "    height: 25px;\n" \
             "    border: None;\n" \
             "    border-radius: 2px;\n" \
             "    \n" \
             "    font: 11pt \"Tahoma\";\n" \
             "    width: 70px;"

        # SETTINGS READ ONLY
        self.SettingsUI.buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel)
        for w in self.SettingsUI.buttonbox.children():
            if w.metaObject().className() == "QPushButton":
                w.setCursor(QCursor(Qt.PointingHandCursor))
                w.setStyleSheet(ss)
        self.SettingsUI.setupReadOnly()
        self.CheckCPErrors()

    def setupReadOnly(self, loadcp=True):
        self.closeButton.setVisible(True)
        self.Cutplans.AddButton.setVisible(False)
        qry = "SELECT * FROM simulation.fullresults Where SimID = "+str(
            self.simid)
        data = read_sql(qry, self.db)
        self.nameTextbox.setText(data["SimName"][0])
        self.nameTextbox.setDisabled(True)
        qry = "SELECT CutplanID as ID, NumLogs as \"Log Count\" From " + \
              "cutplans WHERE SimID = " + str(self.simid)

        self.results = data.iloc[:, 3:15].copy()
        self.results.columns = ['RunTime', 'LogsCut', 'Production',
                                'LogVolume', 'Recovery', 'LogRate', 'Uptime',
                                'MSLDT', 'BSLDT', 'TSLDT', 'Sawdust', 'Shift']
        self.results.loc[
            self.results.index[0], 'Shift'] = self.results.shape[0]
        self.results = self.results.sort_values(by=['Shift'])
        self.results['Sawdust'] = self.results['Sawdust'] / \
            self.results['LogVolume']
        self.ResultsWidget.updateResults(self.results)

        if loadcp:
            cpdata = read_sql(qry, self.db)
            self.Cutplans.AddCP(addData=cpdata, errors=self.CheckCPErrors())

        qry = "SELECT * From SimHistory Where SimID = " + str(self.simid) + ";"
        settings = read_sql(qry, self.db)
        self.loggap_setting = settings.LogGap[0]
        dt = settings.Downtime[0]
        if dt == 0:
            self.downtime_setting = []
            for i in range(len(self.SettingsUI.downtimeCBs)):
                self.downtime_setting.append(False)
        elif dt == 1:
            self.downtime_setting = []
            for i in range(len(self.SettingsUI.downtimeCBs)):
                self.downtime_setting.append(True)
        else:
            qry = "SELECT * FROM DowntimeSettings Where SimID = " + str(
                self.simid) + ";"
            dt = read_sql(qry, self.db)
            for i in range(len(self.SettingsUI.downtimeCBs)):
                x = (dt.iloc[0, i+1] == 1)
                self.SettingsUI.downtimeCBs[i].setChecked(x)
        self.SettingsUI.numbinsTB.setValue(settings.NumBins[0])
        if settings.LineSpeed[0] == 55.0:
            self.SettingsUI.highspeedRB.setChecked(True)
        elif settings.LineSpeed[0] == 35.0:
            self.SettingsUI.lowspeedRB.setChecked(True)
        elif settings.LineSpeed[0] == -1.0:
            self.SettingsUI.autospeedRB.setChecked(True)
        else:
            self.SettingsUI.customspeedRB.setChecked(True)
            self.SettingsUI.customspeedTB.setValue(settings.LineSpeed[0])
        if settings.Downtime[0] == 0:
            qry = "SELECT * FROM CutbackSettings Where SimID = " + str(
                self.simid) + ";"
            cb = read_sql(qry, self.db)
            for i in range(len(self.SettingsUI.downtimeCBs)):
                x = (cb.iloc[0, i+1] == 1)
                self.SettingsUI.downtimeCBs[i].setChecked(x)

        self.SettingsUI.buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel)
        for w in self.SettingsUI.buttonbox.children():
            if w.metaObject().className() == "QPushButton":
                w.setCursor(QCursor(Qt.PointingHandCursor))
        self.SettingsUI.setupReadOnly()

    def CheckCPErrors(self):
        with open('support\\cpErrors.sql', 'r') as f:
            query = f.read().replace('@SimID', str(self.simid))
        cperrors = read_sql(query, self.db)

        return cperrors


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = SimulationPage()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
    ui.esa.Quit()
