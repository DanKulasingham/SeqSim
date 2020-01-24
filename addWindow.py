# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calendar.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtCore import QDate, Qt, QCoreApplication, QEvent, QMetaObject, \
    QObject
from PyQt5.QtWidgets import QWidget, QToolButton, QApplication, QSpinBox, \
    QCalendarWidget, QHBoxLayout, QVBoxLayout, QTableView, QDialogButtonBox, \
    QItemDelegate, QAbstractSpinBox
from PyQt5.QtGui import QCursor, QFont
from datetime import datetime, timedelta
from pyodbc import connect
from pandas import DataFrame, read_sql
from seqsim.classes import PandasModel
from seqsim.helper import LogScanner


class HoverFilter(QObject):
    def __init__(self, parent=None, *args):
        super(HoverFilter, self).__init__(parent, *args)

    def eventFilter(self, object, event):
        if event.type() in [QEvent.HoverMove, QEvent.HoverLeave,
                            QEvent.HoverEnter]:
            return True
        return super(HoverFilter, self).eventFilter(object, event)


class LogCountDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        spinbox = QSpinBox(parent)
        spinbox.setStyleSheet(
            'background-color: white; border: none; color: rgb(0,115,119);'
            'selection-background-color:white; selection-color:rgb(0,115,119);'
        )
        spinbox.setButtonSymbols(QAbstractSpinBox.NoButtons)
        spinbox.setAlignment(Qt.AlignRight)
        spinbox.setRange(0, 10000)
        return spinbox

    def setEditorData(self, editor, index):
        editor.setValue(int(index.data()))


