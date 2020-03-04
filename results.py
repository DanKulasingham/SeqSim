# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'results.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtCore import QCoreApplication, pyqtSignal, QMetaObject, Qt, \
    QVariantAnimation, QEasingCurve, QEvent, QPropertyAnimation
from PyQt5.QtWidgets import QProgressBar, QWidget, QSizePolicy, QFrame, \
    QLabel, QApplication, QGridLayout, QVBoxLayout, QSpacerItem, QHBoxLayout, \
    QScrollArea
from PyQt5.QtGui import QFont, QCursor
from seqsim.classes import QtPyChart


class ResultsBar(QProgressBar):
    def __init__(self, id, targets, parent=None):
        super(ResultsBar, self).__init__(parent)
        self.a = False
        self.id = id
        self.setObjectName(id)
        self.targets = targets
        self.setValue2(targets[1]/2)
        self.setTextVisible(False)
        self.actval = 0
        if parent is None:
            self.anim = QVariantAnimation(self)
        else:
            self.anim = QVariantAnimation(parent)
        self.anim.setStartValue(0)
        self.anim.setEasingCurve(QEasingCurve.OutBounce)
        self.anim.currentLoopChanged.connect(self.animationEvent)
        self.anim.finished.connect(self.animFinished)

    def setValue2(self, val, update=True):
        v = (val/self.targets[1])*100
        if v > 99:
            v = 100
        self.setProperty("value", v)
        self.setValue(v)
        self.updateStyleSheet(v)

    def animationEvent(self):
        v = self.anim.currentValue()
        self.setValue2(v)

    def setActual(self, val):
        self.actval = (val/self.targets[1])*100
        if self.actval > 99:
            self.actval = 100
        if self.a:
            self.anim.setEndValue(self.actval)
        else:
            self.setValue2(val)

    def startAnimation(self):
        self.anim.setStartValue(0)
        self.anim.setEndValue(self.actval)
        self.anim.setDuration(20*self.actval)
        self.anim.start()
        self.a = True

    def animFinished(self):
        self.a = False
        return

    def updateStyleSheet(self, val):
        ss = \
            "#@ID {\n" \
            "    background-color: rgba(0,0,0,0);\n" \
            "    border: none;\n" \
            "}\n" \
            "#@ID::chunk {\n" \
            "    background-color: qlineargradient(spread:pad, x1:0, " \
            "y1:0, x2:0, y2:1, stop:0 @Colour1, stop:1 "  \
            "@Colour2);\n" \
            "    width: 1px;\n" \
            "    border: none;\n" \
            "}"
        if val == 100:
            col1 = "rgb(150,220,90)"
            col2 = "rgb(160,230,100)"
        elif val < (self.targets[0]/self.targets[1])*100:
            col1 = "rgb(250,70,65)"
            col2 = "rgb(255,80,75)"
        else:
            col1 = "rgb(245,170,40)"
            col2 = "rgb(255,180,50)"
        ss = ss.replace(
            "@Colour1", col1
        ).replace(
            "@Colour2", col2
        ).replace("@ID", self.id)
        self.setStyleSheet(ss)


