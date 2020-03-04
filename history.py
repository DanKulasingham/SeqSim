from PyQt5.QtCore import QSize, QCoreApplication, QMetaObject, Qt, QObject, \
    pyqtSlot, pyqtSignal, QThread, QEvent
from PyQt5.QtWidgets import \
    QHBoxLayout, QVBoxLayout, QWidget, QSpacerItem, QToolButton, QLabel, \
    QLineEdit, QSizePolicy, QApplication, QTableWidget, QTableWidgetItem, \
    QHeaderView, QAbstractItemView, QScrollArea, QFrame, QMessageBox
from PyQt5.QtGui import QFont, QIcon, QCursor, QMovie, QColor, QBrush, QPixmap
from mysql import connector
from math import ceil
from pandas import read_sql
from seqsim.helper import DrawCutplan
from pyodbc import connect as sqlconnect, \
    ProgrammingError as sqlProgrammingError, \
    OperationalError as sqlOperationalError
from seqsim.helper import LogScanner


class ToolButtonID(QToolButton):
    clickedID = pyqtSignal(int)

    def __init__(self, id, parent=None):
        super(ToolButtonID, self).__init__(parent)
        self.id = id
        self.clicked.connect(self.onClick)

    def onClick(self):
        self.clickedID.emit(self.id)


class HistoryLoader(QObject):
    pageLoaded = pyqtSignal()
    cutplanLoaded = pyqtSignal(int, int)
    cploadfinish = pyqtSignal()

    def __init__(self, host, userid, page=1, search=""):
        super(HistoryLoader, self).__init__()
        self.host = host
        self.limit = 10
        self.data = None
        self.cps = None
        self.search = search
        self.page = page
        self.totalpages = 0
        self.shownpages = []
        self.userid = userid
        self.quit = False

    @pyqtSlot()
    def loadPage(self):
        self.quit = False
        db = connector.connect(
            host=self.host, user="root", passwd="Sequal1234",
            database="simulation", use_pure=True
        )
        with open('support\\getHistory.sql', 'r') as f:
            qry = f.read()

        qry = qry.replace('@user', str(self.userid))
        qry = qry.replace('@offset', str((self.page-1)*self.limit))
        qry = qry.replace('@limit', str(self.limit))
        qry = qry.replace('@search', self.search)
        self.data = read_sql(qry, db)

        # Total pages
        with open('support\\getHistoryCount.sql', 'r') as f:
            qry = f.read()

        qry = qry.replace('@user', str(self.userid))
        qry = qry.replace('@search', self.search)

        cursor = db.cursor()
        cursor.execute(qry)
        (self.sims, ) = cursor.fetchone()
        self.totalpages = ceil(self.sims/self.limit)

        # Load Cutplans
        cps = []
        for i in range(self.data.shape[0]):
            cqry = "SELECT CutplanID as ID, NumLogs as \"Log Count\" From " + \
                   "cutplans WHERE SimID = " + str(self.data['SimID'][i])
            cps.append(read_sql(cqry, db))
        self.cps = cps

        self.pageLoaded.emit()
        try:
            self.conn = sqlconnect(LogScanner)
        except sqlProgrammingError:
            self.conn = None
        with open("support\\cpquery2.sql", 'r') as f:
            self.sqltext = f.read()
        self.cpload(0, 0)

    def cpload(self, i, j):
        if i >= len(self.cps):
            self.cploadfinish.emit()
            return
        if j == self.cps[i].shape[0]:
            j = 0
            i += 1
        if i == len(self.cps):
            return
        if self.quit:
            self.quit = False
            self.cploadfinish.emit()
            return
        cid = 10000 + i*100 + j
        qry = self.sqltext.replace('@CPID', str(self.cps[i].ID[j]))
        if self.conn is not None:
            try:
                data = read_sql(qry, self.conn)
            except (sqlOperationalError, sqlProgrammingError):
                self.conn = sqlconnect(LogScanner)
                data = read_sql(qry, self.conn)
            DrawCutplan(
                self.conn, data.iloc[0], cid,
                folder="images\\cps\\table\\",
                highlight=False)
        self.cutplanLoaded.emit(i, j)
        self.cpload(i, j+1)


