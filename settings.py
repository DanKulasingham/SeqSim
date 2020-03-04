from PyQt5.QtCore import QCoreApplication, Qt, QEvent
from PyQt5.QtWidgets import QCheckBox, QSizePolicy, \
    QDoubleSpinBox, QSpinBox, QGridLayout, QGroupBox, QHBoxLayout, \
    QLabel, QRadioButton, QSpacerItem, QVBoxLayout, QWidget, \
    QAbstractSpinBox, QDialogButtonBox, QPushButton
from PyQt5.QtGui import QCursor
from mysql import connector
from pandas import read_sql


# Log Gap, Default DT Settings, Bins, Line Speed, Default Cutback Settings
defaultsettings = [0.5, False, 18, 55.0, True]
defaultcutbacksettings = ['4.6m', '4.5m', '4.0m', '3.6m', '3.0m']


class SettingsWindow(QWidget):
    def eventFilter(self, object, event):
        if event.type() == QEvent.FocusIn:
            self.customspeedRB.setChecked(True)
        return super(SettingsWindow, self).eventFilter(object, event)

    def setupUi(self, Form, host='192.168.2.171'):
        Form.resize(250, 900)
        Form.setStyleSheet('font: 10pt \"Tahoma\";')
        self.host = host
        self.downtimechecked = 0
        self.default = defaultsettings
        self.defaultcutbacks = defaultcutbacksettings

        db = connector.connect(
            host=self.host, user="root", passwd="Sequal1234",
            database="simulation", use_pure=True
        )
        buttonSS = "QPushButton {\n" \
            "    background-color: ;\n" \
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0, " \
            "x2:1, y2:1, stop:0 rgba(0, 115, 119, 255), stop:1 rgb(4, 147, " \
            "131));\n" \
            "    color: white;\n" \
            "    height: 25px;\n" \
            "    border: None;\n" \
            "    border-radius: 2px;\n" \
            "    \n" \
            "    font: 11pt \"Tahoma\";\n" \
            "    width: "

        self.mainlayout = QVBoxLayout(Form)
        hlayout = QHBoxLayout()
        self.titlelabel = QLabel(Form)
        self.titlelabel.setStyleSheet(
            'font: 12pt \"Tahoma\"; font-weight: bold;')
        hlayout.addWidget(self.titlelabel)
        hspacer = QSpacerItem(
            40, 25, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hlayout.addItem(hspacer)
        self.resetbutton = QPushButton(Form)
        self.resetbutton.setStyleSheet(buttonSS+"140px;}")
        self.resetbutton.setCursor(QCursor(Qt.PointingHandCursor))
        hlayout.addWidget(self.resetbutton)
        self.mainlayout.addLayout(hlayout)
        self.hlayout = QVBoxLayout()

        # ################ #
        # GENERAL SETTINGS #
        # ################ #
        self.generalGB = QGroupBox(Form)
        self.generalGB.setStyleSheet('QGroupBox {font: 11pt \"Tahoma\";}')
        self.hlayout2 = QVBoxLayout(self.generalGB)
        self.hlayout2.setSpacing(15)

        self.gridlayout = QGridLayout()
        self.gridlayout.setHorizontalSpacing(2)
        self.loggaplabel = QLabel(self.generalGB)
        self.gridlayout.addWidget(self.loggaplabel, 0, 0, 1, 1)
        self.loggapTB = QDoubleSpinBox(self.generalGB)
        self.loggapTB.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.loggapTB.setSingleStep(0.1)
        self.loggapTB.setMinimum(0.3)
        self.loggapTB.setStyleSheet(
            'QDoubleSpinBox::disabled {color: rgb(200, 200, 200);}')
        self.gridlayout.addWidget(self.loggapTB, 0, 1, 1, 1)
        self.loggapAuto = QCheckBox(self.generalGB)
        self.gridlayout.addWidget(self.loggapAuto, 0, 2, 1, 1)
        self.numbinslabel = QLabel(self.generalGB)
        self.gridlayout.addWidget(self.numbinslabel, 1, 0, 1, 1)
        self.numbinsTB = QSpinBox(self.generalGB)
        self.numbinsTB.setMinimum(1)
        self.numbinsTB.setMaximum(40)
        self.gridlayout.addWidget(self.numbinsTB, 1, 1, 1, 1)
        vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridlayout.addItem(vspacer, 2, 0, 1, 1)

        self.hlayout2.addLayout(self.gridlayout)
        # hspacer = QSpacerItem(
        #     20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # self.hlayout2.addItem(hspacer)

        # Line speed group box
        self.linespeedGB = QGroupBox(self.generalGB)
        self.linespeedGB.setStyleSheet('QGroupBox {font: 11pt \"Tahoma\";}')
        vlayout = QVBoxLayout(self.linespeedGB)
        self.highspeedRB = QRadioButton(self.linespeedGB)
        vlayout.addWidget(self.highspeedRB)
        self.lowspeedRB = QRadioButton(self.linespeedGB)
        vlayout.addWidget(self.lowspeedRB)
        self.autospeedRB = QRadioButton(self.linespeedGB)
        vlayout.addWidget(self.autospeedRB)
        hlayout = QHBoxLayout()
        hlayout.setSpacing(0)
        self.customspeedRB = QRadioButton(self.linespeedGB)
        self.customspeedRB.setMinimumWidth(17)
        self.customspeedRB.setMaximumWidth(17)
        hlayout.addWidget(self.customspeedRB)
        self.customspeedTB = QDoubleSpinBox(self.linespeedGB)
        self.customspeedTB.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.customspeedTB.setDecimals(1)
        self.customspeedTB.setMaximum(200)
        self.customspeedTB.installEventFilter(self)
        hlayout.addWidget(self.customspeedTB)
        vlayout.addLayout(hlayout)
        vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        vlayout.addItem(vspacer)
        self.hlayout2.addWidget(self.linespeedGB)
        self.hlayout.addWidget(self.generalGB)

        # ################# #
        # DOWNTIME SETTINGS #
        # ################# #
        self.downtimeGB = QGroupBox(Form)
        self.downtimeGB.setStyleSheet('QGroupBox {font: 11pt \"Tahoma\";}')
        gridlayout = QGridLayout(self.downtimeGB)
        self.downtimeCBall = QCheckBox(self.downtimeGB)
        gridlayout.addWidget(self.downtimeCBall, 0, 0, 1, 1)
        self.downtimeCBtexts = list(
            read_sql(
                'SELECT * From DowntimeSettings Where SimID = -1;', db
            ).head()
        )[1:]
        self.downtimeCBs = []
        for i in range(len(self.downtimeCBtexts)):
            self.downtimeCBs.append(QCheckBox(self.downtimeGB))
            row = int(i/2)
            col = i % 2
            gridlayout.addWidget(self.downtimeCBs[i], row+1, col, 1, 1)
        vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        gridlayout.addItem(vspacer, row+1, 0, 1, 1)
        self.hlayout.addWidget(self.downtimeGB)

        # ################ #
        # CUTBACK SETTINGS #
        # ################ #
        self.cutbackGB = QGroupBox(Form)
        self.cutbackGB.setStyleSheet('QGroupBox {font: 11pt \"Tahoma\";}')
        gridlayout = QGridLayout(self.cutbackGB)
        self.cutbackCBtexts = list(
            read_sql(
                'SELECT * From CutbackSettings Where SimID = -1;', db
            ).head()
        )[1:]
        self.cutbackCBs = []
        for i in range(len(self.cutbackCBtexts)):
            self.cutbackCBs.append(QCheckBox(self.cutbackGB))
            row = int(i/2)
            col = i % 2
            gridlayout.addWidget(self.cutbackCBs[i], row, col, 1, 1)
        vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        gridlayout.addItem(vspacer, row+1, 0, 1, 1)
        self.hlayout.addWidget(self.cutbackGB)

        self.mainlayout.addLayout(self.hlayout)
        self.buttonbox = QDialogButtonBox(Form)
        self.buttonbox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonbox.setStyleSheet(
            "QDialogButtonBox "+buttonSS+"70px;}")
        for w in self.buttonbox.children():
            if w.metaObject().className() == "QPushButton":
                w.setCursor(QCursor(Qt.PointingHandCursor))
        self.mainlayout.addWidget(self.buttonbox)
        vspacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.mainlayout.addItem(vspacer)
        self.retranslateUi(Form)

        self.SetDefaultSettings()

        # ####### #
        # SIGNALS #
        # ####### #
        self.resetbutton.clicked.connect(self.SetDefaultSettings)
        self.loggapAuto.stateChanged.connect(self.onLogGapAuto)
        self.downtimeCBall.stateChanged.connect(self.onDowntimeAll)
        for cb in self.downtimeCBs:
            cb.stateChanged.connect(self.onDowntimeCB)
        for cb in self.cutbackCBs:
            cb.stateChanged.connect(self.onCutbackCB)
        self.numbinsTB.valueChanged.connect(self.showResetButton)
        self.loggapTB.valueChanged.connect(self.showResetButton)
        if defaultsettings[3] == 55.0:
            self.highspeedRB.toggled.connect(self.showResetButton)
        elif defaultsettings[3] == 35.0:
            self.lowspeedRB.toggled.connect(self.showResetButton)
        else:
            self.autospeedRB.toggled.connect(self.showResetButton)

    def SetDefaultSettings(self):
        if defaultsettings[3] == 55.0:
            self.highspeedRB.setChecked(True)
        elif defaultsettings[3] == 35.0:
            self.lowspeedRB.setChecked(True)
        else:
            self.autospeedRB.setChecked(True)
        if defaultsettings[0] > 0:
            self.loggapTB.setValue(defaultsettings[0])
            self.loggapAuto.setChecked(False)
        else:
            self.loggapAuto.setChecked(True)
        self.numbinsTB.setValue(defaultsettings[2])
        self.downtimeCBall.setChecked(Qt.Checked)
        self.downtimechecked = 4
        for cb in self.downtimeCBs:
            cb.setChecked(True)
        for cb in self.cutbackCBs:
            cb.setChecked(False)
        for cb in self.defaultcutbacks:
            self.cutbackCBs[self.cutbackCBtexts.index(cb)].setChecked(True)
        self.resetbutton.setVisible(False)

    def onCutbackCB(self, state):
        self.showResetButton()

    def onDowntimeAll(self, state):
        self.showResetButton()
        if state == Qt.Unchecked:
            for cb in self.downtimeCBs:
                cb.setChecked(False)
        elif state == Qt.Checked:
            for cb in self.downtimeCBs:
                cb.setChecked(True)
        elif state == Qt.PartiallyChecked and self.downtimechecked == 0:
            for cb in self.downtimeCBs:
                cb.setChecked(True)

    def onDowntimeCB(self, state):
        self.showResetButton()
        if state == Qt.Checked:
            self.downtimechecked += 1
        else:
            self.downtimechecked -= 1

        if self.downtimechecked == len(self.downtimeCBs):
            self.downtimeCBall.setCheckState(Qt.Checked)
        elif self.downtimechecked == 0:
            self.downtimeCBall.setCheckState(Qt.Unchecked)
        else:
            self.downtimeCBall.setCheckState(Qt.PartiallyChecked)

    def onLogGapAuto(self, state):
        self.showResetButton()
        self.loggapTB.setDisabled(state)

    def showResetButton(self):
        self.resetbutton.setVisible(True)

    def setupReadOnly(self):
        self.highspeedRB.setDisabled(True)
        self.lowspeedRB.setDisabled(True)
        self.autospeedRB.setDisabled(True)
        self.customspeedRB.setDisabled(True)
        self.customspeedTB.setDisabled(True)
        self.loggapAuto.setDisabled(True)
        self.loggapTB.setDisabled(True)
        self.loggapTB.setStyleSheet('')
        self.numbinsTB.setDisabled(True)
        for cb in self.downtimeCBs:
            cb.setDisabled(True)
        self.downtimeCBall.setDisabled(True)
        for cb in self.cutbackCBs:
            cb.setDisabled(True)
        self.resetbutton.setVisible(False)

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        self.titlelabel.setText(_translate('Form', 'Settings'))
        self.resetbutton.setText(_translate('Form', 'Reset to Default'))
        self.generalGB.setTitle(_translate('Form', 'General'))
        self.linespeedGB.setTitle(_translate('Form', 'Line Speed'))
        self.highspeedRB.setText(_translate('Form', '55 m/min'))
        self.lowspeedRB.setText(_translate('Form', '35 m/min'))
        self.autospeedRB.setText(_translate('Form', 'Auto'))
        self.customspeedRB.setText('')
        self.customspeedTB.setSuffix(_translate('Form', ' m/min'))
        self.loggaplabel.setText(_translate('Form', 'Log Gap: '))
        self.loggapTB.setValue(defaultsettings[0])
        self.loggapTB.setSuffix(_translate('Form', ' m'))
        self.loggapAuto.setText(_translate('Form', 'Auto'))
        self.numbinslabel.setText(_translate('Form', 'Number\nof Bins: '))
        self.downtimeGB.setTitle(_translate('Form', 'Simulated Downtime'))
        for i in range(len(self.downtimeCBtexts)):
            self.downtimeCBs[i].setText(
                _translate('Form', self.downtimeCBtexts[i]))
        self.downtimeCBall.setText(_translate('Form', 'All'))
        self.cutbackGB.setTitle(_translate('Form', 'Cutbacks'))
        for i in range(len(self.cutbackCBtexts)):
            self.cutbackCBs[i].setText(
                _translate('Form', self.cutbackCBtexts[i]))