class DataWidget(QWidget):
    def __init__(self, parent=None, mult=1, results=None):
        super(DataWidget, self).__init__(parent)
        if results is None:
            results = [8.0, 2150, 300.0, 638.3, 0.47, 4.48, 0.5, 0.1, 0.2, 0.2,
                       0.12]
        self.mult = mult
        self.prod = results[2]
        self.prodTarget = (375.0*mult, 475.0*mult)
        self.logscut = results[1]
        self.logscutTarget = (2100.0*mult, 2400.0*mult)
        self.logvol = results[3]
        self.logvolTarget = (700.0*mult, 800.0*mult)
        self.runtime = results[0]
        self.runtimeTarget = ((530/120)*mult, (530/60)*mult)
        self.recovery = results[4]
        self.recoveryTarget = (0.45, 0.5)
        self.uptime = results[6]
        self.uptimeTarget = (0.5, 0.62)
        self.msldt = results[7]
        self.bsldt = results[8]
        self.tsldt = results[9]
        self.sawdust = results[10]
        self.setupUi(parent)

    def setupUi(self, Form):
        self.setMinimumSize(0, 400)
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )
        self.setSizePolicy(sizePolicy)
        self.setStyleSheet(
            "QLabel {"
            "background: none; font: 12pt \"Tahoma\";font-weight: bold;"
            "}")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setVerticalSpacing(25)
        self.LogsCutLabel = QLabel(self)
        self.LogsCutLabel.setObjectName("LogsCutLabel")
        self.gridLayout.addWidget(self.LogsCutLabel, 0, 1, 1, 1)
        self.LogsCutBar = ResultsBar("LogsCutBar", self.logscutTarget, self)
        self.gridLayout.addWidget(self.LogsCutBar, 0, 2, 1, 1)
        self.LogVolumeBar = ResultsBar("LogVolumeBar", self.logvolTarget, self)
        self.gridLayout.addWidget(self.LogVolumeBar, 1, 2, 1, 1)
        spacerItem = QSpacerItem(
            40, 20,
            QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 4, 1, 1)
        self.ProductionValue = QLabel(self)
        self.ProductionValue.setObjectName("ProductionValue")
        self.gridLayout.addWidget(self.ProductionValue, 2, 3, 1, 1)
        self.LogVolumeLabel = QLabel(self)
        self.LogVolumeLabel.setObjectName("LogVolumeLabel")
        self.gridLayout.addWidget(self.LogVolumeLabel, 1, 1, 1, 1)
        self.RuntimeValue = QLabel(self)
        self.RuntimeValue.setObjectName("RuntimeValue")
        self.gridLayout.addWidget(self.RuntimeValue, 3, 3, 1, 1)
        self.ProductionLabel = QLabel(self)
        self.ProductionLabel.setObjectName("ProductionLabel")
        self.gridLayout.addWidget(self.ProductionLabel, 2, 1, 1, 1)
        self.LogsCutValue = QLabel(self)
        self.LogsCutValue.setObjectName("LogsCutValue")
        self.gridLayout.addWidget(self.LogsCutValue, 0, 3, 1, 1)
        self.LogVolumeValue = QLabel(self)
        self.LogVolumeValue.setObjectName("LogVolumeValue")
        self.gridLayout.addWidget(self.LogVolumeValue, 1, 3, 1, 1)
        self.RuntimeLabel = QLabel(self)
        self.RuntimeLabel.setObjectName("RuntimeLabel")
        self.gridLayout.addWidget(self.RuntimeLabel, 3, 1, 1, 1)
        self.ProductionBar = ResultsBar("ProductionBar", self.prodTarget, self)
        self.gridLayout.addWidget(self.ProductionBar, 2, 2, 1, 1)
        self.RuntimeBar = ResultsBar("RuntimeBar", self.runtimeTarget, self)
        self.gridLayout.addWidget(self.RuntimeBar, 3, 2, 1, 1)
        spacerItem1 = QSpacerItem(
            40, 20,
            QSizePolicy.Preferred,
            QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(0, 20, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        dict = {
            'Recovery': self.recovery,
            'Chip': (1-self.recovery-self.sawdust),
            'Sawdust': self.sawdust
        }
        self.recoveryWidget = QtPyChart(dict, self.recoveryTarget, parent=self)
        self.recoveryWidget.setObjectName("recoveryWidget")
        self.horizontalLayout.addWidget(self.recoveryWidget)
        dict = {
            'Uptime': self.uptime,
            'MSL': self.msldt,
            'BSL': self.bsldt,
            'TSL': self.tsldt
        }
        self.uptimeWidget = QtPyChart(dict, self.uptimeTarget, parent=self)
        self.uptimeWidget.setObjectName("uptimeWidget")
        self.horizontalLayout.addWidget(self.uptimeWidget)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setContentsMargins(0, 20, 0, 20)
        self.setLayout(self.verticalLayout)

        self.LogsCutBar.setActual(self.logscut)
        self.LogVolumeBar.setActual(self.logvol)
        self.RuntimeBar.setActual(self.runtime)
        self.ProductionBar.setActual(self.prod)

        self.setupAnimation()

        self.setWidgetText()
        # QMetaObject.connectSlotsByName(Form)

    def setupAnimation(self):
        self.logscutAnim = QVariantAnimation(self)
        self.logscutAnim.setStartValue(0)
        self.logscutAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.logvolAnim = QVariantAnimation(self)
        self.logvolAnim.setStartValue(0.0)
        self.logvolAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.prodAnim = QVariantAnimation(self)
        self.prodAnim.setStartValue(0.0)
        self.prodAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.runtimeAnim = QVariantAnimation(self)
        self.runtimeAnim.setStartValue(0.0)
        self.runtimeAnim.setEasingCurve(QEasingCurve.OutCubic)
        self.logscutAnim.valueChanged.connect(self.aeLogsCut)
        self.logvolAnim.valueChanged.connect(self.aeLogVolume)
        self.prodAnim.valueChanged.connect(self.aeProduction)
        self.runtimeAnim.valueChanged.connect(self.aeRuntime)

    def aeLogsCut(self, val):
        self.LogsCutBar.setValue2(val)
        self.LogsCutValue.setText("{0} logs".format(val))

    def aeLogVolume(self, val):
        self.LogVolumeBar.setValue2(val)
        self.LogVolumeValue.setText("{:.1f} m<sup>3</sup>".format(val))

    def aeProduction(self, val):
        self.ProductionBar.setValue2(val)
        self.ProductionValue.setText("{:.1f} m<sup>3</sup>".format(val))

    def aeRuntime(self, val):
        self.RuntimeBar.setValue2(val)
        self.RuntimeValue.setText("{:.1f} hours".format(val))

    def startAnimation(self):
        self.recoveryWidget.animStart()
        self.uptimeWidget.animStart()
        self.logscutAnim.setDuration(2000*(self.logscut/self.logscutTarget[1]))
        self.logscutAnim.setEndValue(self.logscut)
        self.logscutAnim.start()
        self.logvolAnim.setDuration(2000*(self.logvol/self.logvolTarget[1]))
        self.logvolAnim.setEndValue(self.logvol)
        self.logvolAnim.start()
        self.prodAnim.setDuration(2000*(self.prod/self.prodTarget[1]))
        self.prodAnim.setEndValue(self.prod)
        self.prodAnim.start()
        self.runtimeAnim.setDuration(2000*(self.runtime/self.runtimeTarget[1]))
        self.runtimeAnim.setEndValue(self.runtime)
        self.runtimeAnim.start()
        # self.LogsCutBar.startAnimation()
        # self.LogVolumeBar.startAnimation()
        # self.RuntimeBar.startAnimation()
        # self.ProductionBar.startAnimation()

    def setWidgetText(self):
        self.LogsCutLabel.setText("Logs Cut:")
        self.ProductionValue.setText("{:.1f} m<sup>3</sup>".format(self.prod))
        self.LogVolumeLabel.setText("Log Volume:")
        self.RuntimeValue.setText("{:.1f} hours".format(self.runtime))
        self.ProductionLabel.setText("Production:")
        self.LogsCutValue.setText("{0} logs".format(self.logscut))
        self.LogVolumeValue.setText("{:.1f} m<sup>3</sup>".format(self.logvol))
        self.RuntimeLabel.setText("Runtime:")

    def getHeight(self):
        return self.minimumHeight()

    def updateResults(self, results):
        self.prod = results["Production"]
        self.logscut = results["LogsCut"]
        self.logvol = results["LogVolume"]
        self.runtime = results["RunTime"]
        self.recovery = results["Recovery"]/100
        self.uptime = results["Uptime"]
        self.msldt = results["MSLDT"]
        self.bsldt = results["BSLDT"]
        self.tsldt = results["TSLDT"]
        if results.isna()["Sawdust"]:
            self.sawdust = (1-self.recovery)*0.25
        else:
            self.sawdust = results["Sawdust"]
        self.LogsCutBar.setActual(self.logscut)
        self.LogsCutValue.setText("{0} logs".format(self.logscut))
        self.LogVolumeBar.setActual(self.logvol)
        self.LogVolumeValue.setText("{:.1f} m<sup>3</sup>".format(self.logvol))
        self.RuntimeBar.setActual(self.runtime)
        self.RuntimeValue.setText("{:.1f} hours".format(self.runtime))
        self.ProductionBar.setActual(self.prod)
        self.ProductionValue.setText("{:.1f} m<sup>3</sup>".format(self.prod))
        rec = self.recovery
        sd = self.sawdust
        self.recoveryWidget.updateResults(
            (rec, (1-rec-sd), sd))
        self.uptimeWidget.updateResults(
            (self.uptime, self.msldt, self.bsldt, self.tsldt))

    def printSize(self):
        print(self.size())


class MyProgressBar(QProgressBar):
    mouseClicked = pyqtSignal()

    def __init__(self, parent=None):
        super(MyProgressBar, self).__init__(parent)
        self.installEventFilter(self)
        self.setStyleSheet("QProgressBar {\n"
                           "    border: None;\n"
                           "    color: #ffffff;\n"
                           "    background-color: #c0dddd;\n"
                           "}\n"
                           "\n"
                           " QProgressBar::chunk {\n"
                           "    border: None;\n"
                           "    background-color: qlineargradient(spread:pad, "
                           "x1:0, y1:0, x2:1, y2:1, stop:0 rgb(0, 115, 119), "
                           "stop:1 rgb(4, 147, 131));\n"
                           "    width: 1px;\n"
                           "    color: #ffffff;\n"
                           "}")

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mouseClicked.emit()
        return super(MyProgressBar, self).eventFilter(obj, event)


class DropdownWidget(QWidget):
    def __init__(self, parent=None, name="Total"):
        super(DropdownWidget, self).__init__(parent)
        self.name = name
        self.isOpen = False
        self.isButton = False

        layout = QVBoxLayout()
        layout.setSpacing(0)
        self.bar = MyProgressBar(parent)
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(15)
        self.bar.setFont(font)
        self.bar.setProperty("value", 0)
        self.bar.setValue(0)
        self.bar.setAlignment(
            Qt.AlignLeading
            | Qt.AlignLeft
            | Qt.AlignVCenter)
        self.bar.setTextVisible(True)
        self.bar.setObjectName(self.name)
        layout.addWidget(self.bar)
        self.data = QScrollArea(self)
        sizePolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.Minimum)
        self.data.setSizePolicy(sizePolicy)
        self.data.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.data.setMaximumHeight(0)
        self.data.setObjectName("DropdownSA")
        self.data.setFrameShape(QFrame.NoFrame)
        self.data.setStyleSheet(
            "QScrollArea {"
            "background-color: qlineargradient(spread:pad, "
            "x1:0, y1:0, x2:1, y2:1, stop:0 rgb(192, 221, 221), "
            "stop:1 rgb(180, 233, 197));}")
        self.data.setWidgetResizable(True)
        if name == "Total":
            self.dataWidget = DataWidget(self.data, mult=2)
        else:
            self.dataWidget = DataWidget(self.data)
        self.data.setWidget(self.dataWidget)
        layout.addWidget(self.data)
        self.setLayout(layout)

        self.bar.setFormat("   ▶  "+self.name)

        self.anim = QPropertyAnimation(self.data, b"maximumHeight")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.anim.valueChanged.connect(self.animationEvent)

        # self.bar.mouseClicked.connect(self.onClick)

    def onClick(self):
        self.anim.stop()
        self.anim.setStartValue(self.data.maximumHeight())
        if self.isOpen:
            self.isOpen = False
            self.anim.setDuration(250)
            self.bar.setFormat("   ▶  "+self.name)
            self.anim.setEndValue(0)
        else:
            self.isOpen = True
            self.anim.setDuration(500)
            self.bar.setFormat("   ▾  "+self.name)
            self.anim.setEndValue(450)
            self.dataWidget.startAnimation()
        self.anim.start()

    def updateResults(self, results):
        if results["RunTime"] > 0.1 and not self.isButton:
            self.toggleButton()
        elif results["RunTime"] < 0.1 and self.isButton:
            self.toggleButton()
        v = (results["RunTime"]/self.dataWidget.runtimeTarget[1])*100
        if v > 99:
            v = 100
        v = int(v)
        self.bar.setProperty(
            "Value", v)
        self.bar.setValue(v)
        self.dataWidget.updateResults(results)

    def toggleButton(self):
        if self.isButton:
            self.isButton = False
            self.bar.setCursor(
                QCursor(Qt.ArrowCursor))
            self.bar.mouseClicked.disconnect()
        else:
            self.isButton = True
            self.bar.setCursor(
                QCursor(Qt.PointingHandCursor))
            self.bar.mouseClicked.connect(self.onClick)

    def animationEvent(self, val):
        self.data.setMinimumHeight(min(425, val))


class ResultsWidget(QWidget):
    def setupUi(self, Form):
        self.bars = []
        self.names = []
        self.bla = True

        sizepolicy = QSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.MinimumExpanding
        )
        self.setSizePolicy(sizepolicy)
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setSpacing(15)
        self.verticalLayout_5.setObjectName("verticalLayout_5")

        # BARS
        self.bars.append(DropdownWidget(Form, "Shift 1"))
        self.names.append("Shift 1")
        self.verticalLayout_5.addWidget(self.bars[0])
        self.bars.append(DropdownWidget(Form, "Shift 2"))
        self.names.append("Shift 2")
        self.verticalLayout_5.addWidget(self.bars[1])
        self.bars.append(DropdownWidget(Form, "Total"))
        self.names.append("Total")
        self.verticalLayout_5.addWidget(self.bars[2])

        spacerItem = QSpacerItem(
            20, 40, QSizePolicy.Minimum,
            QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem)
        self.setLayout(self.verticalLayout_5)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def updateResults(self, results):
        if self.bla:
            self.bla = False
        for i in range(results.shape[0]):
            self.bars[i].updateResults(results.iloc[i])

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        # self.shift2.setFormat(_translate("Form", "   ▶  Shift 2"))
        # self.total.setFormat(_translate("Form", "   ▶  Total"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = ResultsWidget()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