class HoverFilter(QObject):
    def __init__(self, parent=None, *args):
        super(HoverFilter, self).__init__(parent, *args)

    def eventFilter(self, object, event):
        if event.type() in [QEvent.HoverMove, QEvent.HoverLeave,
                            QEvent.HoverEnter]:
            return True
        return super(HoverFilter, self).eventFilter(object, event)


class MyLabel(QLabel):
    hoverChange = pyqtSignal(int, bool)

    def __init__(self, parent=None, id=0):
        super(MyLabel, self).__init__(parent)
        self.installEventFilter(self)
        self.id = id

    def enterEvent(self, event):
        self.hoverChange.emit(self.id, True)

    def leaveEvent(self, event):
        self.hoverChange.emit(self.id, False)

    def eventFilter(self, object, event):
        if object is self:
            if event.type() in [QEvent.HoverMove, QEvent.HoverEnter,
                                QEvent.MouseMove]:
                self.hoverChange.emit(self.id, True)
            elif event.type() in [QEvent.HoverLeave, QEvent.Leave]:
                self.hoverChange.emit(self.id, False)
        return super(MyLabel, self).eventFilter(object, event)


class MyScrollArea(QScrollArea):
    hoverChange = pyqtSignal(int, bool)

    def __init__(self, parent=None, id=0):
        super(MyScrollArea, self).__init__(parent)
        self.viewport().installEventFilter(self)
        self.id = id

    def eventFilter(self, object, event):
        if object is self.viewport():
            if event.type() in [QEvent.HoverMove, QEvent.HoverEnter,
                                QEvent.MouseMove]:
                self.hoverChange.emit(self.id, True)
            elif event.type() in [QEvent.HoverLeave, QEvent.Leave]:
                self.hoverChange.emit(self.id, False)
        return super(MyScrollArea, self).eventFilter(object, event)


class MyTable(QTableWidget):
    cellExited = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(MyTable, self).__init__(parent)
        self.viewport().installEventFilter(self)
        self.i = -1

    def eventFilter(self, object, event):
        if object is self.viewport():
            if event.type() in [QEvent.HoverMove, QEvent.HoverEnter,
                                QEvent.MouseMove]:
                i = self.indexAt(event.pos()).row()
                if self.i < 0:
                    self.setCursor(QCursor(Qt.PointingHandCursor))
                if i != self.i:
                    self.cellExited.emit(self.i, 4)
                    self.i = i
            elif event.type() in [QEvent.HoverLeave, QEvent.Leave]:
                self.setCursor(QCursor(Qt.ArrowCursor))
                self.cellExited.emit(self.i, 4)
                self.i = -1
        return super(MyTable, self).eventFilter(object, event)