class AddCutplanDialog(QWidget):
    def setupUi(self, adddata=None, sqlfile=None, host=None):
        now = datetime.now()
        if host is None:
            self.host = ''
        else:
            self.host = host
        if adddata is None:
            self.addData = DataFrame(
                columns=['ID', 'Log Count', 'Description'])
        else:
            self.addData = adddata
        self.availData = None
        self.addPD = None
        self.avalPD = None

        # SQL
        if sqlfile is None:
            self.sqlfile = "support\\cpquery.sql"
        else:
            self.sqlfile = sqlfile

        # SERVER CONNECT
        QApplication.setOverrideCursor(
            QCursor(Qt.WaitCursor))
        self.conn = connect(LogScanner)
        QApplication.restoreOverrideCursor()

        self.setObjectName("Dialog")
        # self.setWindowIcon(QIcon('images/icon.ico'))
        self.resize(250, 900)
        self.setStyleSheet(
            "#Dialog {\n"
            "    background-color: white;\n"
            "}")
        self.installEventFilter(self)
        self.horizontalLayout = QVBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.calendarWidget = QCalendarWidget(self)
        font = QFont()
        font.setFamily("Tahoma")
        font.setPointSize(10)
        self.calendarWidget.setFont(font)
        self.calendarWidget.setStyleSheet(
            "#qt_calendar_prevmonth {\n"
            "    qproperty-icon: url(\"images/prev.png\");\n"
            "}\n"
            "\n"
            "#qt_calendar_nextmonth {\n"
            "    qproperty-icon: url(\"images/next.png\");\n"
            "}\n"
            "\n"
            "#qt_calendar_navigationbar {\n"
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0, "
            "x2:1, y2:1, stop:0 rgb(192, 221, 221), stop:1 rgb(180, 233, "
            "197));\n"
            "}\n"
            "\n"
            "#qt_calendar_monthbutton {\n"
            "    color: rgb(0,115,119);\n"
            "    font-size: 15px;\n"
            "}\n"
            "\n"
            "#qt_calendar_yearbutton {\n"
            "    color: rgb(0,115,119);\n"
            "    font-size: 15px;\n"
            "}\n"
            "\n"
            "QCalendarWidget QMenu {\n"
            "    background-color: white;\n"
            "    color: rgb(0,115,119);\n"
            "}\n"
            "\n"
            "QCalendarWidget QMenu::item:selected {\n"
            "    background-color: rgb(192, 221, 221);\n"
            "    color: rgb(0,115,119);\n"
            "}\n"
            "\n"
            "QCalendarWidget QSpinBox {\n"
            "    color: rgb(0,115,119);\n"
            "    selection-background-color: rgb(0, 115, 119);\n"
            "    selection-color: white;\n"
            "}\n"
            "\n"
            "#qt_calendar_calendarview:enabled {\n"
            "    background-color: rgb(192, 221, 221);\n"
            "    alternate-background-color: white;\n"
            "    color: rgb(0, 115, 119);\n"
            "    selection-background-color: rgb(0, 115, 119);\n"
            "    selection-color: white;\n"
            "}\n"
            "\n"
            "#qt_calendar_calendarview:disabled {\n"
            "    color: #44acb0;\n"
            "}\n"
            "\n"
            "")
        btn = self.calendarWidget.findChild(
            QToolButton, "qt_calendar_prevmonth")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        btn = self.calendarWidget.findChild(
            QToolButton, "qt_calendar_nextmonth")
        btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.calendarWidget.setVerticalHeaderFormat(
            QCalendarWidget.NoVerticalHeader)
        self.calendarWidget.setObjectName("calendarWidget")
        self.calendarWidget.setMinimumDate(QDate(2016, 1, 1))
        self.calendarWidget.setMaximumDate(
            QDate(now.year, now.month, now.day))
        btn = self.calendarWidget.findChild(
            QSpinBox, "qt_calendar_yearedit")
        btn.setAlignment(Qt.AlignCenter)
        btn.setButtonSymbols(QSpinBox.NoButtons)
        self.horizontalLayout.addWidget(self.calendarWidget)

        self.leftTV = QTableView(self)
        self.leftTV.setStyleSheet(
            "QTableView {"
            "border: 1px solid rgb(192, 221, 221);"
            "gridline-color: rgb(192, 221, 221);"
            "selection-background-color: rgb(192, 221, 221);"
            "selection-color: rgb(0,115,119);"
            "}"
            "QTableView::item::selected:!active {"
            "selection-color: rgb(0,115,119);"
            "}"
        )
        self.leftTV.setObjectName("leftTV")
        self.leftTV.horizontalHeader().setDefaultSectionSize(65)
        self.leftTV.horizontalHeader().setStretchLastSection(True)
        self.leftTV.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "height: 25px;"
            "border: 1px outset rgb(192, 221, 221);"
            "background-color: white;"
            "selection-background-color: white;"
            "}"
        )
        scrollbarss = """
QScrollBar:vertical {
border: none;
background: white;
width: 5px;
margin: 0 0 0 0;
}
QScrollBar::handle:vertical {
background: rgb(192, 221, 221);
border-radius: 2px;
min-height: 20px;
}
QScrollBar::add-line:vertical {
border: none;
background: none;
height: 0;
subcontrol-position: none;
subcontrol-origin: none;
}

QScrollBar::sub-line:vertical {
border: none;
background: none;
height: 0;
subcontrol-position: none;
subcontrol-origin: none;
}
QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
border: none;
width: 0;
height: 0;
background: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
background: none;
}

QScrollBar:horizontal {
border: none;
background: white;
height: 5px;
margin: 0 0 0 0;
}
QScrollBar::handle:horizontal {
background: rgb(192, 221, 221);
border-radius: 2px;
min-width: 20px;
}
QScrollBar::add-line:horizontal {
border: none;
background: none;
width: 0;
}

QScrollBar::sub-line:horizontal {
border: none;
background: none;
width: 0;
}
QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
border: none;
width: 0;
height: 0;
background: none;
}

QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
background: none;
}
"""
        self.leftTV.verticalScrollBar().setStyleSheet(scrollbarss)
        self.leftTV.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.leftTV.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.leftFilter = HoverFilter()
        self.leftTV.horizontalHeader().installEventFilter(self.leftFilter)
        lcDelegate = LogCountDelegate()
        self.leftTV.setItemDelegateForColumn(1, lcDelegate)
        self.horizontalLayout.addWidget(self.leftTV)

        self.middleButtonsLayout = QHBoxLayout()
        self.middleButtonsLayout.setObjectName("middleButtonsLayout")
        self.addButton = QToolButton(self)
        self.addButton.setObjectName("addButton")
        buttonStyle = \
            "QToolButton {\n"\
            "	background-color: qlineargradient(spread:pad, x1:0, y1:0, "\
            "x2:1, y2:1, stop:0 rgba(0, 115, 119, 255), stop:1 rgb(4, 147, "\
            "131, 255));\n"\
            "	color: white;\n"\
            "	border: None;"\
            "	border-radius: 2px;"\
            "	font: 11pt \"Tahoma\";"\
            "}"
        self.addButton.setStyleSheet(buttonStyle)
        self.addButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.middleButtonsLayout.addWidget(self.addButton)
        self.deleteButton = QToolButton(self)
        font = QFont()
        font.setPointSize(10)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName("deleteButton")
        self.deleteButton.setStyleSheet(buttonStyle)
        self.deleteButton.setCursor(
            QCursor(Qt.PointingHandCursor))
        self.middleButtonsLayout.addWidget(self.deleteButton)
        self.horizontalLayout.addLayout(self.middleButtonsLayout)

        self.rightTV = QTableView(self)
        self.rightTV.setStyleSheet(
            "QTableView {"
            "border: 1px solid rgb(192, 221, 221);"
            "gridline-color: rgb(192, 221, 221);"
            "selection-background-color: rgb(192, 221, 221);"
            "selection-color: rgb(0,115,119);"
            "}"
            "QTableView::item::selected:!active {"
            "selection-color: rgb(0,115,119);"
            "}"
        )
        self.rightTV.setObjectName("rightTV")
        self.rightTV.verticalScrollBar().setStyleSheet(scrollbarss)
        self.rightTV.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.rightTV.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rightTV.horizontalHeader().setDefaultSectionSize(65)
        self.rightTV.horizontalHeader().setStretchLastSection(True)
        self.rightTV.horizontalHeader().setStyleSheet(
            "QHeaderView::section {"
            "height: 25px;"
            "border: 1px outset rgb(192, 221, 221);"
            "background-color: white;"
            "selection-background-color: white;"
            "}"
        )
        self.rightFilter = HoverFilter()
        self.rightTV.horizontalHeader().installEventFilter(self.rightFilter)
        lcDelegate = LogCountDelegate()
        self.rightTV.setItemDelegateForColumn(1, lcDelegate)
        self.horizontalLayout.addWidget(self.rightTV)
        # self.horizontalLayout.addLayout(self.vertlayoutl)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet(
            "QDialogButtonBox QPushButton {\n"
            "    background-color: ;\n"
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0, "
            "x2:1, y2:1, stop:0 rgba(0, 115, 119, 255), stop:1 rgb(4, 147, "
            "131, 255));\n"
            "    color: white;\n"
            "    width: 70px;\n"
            "    height: 25px;\n"
            "    border: None;\n"
            "    border-radius: 2px;\n"
            "    \n"
            "    font: 11pt \"Tahoma\";\n"
            "}")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        for w in self.buttonBox.children():
            if w.metaObject().className() == "QPushButton":
                w.setCursor(QCursor(Qt.PointingHandCursor))
        self.horizontalLayout.addWidget(self.buttonBox)

        # DATA SET UP
        # self.onDateChange()
        # self.RTVSetUp()

        # EVENTS
        self.calendarWidget.selectionChanged.connect(self.onDateChange)
        self.addButton.clicked.connect(self.addFunction)
        self.deleteButton.clicked.connect(self.deleteFunction)

        self.retranslateUi(self)
        # self.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(
        #     self.accept)
        # self.buttonBox.rejected.connect(self.reject)
        QMetaObject.connectSlotsByName(self)

    def eventFilter(self, object, event):
        if object is self and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter,):
                return True
        return super(AddCutplanDialog, self).eventFilter(object, event)

    def onDateChange(self):
        f = open(self.sqlfile, 'r')
        sqltext = f.read()

        selDate = self.calendarWidget.selectedDate().toPyDate()
        date1 = datetime(selDate.year, selDate.month, selDate.day, 4, 0, 0, 0)
        date2 = date1 + timedelta(1)
        sqltext = sqltext.replace(
            '@date1', str(date1)).replace('@date2', str(date2))

        self.availData = read_sql(sqltext, self.conn)
        self.LTVSetUp()

    def LTVSetUp(self):
        self.availPD = PandasModel(
            self.availData
        )
        for i in range(self.addData.shape[0]):
            for j in range(self.availData.shape[0]):
                if self.addData.ID[i] == self.availData.ID[j]:
                    self.availPD.setCompleted(j)
        self.leftTV.setModel(self.availPD)
        self.leftTV.setSelectionBehavior(QTableView.SelectRows)
        self.leftTV.verticalHeader().setVisible(False)
        self.leftTV.setColumnWidth(0, 45)
        self.availPD.dataChanged.connect(self.updateAvailPD)

    def RTVSetUp(self):
        self.addPD = PandasModel(
            self.addData
        )
        self.rightTV.setModel(self.addPD)
        self.rightTV.setSelectionBehavior(QTableView.SelectRows)
        self.rightTV.verticalHeader().setVisible(False)
        self.rightTV.setColumnWidth(0, 45)
        self.addPD.dataChanged.connect(self.updateAddPD)

    def updateAvailPD(self, index, index2):
        self.availData.iloc[index.row(), index.column()] = \
            self.availPD._df.iloc[index.row(), index.column()]

    def updateAddPD(self, index, index2):
        self.addData.iloc[index.row(), index.column()] = \
            self.addPD._df.iloc[index.row(), index.column()]

    def addFunction(self):
        sm = self.leftTV.selectionModel()
        if sm.hasSelection():
            for r in sm.selectedRows():
                if not self.availPD._completed[r.row()]:
                    data = self.availData.iloc[r.row()]
                    self.addData = self.addData.append(data, ignore_index=True)
                    self.availPD.setCompleted(r.row())
            self.RTVSetUp()

    def deleteFunction(self):
        sm = self.rightTV.selectionModel()
        if sm.hasSelection():
            for r in sm.selectedRows():
                for i in range(self.availData.shape[0]):
                    if self.availData.ID[i] == self.addData.ID[r.row()]:
                        self.availPD.setCompleted(i, False)
                self.addData = self.addData.drop(index=r.row())
            self.addData = self.addData.reset_index().drop(columns='index')
            self.RTVSetUp()

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add Cutplans"))
        self.addButton.setText(_translate("Dialog", "Add ▼"))
        self.deleteButton.setText(_translate("Dialog", "▲ Remove"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Dialog = AddCutplanDialog()
    Dialog.setupUi(host="192.168.3.55")
    Dialog.show()
    sys.exit(app.exec_())
