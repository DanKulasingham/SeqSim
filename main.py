# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtGui import QFont, QCursor, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QSizePolicy, QLabel, \
    QHBoxLayout, QWidget, QMessageBox, QLineEdit, QSpacerItem, QPushButton, \
    QApplication, QFrame, QMainWindow, QScrollArea, QStackedLayout, \
    QSplashScreen
from PyQt5.QtCore import Qt, pyqtSignal, QMetaObject, QCoreApplication, \
    QVariantAnimation, QSize
from production import SimulationPage
from history import HistoryPage
from os.path import exists as pathexists
from os import environ
from subprocess import check_output, CalledProcessError
from configparser import ConfigParser
from mysql.connector import connect as mysqlconnect
from mysql.connector.errors import DatabaseError


class NewUserPopup(QDialog):
    username = pyqtSignal(str)

    def setupUi(self, Form):
        Form.setObjectName("NewUserPopup")
        Form.resize(320, 180)
        Form.setStyleSheet("QDialog {\nbackground-color: qlineargradient("
                           "spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 "
                           "rgba(0, 115, 119, 255), stop:1 rgb(4, 147, 131, "
                           "255));\n}")

        self.vlayout = QVBoxLayout(Form)
        vspacer = QSpacerItem(
            20, 35,
            QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vlayout.addItem(vspacer)

        self.newuserlabel = QLabel(Form)
        self.newuserlabel.setObjectName("NewUserLabel")
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(14)
        font.setBold(True)
        self.newuserlabel.setFont(font)
        self.newuserlabel.setAlignment(Qt.AlignCenter)
        self.newuserlabel.setStyleSheet("color:white;\nborder:none;")
        self.vlayout.addWidget(self.newuserlabel)

        self.hlayout = QHBoxLayout()
        hspacer = QSpacerItem(
            40, 20,
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayout.addItem(hspacer)

        self.namelabel = QLabel(Form)
        self.namelabel.setObjectName("NameLabel")
        font.setBold(False)
        font.setPointSize(12)
        self.namelabel.setFont(font)
        self.namelabel.setStyleSheet("color:white;")
        self.hlayout.addWidget(self.namelabel)

        self.nametextbox = QLineEdit(Form)
        self.nametextbox.setStyleSheet("color: rgb(0,115,119);")
        self.nametextbox.setFont(font)
        self.hlayout.addWidget(self.nametextbox)

        hspacer = QSpacerItem(
            40, 20,
            QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayout.addItem(hspacer)
        self.vlayout.addLayout(self.hlayout)

        vspacer = QSpacerItem(
            20, 35,
            QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vlayout.addItem(vspacer)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

        # self.accepted.connect(self.onAccept)
        self.nametextbox.returnPressed.connect(self.onAccept)
        self.Form = Form

    def onAccept(self):
        if self.nametextbox.text() != '':
            self.username.emit(self.nametextbox.text())
            self.close()
            self.Form.done(1)

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowFlags(Qt.Widget | Qt.FramelessWindowHint)
        self.newuserlabel.setText(_translate('Form', 'New User\n'))
        self.namelabel.setText(_translate('Form', 'Name:   '))


class HoverButton(QPushButton):
    def __init__(self, parent=None, id=0):
        self.id = id
        self.selected = False
        QPushButton.__init__(self, parent)
        self.setMouseTracking(True)
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(300)
        self.anim.valueChanged.connect(self.animationEvent)
        self.a = 0
        self.ss = "border: none;"\
            "margin: 0px;"\
            "padding: 0px;"\
            "color: rgb(255, 255, 255);"\
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "\
            "y2:0, stop:0 rgba(0, 115, 119, 0), stop:0.5 rgba(0, 115, 119, "\
            "{0}), stop:1 rgba(0, 115, 119, 0));"
        self.setStyleSheet("QPushButton {" + self.ss.format(0) + "}")

    def setSelected(self, sel):
        self.selected = sel
        if sel:
            self.a = 255
            self.setStyleSheet("QPushButton {" + self.ss.format(255) + "}")
        else:
            self.leaveEvent()

    def enterEvent(self, event):
        if self.selected:
            return
        val = self.anim.currentValue()
        if val is None:
            val = self.a
        self.anim.setStartValue(val)
        self.anim.setEndValue(255)
        self.anim.start()
        self.a = 255

    def leaveEvent(self, event=None):
        if self.selected:
            return
        val = self.anim.currentValue()
        if val is None:
            val = self.a
        self.anim.setStartValue(val)
        self.anim.setEndValue(0)
        self.anim.start()
        self.a = 0

    def animationEvent(self):
        val = self.anim.currentValue()
        self.setStyleSheet("QPushButton {" + self.ss.format(val) + "}")


class Ui_MainWindow(object):
    def setupUi(self, MainWindow, username=None, userid=1,
                host='192.168.2.171', splash=None):
        self.username = username
        self.userid = userid
        self.host = host
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1280, 768)
        MainWindow.setStyleSheet("background-color: rgb(255, 255, 255);\n")

        self.popupEnabled = False

        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sideBar = QFrame(self.centralwidget)
        sizePolicy = QSizePolicy(
            QSizePolicy.Fixed,
            QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(100)
        sizePolicy.setHeightForWidth(
            self.sideBar.sizePolicy().hasHeightForWidth())
        self.sideBar.setSizePolicy(sizePolicy)
        self.sideBar.setMinimumSize(QSize(300, 768))
        self.sideBar.setStyleSheet(
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, "
            "y2:1, stop:0 rgb(0, 115, 119), "
            "stop:1 rgb(4, 147, 131));"
            )
        self.sideBar.setFrameShape(QFrame.StyledPanel)
        self.sideBar.setFrameShadow(QFrame.Raised)
        self.sideBar.setLineWidth(0)
        self.sideBar.setObjectName("sideBar")
        self.verticalLayout = QVBoxLayout(self.sideBar)
        self.verticalLayout.setContentsMargins(0, -1, 0, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QLabel(self.sideBar)
        self.label.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.label.setText("")
        self.label.setPixmap(QPixmap("images/logo.png"))
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.buttonsLayout = QVBoxLayout()
        self.buttonsLayout.setContentsMargins(-1, 20, -1, 10)
        self.buttonsLayout.setSpacing(0)
        self.buttonsLayout.setObjectName("buttonsLayout")
        self.SimulationButton = HoverButton(self.sideBar)
        self.SimulationButton.setSelected(True)
        self.SimulationButton.setMinimumSize(QSize(0, 50))
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(16)
        self.SimulationButton.setFont(font)
        self.SimulationButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.SimulationButton.setObjectName("SimulationButton")
        self.buttonsLayout.addWidget(self.SimulationButton)
        self.HistoryButton = HoverButton(self.sideBar)
        self.HistoryButton.setMinimumSize(QSize(0, 50))
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(16)
        self.HistoryButton.setFont(font)
        self.HistoryButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.HistoryButton.setObjectName("HistoryButton")
        self.buttonsLayout.addWidget(self.HistoryButton)
        # self.SettingsButton = HoverButton(self.sideBar)
        # self.SettingsButton.setMinimumSize(QSize(0, 50))
        # font = QFont()
        # font.setFamily("Tahoma")
        # font.setPointSize(16)
        # self.SettingsButton.setFont(font)
        # self.SettingsButton.setCursor(
        #     QCursor(Qt.PointingHandCursor))
        # self.SettingsButton.setObjectName("SettingsButton")
        # self.buttonsLayout.addWidget(self.SettingsButton)
        self.verticalLayout.addLayout(self.buttonsLayout)
        spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum,
            QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addWidget(self.sideBar)
        self.VScrollArea = QScrollArea(self.centralwidget)
        self.VScrollArea.setWidgetResizable(True)
        self.VScrollArea.setObjectName("VScrollArea")
        sizePolicy = QSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.MinimumExpanding)
        self.VScrollArea.setSizePolicy(sizePolicy)
        self.VScrollArea.setMinimumSize(978, 0)
        self.MainWidget = QWidget(self.VScrollArea)
        # self.MainWidget.setGeometry(QRect(0, 0, 976, 766))
        self.MainWidget.setObjectName("MainWidget")
        self.StackedLayout = QStackedLayout(self.MainWidget)
        self.SimulationWidget = QWidget(self.MainWidget)
        self.SimulationUI = SimulationPage()
        self.SimulationUI.setupUi(
            self.SimulationWidget, username, userid, host)
        self.StackedLayout.addWidget(self.SimulationWidget)
        if splash is not None:
            splash.showMessage('Adding final touches...',
                               alignment=Qt.AlignHCenter, color=Qt.white)
        self.HistoryWidget = QWidget(self.MainWidget)
        self.HistoryUI = HistoryPage()
        self.HistoryUI.setupUi(self.HistoryWidget, username, userid, host)
        self.StackedLayout.addWidget(self.HistoryWidget)
        self.PopupWidget = QWidget(self.MainWidget)
        self.PopupUI = SimulationPage()
        self.PopupUI.setupUi(self.PopupWidget, simid=0)
        self.StackedLayout.addWidget(self.PopupWidget)
        self.VScrollArea.setWidget(self.MainWidget)
        self.horizontalLayout.addWidget(self.VScrollArea)
        MainWindow.setCentralWidget(self.centralwidget)

        # EVENTS
        self.SimulationButton.clicked.connect(self.onSimulationButton)
        self.HistoryButton.clicked.connect(self.onHistoryButton)
        self.HistoryUI.table.cellClicked.connect(self.onHistoryPageLoad)
        self.PopupUI.closeButton.clicked.connect(self.onHistoryPageClose)
        self.SimulationUI.CreateNewButton.clicked.connect(self.onNewSimulation)
        # self.SettingsButton.clicked.connect(self.onSettingsButton)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)

    def onSimulationButton(self):
        if self.StackedLayout.currentIndex() != 0:
            QApplication.setOverrideCursor(
                QCursor(Qt.WaitCursor))
            # if self.StackedLayout.currentIndex() == 1:
            #     self.HistoryUI.thread.terminate()
            #     self.HistoryUI.thread.wait()
            self.SimulationButton.setSelected(True)
            self.HistoryButton.setSelected(False)
            self.StackedLayout.setCurrentIndex(0)
            QApplication.restoreOverrideCursor()
        # self.SettingsButton.setSelected(False)

    def onNewSimulation(self):
        username = self.SimulationUI.username
        userid = self.SimulationUI.userid
        host = self.SimulationUI.host

        QApplication.setOverrideCursor(
            QCursor(Qt.WaitCursor))
        self.SimulationUI.thread.quit()
        self.SimulationUI.thread.wait()
        self.SimulationUI.Cutplans.thread.quit()
        self.SimulationUI.Cutplans.thread.wait()
        self.SimulationUI = SimulationPage()
        self.SimulationUI.setupUi(
            self.SimulationWidget, username, userid, host)
        self.SimulationUI.CreateNewButton.clicked.connect(self.onNewSimulation)
        QApplication.restoreOverrideCursor()

    def onHistoryButton(self):
        self.SimulationButton.setSelected(False)
        self.HistoryButton.setSelected(True)
        if self.StackedLayout.currentIndex() == 0 and \
           self.SimulationUI.simrunning:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Simulation running...")
            msgBox.setText("Do you still want to leave the page?")
            msgBox.setStandardButtons(
                QMessageBox.Yes | QMessageBox.No)
            msgBox.setDefaultButton(QMessageBox.No)
            msgBox.setIcon(QMessageBox.Warning)
            self.HistoryButton.setSelected(True)
            r = msgBox.exec()

            if r == QMessageBox.No:
                self.HistoryButton.setSelected(False)
                if self.StackedLayout.currentIndex() == 0:
                    self.SimulationButton.setSelected(True)
                return

        QApplication.setOverrideCursor(
            QCursor(Qt.WaitCursor))
        # if self.StackedLayout.currentIndex() == 1:
        #     self.HistoryUI.thread.terminate()
        #     self.HistoryUI.thread.wait()
        if self.popupEnabled:
            self.StackedLayout.setCurrentIndex(2)
        else:
            self.StackedLayout.setCurrentIndex(1)
        QApplication.restoreOverrideCursor()
        # self.SettingsButton.setSelected(False)

    def setUserID(self, name):
        self.username = name

    def LoadConfig(self):
        config = ConfigParser()
        config.read('config.ini')
        self.MainWidget.username = config['GENERAL']['username']
        self.MainWidget.userid = config['GENERAL']['userid']
        self.MainWidget.host = config['CONNECTION']['host']

    def retranslateUi(self, MainWindow):
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate(
            "MainWindow",
            "SeqSim — Sequal Simulation Software"))
        self.SimulationButton.setText(_translate("MainWindow", "Simulation"))
        self.HistoryButton.setText(_translate("MainWindow", "History"))
        # self.SettingsButton.setText(_translate("MainWindow", "Settings"))

    def onHistoryPageLoad(self, r, c):
        self.PopupUI.simid = self.HistoryUI.loader.data['SimID'][r]
        self.PopupUI.setupReadOnly()
        self.popupEnabled = True
        self.StackedLayout.setCurrentIndex(2)

    def onHistoryPageClose(self):
        self.popupEnabled = False
        self.PopupUI.Cutplans.thread.quit()
        self.PopupUI.Cutplans.thread.wait()
        self.PopupUI.Cutplans.thread.started.disconnect()
        self.PopupUI.Cutplans.threadconnected = False
        self.StackedLayout.setCurrentIndex(1)


if __name__ == "__main__":
    import sys
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)

    pixmap = QPixmap('images\\splash.png')
    splash = QSplashScreen(pixmap)
    splash.show()
    app.processEvents()

    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    app.setWindowIcon(QIcon('images\\icon.ico'))
    import ctypes
    myappid = u'Sequal.SimulationSoftware'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    splash.showMessage('Checking network connection...',
                       alignment=Qt.AlignHCenter, color=Qt.white)
    app.processEvents()
    try:
        db = mysqlconnect(
            host="192.168.2.171", user="root", passwd="Sequal1234",
            database="simulation", connect_timeout=2
        )
        check_output("ping -n 1 -w 2000 192.168.3.55", shell=True)
    except (CalledProcessError, DatabaseError):
        msgbox = QMessageBox(MainWindow)
        msgbox.setWindowTitle('Network Error')
        msgbox.setText('Network connection required.')
        msgbox.setInformativeText('Could not connect to server. '
                                  'Check internet connection and '
                                  'try again.')
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.setIcon(QMessageBox.Critical)
        msgbox.setStyleSheet("#qt_msgbox_label {font-weight: bold;}")
        msgbox.show()
        sys.exit(msgbox.exec())

    splash.showMessage('Checking user settings...',
                       alignment=Qt.AlignHCenter, color=Qt.white)
    app.processEvents()
    if not pathexists('config.ini'):
        # This bit is to set up a new user account if necessary
        Dialog = QDialog()
        NewUserPopup = NewUserPopup()
        NewUserPopup.setupUi(Dialog)
        NewUserPopup.username.connect(ui.setUserID)
        Dialog.show()
        r = Dialog.exec_()

        if r == 0:
            sys.exit()

        username = ui.username
        host = '192.168.2.171'

        db = mysqlconnect(
            host=host, user="root", passwd="Sequal1234",
            database="simulation"
        )
        db.autocommit = True
        query = "SELECT UserID From Users Where " \
            "Username = \'" + username + "\'"
        cursor = db.cursor()
        cursor.execute(query)
        temp = cursor.fetchone()

        if temp is None:
            query = "INSERT INTO users (Username) VALUES " \
                "(\'" + username + "\');"
            cursor.execute(query)
            cursor.execute("SELECT LAST_INSERT_ID();")
            temp = cursor.fetchone()

        (userid, ) = temp

        config = ConfigParser()
        config['GENERAL'] = {
                'username': username,
                'userid': userid
        }
        config['CONNECTION'] = {
                'host': host
        }
        with open('config.ini', 'w') as f:
            config.write(f)
    else:
        config = ConfigParser()
        config.read('config.ini')
        username = config['GENERAL']['username']
        userid = config['GENERAL']['userid']
        host = config['CONNECTION']['host']

    splash.showMessage('Making everything look pretty...',
                       alignment=Qt.AlignHCenter, color=Qt.white)
    app.processEvents()
    ui.setupUi(MainWindow, username, userid, host, splash=splash)
    MainWindow.show()
    splash.finish(MainWindow)

    sys.exit(app.exec_())