class HistoryPage(QWidget):
    def setupUi(self, Form, username=None, userid=1, host='192.168.2.171'):
        self.host = host
        self.userid = userid
        self.simid = None
        self.pageButs = []
        self.pagesshown = []

        self.preva = False
        self.nexta = False

        self.ogcol = QColor(0, 0, 0, 0)
        self.hlcol = QColor(192, 221, 221)

        self.db = connector.connect(
            host=self.host, user="root", passwd="Sequal1234",
            database="simulation", use_pure=True
        )
        self.db.autocommit = True

        Form.setObjectName("HistoryPage")
        Form.resize(900, 750)
        Form.setMinimumSize(QSize(900, 750))
        Form.setStyleSheet(
            "QWidget {\n"
            "   background-color: rgba(255, 255, 255, 0);\n"
            "   color: rgb(0, 115, 119);\n"
            "}\n"
            "QToolButton {\n"
            "	background-color: qlineargradient(spread:pad, x1:0, y1:0, "
            "x2:1, y2:1, stop:0 rgba(0, 115, 119, 255), stop:1 rgb(4, 147, "
            "131));\n"
            "	color: white;\n"
            "	border: None;\n"
            "	border-radius: 2px;\n"
            "	font: 11pt \"Tahoma\";\n"
            "}"
        )

        if Form.layout() is not None:
            QWidget().setLayout(Form.layout())
        self.vlayout = QVBoxLayout(Form)
        self.vlayout.setContentsMargins(50, 25, 50, 20)
        self.vlayout.setSpacing(20)
        self.hlayoutT = QHBoxLayout()
        self.hlayoutT.setContentsMargins(-1, -1, -1, 20)
        self.hlayoutT.setSpacing(5)

        self.simhistlabel = QLabel(Form)
        font = QFont()
        font.setFamily('Tahoma')
        font.setPointSize(14)
        font.setBold(True)
        self.simhistlabel.setFont(font)
        self.hlayoutT.addWidget(self.simhistlabel)

        spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayoutT.addItem(spacer)

        self.searchbox = QLineEdit(Form)
        font.setBold(False)
        font.setPointSize(12)
        self.searchbox.setFont(font)
        self.hlayoutT.addWidget(self.searchbox)

        self.searchbutton = QToolButton(Form)
        self.searchbutton.setMinimumSize(QSize(25, 25))
        self.searchbutton.setIcon(QIcon("images\\search.png"))
        self.searchbutton.setCursor(QCursor(Qt.PointingHandCursor))
        self.hlayoutT.addWidget(self.searchbutton)
        self.vlayout.addLayout(self.hlayoutT)

        self.table = MyTable(Form)
        self.table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents)
        self.table.verticalHeader().setMaximumSectionSize(60)
        self.table.verticalHeader().setDefaultSectionSize(60)
        self.table.setRowCount(0)
        self.table.setColumnCount(5)
        cols = ['Name', 'Cutplans', 'Production', 'Date', '']
        self.table.setHorizontalHeaderLabels(cols)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            "QTableWidget {\n"
            "   border:none;\n"
            "   font: 13pt \"Tahoma\";\n"
            "}\n"
        )
        self.tableheader = self.table.horizontalHeader()
        self.tableheader.setStyleSheet(
            "QHeaderView {font: 14pt \"Tahoma\"}")
        self.filter = HoverFilter()
        self.tableheader.installEventFilter(self.filter)
        self.tableheader.setMouseTracking(True)
        self.tableheader.setSectionResizeMode(QHeaderView.Stretch)
        self.tableheader.setSectionResizeMode(4, QHeaderView.Interactive)
        self.tableheader.resizeSection(4, 40)
        font = self.tableheader.font()
        font.setBold(True)
        self.tableheader.setFont(font)
        self.tableheader.setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        # self.table.setAlternatingRowColors(True)
        self.table.setMouseTracking(True)
        self.table.setMaximumHeight(0)
        self.currentHover = 0
        self.vlayout.addWidget(self.table)

        self.loadinggif = QLabel(Form)
        self.loadinggif.setAlignment(Qt.AlignCenter)
        movie = QMovie("images\\loading.gif")
        self.loadinggif.setMovie(movie)
        movie.start()
        self.vlayout.addWidget(self.loadinggif)

        spacer = QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.vlayout.addItem(spacer)

        self.hlayoutB = QHBoxLayout()
        spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayoutB.addItem(spacer)

        self.prevbutton = QToolButton()
        self.prevbutton.setText('◀')
        self.prevbutton.setStyleSheet(
            "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
        self.hlayoutB.addWidget(self.prevbutton)

        self.buttonsLayout = QHBoxLayout()
        self.hlayoutB.addLayout(self.buttonsLayout)

        self.nextbutton = QToolButton()
        self.nextbutton.setText('▶')
        self.nextbutton.setStyleSheet(
            "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
        self.hlayoutB.addWidget(self.nextbutton)

        spacer = QSpacerItem(
            40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayoutB.addItem(spacer)
        self.hlayoutB.setSpacing(5)

        self.vlayout.addLayout(self.hlayoutB)
        self.simhistlabel.setFocus()
        self.setupThread()

        self.table.cellEntered.connect(self.onHoverEnter)
        self.table.cellExited.connect(self.onHoverExit)
        self.searchbutton.clicked.connect(self.onSearch)
        self.searchbox.returnPressed.connect(self.onSearch)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def onHoverEnter(self, row, col):
        if col == 4:
            colour = self.ogcol
            colstr = 'white;'
        else:
            colour = self.hlcol
            colstr = 'rgb(192,221,221);'
        for j in range(4):
            if j == 1:
                self.table.cellWidget(row, j).widget().setStyleSheet(
                    '#tbw {background-color: '+colstr+'}')
            else:
                self.table.item(row, j).setBackground(QBrush(colour))

    def onHoverExit(self, row, col):
        if row < 0:
            return
        for j in range(4):
            if j == 1:
                self.table.cellWidget(row, j).widget().setStyleSheet('')
            else:
                self.table.item(row, j).setBackground(QBrush(self.ogcol))

    def setupThread(self):
        self.thread = QThread()
        self.loader = HistoryLoader(self.host, self.userid)
        self.loader.moveToThread(self.thread)
        self.thread.started.connect(self.loader.loadPage)
        self.loader.pageLoaded.connect(self.setupTable)
        self.loader.cutplanLoaded.connect(self.loaderCP)
        self.loader.cploadfinish.connect(self.loaderFinish)
        self.thread.start()

    def loaderFinish(self):
        self.thread.quit()
        self.thread.terminate()

    def configPagesShown(self):
        totalpages = self.loader.totalpages
        page = self.loader.page
        if totalpages < 6:
            self.pagesshown = list(range(1, totalpages+1))
        elif page < 4:
            self.pagesshown = list(range(1, 6))
        elif page > (totalpages-3):
            self.pagesshown = list(range(totalpages-4, totalpages+1))
        else:
            self.pagesshown = list(range(page-2, page+3))

        pages = self.pagesshown
        self.deletePageButtons()
        if len(pages) > 1:
            self.configurePrevNext(True)
            for i in pages:
                self.pageButs.append(ToolButtonID(i))
                self.pageButs[pages.index(i)].setText(str(i))
                if i == self.loader.page:
                    self.pageButs[pages.index(i)].setStyleSheet(
                        "background-color: none; color: rgb(0,115,119);")
                else:
                    self.setButtonActive(i, True)
                self.buttonsLayout.addWidget(self.pageButs[pages.index(i)])

    def loaderCP(self, r, c):
        cid = 10000 + r*100 + c
        self.cplayouts[r].itemAt(c).widget().setPixmap(QPixmap(
            'images\\cps\\table\\CP'+str(cid)+'.png').scaled(56, 56))
        # self.cplayouts[r].itemAt(c).widget().setIconSize(QSize(56, 56))

    def setupTable(self):
        self.thread.quit()
        self.delButs = []
        self.delButsW = []
        self.cpscrolls = []
        self.cpwidgets = []
        self.cplayouts = []
        data = self.loader.data
        self.table.setRowCount(data.shape[0])
        for i in range(data.shape[0]):
            cps = self.loader.cps[i]
            self.table.setItem(i, 0, QTableWidgetItem(data['SimName'][i]))
            self.cpscrolls.append(MyScrollArea(id=i))
            self.cpscrolls[i].setMinimumHeight(60)
            self.cpscrolls[i].setFrameShape(QFrame.NoFrame)
            self.cpscrolls[i].setWidgetResizable(True)
            self.cpscrolls[i].setHorizontalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff)
            self.cpscrolls[i].setVerticalScrollBarPolicy(
                Qt.ScrollBarAlwaysOff)
            self.cpwidgets.append(QWidget())
            self.cplayouts.append(QHBoxLayout(self.cpwidgets[i]))
            self.cpscrolls[i].setMouseTracking(True)
            self.cpscrolls[i].setCursor(QCursor(Qt.PointingHandCursor))
            self.cpscrolls[i].hoverChange.connect(self.hoverChange)
            self.cpwidgets[i].setMouseTracking(True)
            self.cpwidgets[i].setObjectName('tbw')
            for j in range(cps.shape[0]):
                cpwidg = MyLabel(self.cpwidgets[i], i)
                cpwidg.setText('')
                cpwidg.setStyleSheet(
                    'background-color: rgba(0,0,0,0);')
                cpwidg.setMinimumSize(QSize(60, 60))
                cpwidg.setMaximumSize(QSize(60, 60))
                cpwidg.hoverChange.connect(self.hoverChange)
                self.cplayouts[i].addWidget(cpwidg)
            hspacer = QSpacerItem(
                40, 20,
                QSizePolicy.Expanding,
                QSizePolicy.Minimum)
            self.cplayouts[i].addItem(hspacer)
            self.cplayouts[i].setSpacing(2)
            self.cplayouts[i].setContentsMargins(0, 0, 0, 0)
            self.cpscrolls[i].setWidget(self.cpwidgets[i])
            self.table.setCellWidget(i, 1, self.cpscrolls[i])
            w = self.cpscrolls[i].width()
            self.cpwidgets[i].setMinimumWidth(max(60*cps.shape[0], w))
            self.table.setItem(i, 2, QTableWidgetItem('{:.1f}m3'.format(
                data['Production'][i])))
            self.table.item(i, 2).setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter)
            date = data['Date'][i].to_pydatetime()
            self.table.setItem(i, 3, QTableWidgetItem(date.strftime(
                '%I:%M%p %d %b %Y')))
            self.table.item(i, 3).setTextAlignment(
                Qt.AlignRight | Qt.AlignVCenter)
            self.delButs.append(ToolButtonID(i))
            self.delButs[i].setMinimumSize(QSize(30, 30))
            self.delButs[i].setIcon(QIcon("images\\delete.png"))
            self.delButs[i].setCursor(QCursor(Qt.PointingHandCursor))
            self.delButs[i].clickedID.connect(self.onDelete)
            self.delButsW.append(QWidget())
            self.delButsW[i].setMouseTracking(True)
            self.delButsW[i].setCursor(QCursor(Qt.ArrowCursor))
            layout = QHBoxLayout(self.delButsW[i])
            layout.addWidget(self.delButs[i])
            self.table.setCellWidget(i, 4, self.delButsW[i])
            # self.table.setRowHeight(i, 60)

        if len(self.pagesshown) == 0:
            self.configPagesShown()

        h = data.shape[0]*70 + self.table.horizontalHeader().height()
        self.table.setMinimumHeight(h)
        self.table.setMaximumHeight(h)
        # self.table.setCursor(QCursor(Qt.PointingHandCursor))
        self.loadinggif.setVisible(False)
        self.table.setVisible(True)

    def onDelete(self, id):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("Deleting simulation...")
        msgBox.setText(
            "Are you sure you want to delete "
            + self.loader.data.SimName[id] + "?")
        msgBox.setStandardButtons(
            QMessageBox.Yes | QMessageBox.No)
        msgBox.setDefaultButton(QMessageBox.No)
        r = msgBox.exec()

        if r == QMessageBox.No:
            return

        with open('support\\deleteQuery.sql', 'r') as f:
            query = f.read().replace('@SimID', str(self.loader.data.SimID[id]))
        db = connector.connect(
            host=self.host, user="root", passwd="Sequal1234",
            database="simulation", use_pure=True
        )
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        self.loader.sims -= 1
        self.loader.totalpages = ceil(self.loader.sims/self.loader.limit)
        if id == 0 and self.loader.data.shape[0] == 1:
            self.onPageClick(self.loader.page-1)
        else:
            self.onPageClick(self.loader.page)

    def hoverChange(self, id, entered):
        if entered:
            self.onHoverEnter(id, 1)
        else:
            self.onHoverExit(id, 1)

    def onPageClick(self, id):
        self.setButtonActive(self.loader.page, True)
        self.setButtonActive(id, False)
        self.loader.quit = True
        self.thread.quit()
        self.table.setVisible(False)
        self.loadinggif.setVisible(True)
        self.loader.page = id
        self.configPagesShown()
        self.configurePrevNext(True)
        self.thread.wait()
        self.thread.started.disconnect()
        self.thread.started.connect(self.loader.loadPage)
        self.thread.start()

    def configurePrevNext(self, a):
        if a:
            if self.loader.page > 1 and not self.preva:
                self.prevbutton.clicked.connect(self.onPrevPage)
                self.prevbutton.setStyleSheet("")
                self.prevbutton.setCursor(QCursor(Qt.PointingHandCursor))
                self.preva = True
            if self.loader.page == 1 and self.preva:
                self.prevbutton.clicked.disconnect()
                self.prevbutton.setStyleSheet(
                    "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
                self.prevbutton.setCursor(QCursor(Qt.ArrowCursor))
                self.preva = False

            if self.loader.page < self.loader.totalpages and not self.nexta:
                self.nextbutton.clicked.connect(self.onNextPage)
                self.nextbutton.setStyleSheet("")
                self.nextbutton.setCursor(QCursor(Qt.PointingHandCursor))
                self.nexta = True
            if self.loader.page == self.loader.totalpages and self.nexta:
                self.nextbutton.clicked.disconnect()
                self.nextbutton.setStyleSheet(
                    "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
                self.nextbutton.setCursor(QCursor(Qt.ArrowCursor))
                self.nexta = False
        else:
            self.prevbutton.setStyleSheet(
                "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
            self.nextbutton.setStyleSheet(
                "background-color: rgba(0,0,0,0); color: rgba(0,0,0,0);")
            if self.preva:
                self.preva = False
                self.prevbutton.clicked.disconnect()
            if self.nexta:
                self.nexta = False
                self.nextbutton.clicked.disconnect()

    def onNextPage(self):
        if self.loader.page < self.loader.totalpages:
            self.onPageClick(self.loader.page+1)

    def onPrevPage(self):
        if self.loader.page > 1:
            self.onPageClick(self.loader.page-1)

    def setButtonActive(self, i, a):
        id = self.pagesshown.index(i)
        if a:
            self.pageButs[id].setStyleSheet("")
            self.pageButs[id].setCursor(QCursor(Qt.PointingHandCursor))
            self.pageButs[id].clickedID.connect(self.onPageClick)
        else:
            self.pageButs[id].setStyleSheet(
                "background-color: none; color: rgb(0,115,119);")
            self.pageButs[id].setCursor(QCursor(Qt.ArrowCursor))
            self.pageButs[id].clickedID.disconnect()

    def deletePageButtons(self):
        self.configurePrevNext(False)
        for i in range(len(self.pageButs)):
            self.buttonsLayout.removeWidget(self.pageButs[i])
            self.pageButs[i].deleteLater()
            self.pageButs[i] = None
        self.pageButs = []

    def onSearch(self):
        self.loader.quit = True
        self.thread.quit()
        self.thread.wait()
        self.deletePageButtons()
        self.table.setVisible(False)
        self.loadinggif.setVisible(True)
        self.loader.search = self.searchbox.text()
        self.loader.page = 1
        self.configPagesShown()
        self.thread.started.disconnect()
        self.thread.started.connect(self.loader.loadPage)
        self.thread.start()

    def retranslateUi(self, Form):
        _translate = QCoreApplication.translate
        self.simhistlabel.setText(_translate("Form", "Simulation History"))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    Form = QWidget()
    ui = HistoryPage()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
