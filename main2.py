# -*- coding: utf-8 -*-
import argparse
import gc
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from text_unidecode import unidecode

from trfi_crawler import distrTen, set_running, set_first_run, Bdscomvn, Chotot, \
    Muaban, Vnexpress, Rongbay, Dichvubds, Sosanhnha, Muabannha, Homedy, Nhadattop1, Dithuenha, Tinbatdongsan, \
    Nhaban, Dothi, Nhadatcanban, Alonhadat, Bdstuanqua, Nhadathay, Muabanchinhchu
from trfi_def import checkUser, read_json_file, write_json_file, counter, logger_err, rq
from time import localtime, strftime
import logging
import time
import traceback
import sys


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger_err.error("Loi khong xac dinh:", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception

# def display_top(snapshot, key_type='lineno', limit=15):
#     snapshot = snapshot.filter_traces((
#         tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
#         tracemalloc.Filter(False, "<unknown>"),
#     ))
#     top_stats = snapshot.statistics(key_type)
#
#     print("Top %s lines" % limit)
#     for index, stat in enumerate(top_stats[:limit], 1):
#         frame = stat.traceback[0]
#         # replace "/path/to/module/file.py" with "module/file.py"
#         filename = os.sep.join(frame.filename.split(os.sep)[-2:])
#         print("#%s: %s:%s: %.1f KiB"
#               % (index, filename, frame.lineno, stat.size / 1024))
#         line = linecache.getline(frame.filename, frame.lineno).strip()
#         if line:
#             print('    %s' % line)
#
#     other = top_stats[limit:]
#     if other:
#         size = sum(stat.size for stat in other)
#         print("%s other: %.1f KiB" % (len(other), size / 1024))
#     total = sum(stat.size for stat in top_stats)
#     print("Total allocated size: %.1f KiB" % (total / 1024))

args = None
parser = argparse.ArgumentParser(description='Argument')
parser.add_argument('site', metavar='s', type=int, nargs='?')
parser.add_argument('type', metavar='t', nargs='?')
parser.add_argument('page', metavar='t', type=str, nargs='?')
parser.add_argument('rerun', metavar='r', type=int, nargs='?')
parser.add_argument('start_page', metavar='sp', type=int, nargs='?')
parser.add_argument('end_page', metavar='ep', type=int, nargs='?')
parser.add_argument('province', metavar='c', type=int, nargs='?')

args = parser.parse_args()
server = read_json_file('config.json')['server']


def current_time():
    return strftime("%Y-%m-%d %H:%M:%S", localtime())


def current_time_2():
    return '{} - '.format(strftime("%H:%M:%S", localtime()))


def get_day():
    return strftime("%d", localtime())


def sleep(time):
    loop = QEventLoop()
    QTimer.singleShot(time, loop.quit)
    loop.exec_()


def put_data(total):
    try:
        data = {'site_id': str(args.site), 'type': args.type, 'sp': str(args.start_page), 'ep': str(args.end_page),
                'province': str(args.province),
                'update': {'time': current_time(), 'total': total}}
        rq.put(f'{server}/api/update_data', json=data)
    except Exception as e:
        logger_err.error('Khong cap nhat duoc du lieu: %s', e)


time_moigioi = str()
moigioi_status = True


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    mess = pyqtSignal(str)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_cb'] = self.signals.progress
        self.kwargs['mess_cb'] = self.signals.mess

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            logger_err.error(e, exc_info=True)
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        self.rf = read_json_file('config.json')
        super(Login, self).__init__(parent)
        #     self.textName = QtWidgets.QLineEdit(self)
        #     self.textPass = QtWidgets.QLineEdit(self)
        #     self.btnLogin = QtWidgets.QPushButton('Login', self)
        #     layout.addWidget(self.textName)
        #     layout.addWidget(self.textPass)
        #     layout.addWidget(self.btnLogin)
        self.setWindowTitle("BDS Crawler")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon-bds.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.resize(420, 260)
        self.setStyleSheet(
            "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 87, 106, 255), stop:1 rgba(58, 113, 113, 255))")

        layout = QtWidgets.QVBoxLayout(self)

        self.txtUser = QtWidgets.QLineEdit(self)
        self.txtUser.setMinimumSize(QtCore.QSize(0, 32))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtUser.setFont(font)
        self.txtUser.setStyleSheet("background-color: #fff;")
        self.txtUser.setObjectName("lineEdit")

        self.txtPass = QtWidgets.QLineEdit(self)
        self.txtPass.setMinimumSize(QtCore.QSize(0, 32))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.txtPass.setFont(font)
        self.txtPass.setStyleSheet("background-color: #fff;")
        self.txtPass.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtPass.setClearButtonEnabled(False)
        self.txtPass.setObjectName("lineEdit_2")

        self.btnLogin = QtWidgets.QPushButton('ĐĂNG NHẬP', self)
        font = QtGui.QFont()
        font.setFamily("Corbel")
        font.setPointSize(11)
        self.btnLogin.setFont(font)
        self.btnLogin.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnLogin.setAutoFillBackground(False)
        self.btnLogin.setStyleSheet("background-color: rgb(76, 76, 76);\n"
                                    "color: rgb(255, 255, 255);")
        self.btnLogin.setAutoDefault(False)
        self.btnLogin.setFlat(False)
        self.btnLogin.setAutoDefault(True)
        self.btnLogin.setObjectName("btnLogin")

        self.ckbRemember = QtWidgets.QCheckBox(self)
        self.ckbRemember.setObjectName("ckbRemember")
        self.ckbRemember.setStyleSheet("color: rgb(255, 255, 255);")

        layout.setContentsMargins(70, -1, 70, -1)
        layout.addWidget(self.txtUser)
        layout.addWidget(self.txtPass)
        layout.addWidget(self.ckbRemember)
        layout.addWidget(self.btnLogin)

        self.txtPass.setToolTip("Nhập mật khẩu")
        self.txtPass.setPlaceholderText("Mật khẩu")
        self.txtUser.setToolTip("Nhập tên đăng nhập")
        self.txtUser.setPlaceholderText("Tên đăng nhập")
        self.ckbRemember.setText('Nhớ mật khẩu')

        self.btnLogin.clicked.connect(self.handleLogin)

        user_rmb = self.rf['user']['remember']
        user_username = self.rf['user']['username']
        user_passwd = self.rf['user']['password']

        if user_rmb:
            self.ckbRemember.setChecked(True)
            self.txtUser.setText(user_username)
            self.txtPass.setText(user_passwd)

    def handleLogin(self):
        if self.ckbRemember.isChecked():
            self.rf['user']['remember'] = True
            self.rf['user']['username'] = self.txtUser.text()
            self.rf['user']['password'] = self.txtPass.text()
            write_json_file('config.json', self.rf)
        else:
            self.rf['user']['remember'] = False
            self.rf['user']['username'] = ''
            self.rf['user']['password'] = ''
            write_json_file('config.json', self.rf)
        checkUser(self, QtWidgets)


class Ui_MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(Ui_MainWindow, self).__init__(*args, **kwargs)
        self.threadpool = QThreadPool()
        self.isRunning = False
        self.is_stop = False
        self.total_post = 0
        self.rf = read_json_file('config.json')

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.setEnabled(True)
        MainWindow.resize(580, 720)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon-bds.ico"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(
            "background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 87, 106, 255), stop:1 rgba(58, 113, 113, 255));\n"
            "color: #fff;")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setContentsMargins(0, 22, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(70, -1, 75, -1)
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 20))
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 20))
        self.progressBar.setStyleSheet("color: #fff;")
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 7, 1, 1, 6)
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_11.setFont(font)
        self.label_11.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_11.setAutoFillBackground(False)
        self.label_11.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_11.setTextFormat(QtCore.Qt.PlainText)
        self.label_11.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_11.setIndent(6)
        self.label_11.setObjectName("label_11")
        self.gridLayout.addWidget(self.label_11, 4, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setMinimumSize(QtCore.QSize(100, 0))
        self.label_3.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_3.setStyleSheet("color: #fff;")
        self.label_3.setIndent(20)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 6, 3, 1, 2)
        self.txtCheckPhone = QtWidgets.QLineEdit(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtCheckPhone.sizePolicy().hasHeightForWidth())
        self.txtCheckPhone.setSizePolicy(sizePolicy)
        self.txtCheckPhone.setMaximumSize(QtCore.QSize(50, 16777215))
        self.txtCheckPhone.setFocusPolicy(QtCore.Qt.TabFocus)
        self.txtCheckPhone.setWhatsThis("")
        self.txtCheckPhone.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                         "color: black;")
        self.txtCheckPhone.setAlignment(QtCore.Qt.AlignCenter)
        self.txtCheckPhone.setObjectName("txtCheckPhone")
        self.gridLayout.addWidget(self.txtCheckPhone, 6, 5, 1, 1)
        self.cbbProvince = QtWidgets.QComboBox(self.centralwidget)
        self.cbbProvince.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cbbProvince.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                       "color: black;")
        self.cbbProvince.setObjectName("cbbProvince")
        self.gridLayout.addWidget(self.cbbProvince, 1, 1, 1, 6)
        self.lbl_sttpage = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_sttpage.sizePolicy().hasHeightForWidth())
        self.lbl_sttpage.setSizePolicy(sizePolicy)
        self.lbl_sttpage.setMinimumSize(QtCore.QSize(0, 20))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.lbl_sttpage.setFont(font)
        self.lbl_sttpage.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.lbl_sttpage.setAutoFillBackground(False)
        self.lbl_sttpage.setStyleSheet("color: black;\n"
                                       "background-color: #fff;")
        self.lbl_sttpage.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_sttpage.setIndent(6)
        self.lbl_sttpage.setObjectName("lbl_sttpage")
        self.gridLayout.addWidget(self.lbl_sttpage, 7, 0, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_7.setFont(font)
        self.label_7.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_7.setAutoFillBackground(False)
        self.label_7.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_7.setTextFormat(QtCore.Qt.PlainText)
        self.label_7.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_7.setIndent(6)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 20))
        self.label.setAutoFillBackground(False)
        self.label.setStyleSheet("color: rgb(255, 255, 255);")
        self.label.setIndent(5)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 5, 2, 1, 1)
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy)
        self.label_12.setMinimumSize(QtCore.QSize(120, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_12.setFont(font)
        self.label_12.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_12.setAutoFillBackground(False)
        self.label_12.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_12.setTextFormat(QtCore.Qt.PlainText)
        self.label_12.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_12.setIndent(6)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 5, 0, 1, 1)
        self.rdoAuto = QtWidgets.QRadioButton(self.centralwidget)
        self.rdoAuto.setMinimumSize(QtCore.QSize(50, 0))
        self.rdoAuto.setMaximumSize(QtCore.QSize(65, 16777215))
        self.rdoAuto.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.rdoAuto.setAcceptDrops(True)
        self.rdoAuto.setChecked(True)
        self.rdoAuto.setStyleSheet("color: rgb(255, 255, 255);")
        self.rdoAuto.setObjectName("rdoAuto")
        self.gridLayout.addWidget(self.rdoAuto, 4, 1, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_10.setFont(font)
        self.label_10.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_10.setAutoFillBackground(False)
        self.label_10.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_10.setTextFormat(QtCore.Qt.PlainText)
        self.label_10.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_10.setIndent(6)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 3, 0, 1, 1)
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_18.sizePolicy().hasHeightForWidth())
        self.label_18.setSizePolicy(sizePolicy)
        self.label_18.setMinimumSize(QtCore.QSize(120, 20))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_18.setFont(font)
        self.label_18.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_18.setAutoFillBackground(False)
        self.label_18.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_18.setTextFormat(QtCore.Qt.PlainText)
        self.label_18.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_18.setIndent(6)
        self.label_18.setObjectName("label_18")
        self.gridLayout.addWidget(self.label_18, 6, 0, 1, 1)
        self.rdoCustom = QtWidgets.QRadioButton(self.centralwidget)
        self.rdoCustom.setMinimumSize(QtCore.QSize(50, 0))
        self.rdoCustom.setMaximumSize(QtCore.QSize(65, 16777215))
        self.rdoCustom.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.rdoCustom.setStyleSheet("color: rgb(255, 255, 255);")
        self.rdoCustom.setObjectName("rdoCustom")
        self.gridLayout.addWidget(self.rdoCustom, 4, 2, 1, 1)
        self.cbbDistrict = QtWidgets.QComboBox(self.centralwidget)
        self.cbbDistrict.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cbbDistrict.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                       "color: black;")
        self.cbbDistrict.setObjectName("cbbDistrict")
        self.gridLayout.addWidget(self.cbbDistrict, 2, 1, 1, 6)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_6.setFont(font)
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAutoFillBackground(False)
        self.label_6.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_6.setTextFormat(QtCore.Qt.PlainText)
        self.label_6.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_6.setIndent(6)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 1, 0, 1, 1)
        self.spinAutoRun = QtWidgets.QSpinBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinAutoRun.sizePolicy().hasHeightForWidth())
        self.spinAutoRun.setSizePolicy(sizePolicy)
        self.spinAutoRun.setProperty("value", 1)
        self.spinAutoRun.setMinimumSize(QtCore.QSize(0, 20))
        self.spinAutoRun.setMaximumSize(QtCore.QSize(50, 20))
        self.spinAutoRun.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.spinAutoRun.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                       "color: black;")
        self.spinAutoRun.setAlignment(QtCore.Qt.AlignCenter)
        self.spinAutoRun.setObjectName("spinAutoRun")
        self.gridLayout.addWidget(self.spinAutoRun, 5, 1, 1, 1)
        self.cbbLoaiTin = QtWidgets.QComboBox(self.centralwidget)
        self.cbbLoaiTin.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cbbLoaiTin.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                      "color: black;")
        self.cbbLoaiTin.setObjectName("cbbLoaiTin")
        self.gridLayout.addWidget(self.cbbLoaiTin, 3, 1, 1, 6)
        self.spinEndPage = QtWidgets.QSpinBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinEndPage.sizePolicy().hasHeightForWidth())
        self.spinEndPage.setSizePolicy(sizePolicy)
        self.spinEndPage.setMinimumSize(QtCore.QSize(50, 0))
        self.spinEndPage.setMaximumSize(QtCore.QSize(50, 16777215))
        self.spinEndPage.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.spinEndPage.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                       "color: black;")
        self.spinEndPage.setAlignment(QtCore.Qt.AlignCenter)
        self.spinEndPage.setMinimum(1)
        self.spinEndPage.setMaximum(999)
        self.spinEndPage.setProperty("value", 3)
        self.spinEndPage.setObjectName("spinEndPage")
        self.gridLayout.addWidget(self.spinEndPage, 4, 4, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setMinimumSize(QtCore.QSize(120, 0))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.label_9.setFont(font)
        self.label_9.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_9.setAutoFillBackground(False)
        self.label_9.setStyleSheet("color: rgb(255, 255, 255);")
        self.label_9.setTextFormat(QtCore.Qt.PlainText)
        self.label_9.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.label_9.setIndent(6)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 2, 0, 1, 1)
        self.spinStartPage = QtWidgets.QSpinBox(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.spinStartPage.sizePolicy().hasHeightForWidth())
        self.spinStartPage.setSizePolicy(sizePolicy)
        self.spinStartPage.setMinimumSize(QtCore.QSize(50, 0))
        self.spinStartPage.setMaximumSize(QtCore.QSize(50, 16777215))
        self.spinStartPage.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.spinStartPage.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                         "color: black;")
        self.spinStartPage.setAlignment(QtCore.Qt.AlignCenter)
        self.spinStartPage.setMinimum(1)
        self.spinStartPage.setObjectName("spinStartPage")
        self.gridLayout.addWidget(self.spinStartPage, 4, 3, 1, 1)
        self.cbbSite = QtWidgets.QComboBox(self.centralwidget)
        self.cbbSite.setFocusPolicy(QtCore.Qt.TabFocus)
        self.cbbSite.setStyleSheet("background-color: rgb(255, 255, 255);\n"
                                   "color: black;")
        self.cbbSite.setObjectName("cbbSite")
        self.gridLayout.addWidget(self.cbbSite, 0, 1, 1, 6)
        self.ckbExportPhone = QtWidgets.QCheckBox(self.centralwidget)
        self.ckbExportPhone.setMinimumSize(QtCore.QSize(0, 20))
        self.ckbExportPhone.setWhatsThis("")
        self.ckbExportPhone.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ckbExportPhone.setStyleSheet("color: #fff;")
        self.ckbExportPhone.setObjectName("ckbExportPhone")
        self.gridLayout.addWidget(self.ckbExportPhone, 6, 1, 1, 2)
        self.listWidget = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget.setEnabled(True)
        self.listWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.listWidget.setMaximumSize(QtCore.QSize(1000, 1000))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.listWidget.setFont(font)
        self.listWidget.setStyleSheet("background-color: white; color: black;")
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.gridLayout.addWidget(self.listWidget, 8, 0, 1, 7)
        self.listWidget_2 = QtWidgets.QListWidget(self.centralwidget)
        self.listWidget_2.setMaximumSize(QtCore.QSize(16777215, 27))
        self.listWidget_2.setStyleSheet("background-color: white; color: black;")
        self.listWidget_2.setObjectName("listWidget_2")
        self.gridLayout.addWidget(self.listWidget_2, 10, 0, 1, 7)
        self.btnStart = QtWidgets.QPushButton(self.centralwidget)
        self.btnStart.setMinimumSize(QtCore.QSize(160, 0))
        font = QtGui.QFont()
        font.setFamily("Corbel")
        font.setPointSize(11)
        self.btnStart.setFont(font)
        self.btnStart.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnStart.setAutoFillBackground(False)
        self.btnStart.setStyleSheet("background-color: rgb(76, 76, 76);\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "border: none;\n"
                                    "padding: 4px 0 4px 0;")
        self.btnStart.setAutoDefault(True)
        self.btnStart.setFlat(False)
        self.btnStart.setObjectName("btnStart")
        self.gridLayout.addWidget(self.btnStart, 9, 0, 1, 7, QtCore.Qt.AlignHCenter)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        try: args_type = args.type.lower()
        except AttributeError: pass
        if args.site:
            self.cbbLoaiTin.addItem('Bán nhà')
            self.cbbLoaiTin.addItem('Bán đất + Bán CHCC')
            self.cbbSite.setCurrentIndex(args.site - 1)
            if args.type.isnumeric():
                self.cbbLoaiTin.setCurrentIndex(args.type - 1)
            else:
                if args_type == 'b': type_index = 1
                elif args_type == 'ct': type_index = 2
                elif args_type == 'all': type_index = 3
                elif args_type == 'bn': type_index = 4
                elif unidecode(args_type) == 'bd': type_index = 5
                else: type_index = 0
                self.cbbLoaiTin.setCurrentIndex(type_index - 1)
            self.cbbProvince.setCurrentIndex(args.province - 1)
            if args.page.lower() == 'auto':
                self.rdoAuto.setChecked(True)
            elif args.page.lower() == 'custom':
                self.rdoCustom.setChecked(True)
            self.spinStartPage.setValue(args.start_page)
            self.spinEndPage.setValue(args.end_page)
            self.spinAutoRun.setValue(args.rerun)
            self.btnStart.click()

    def openTools(self):
        subprocess.run([r'BDSCrawler.exe', '4', '1', 'c', '1', '1', '3'])

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", f"BDS Crawler 6.1.3 - {counter if counter > 1 else ''}"))
        self.label_10.setText(_translate("MainWindow", "Loại Tin"))
        self.label_12.setText(_translate("MainWindow", "Tự chạy"))
        self.label_11.setText(_translate("MainWindow", "Trang"))
        self.label_6.setText(_translate("MainWindow", "Tỉnh/Thành"))
        self.label_9.setText(_translate("MainWindow", "Quận/Huyện"))
        self.spinAutoRun.setToolTip(_translate("MainWindow", "Sau khi chạy xong sẽ đợi bao nhiêu phút để chạy tiếp"))
        self.spinAutoRun.setStatusTip(_translate("MainWindow", "Sau khi chạy xong sẽ đợi bao nhiêu phút để chạy tiếp"))
        self.rdoAuto.setStatusTip(_translate("MainWindow", "Tự động ngừng chạy khi đến trang có chứa tin cũ"))
        self.btnStart.setText(_translate("MainWindow", "START"))
        self.label.setText(_translate("MainWindow", "phút"))
        self.label_7.setText(_translate("MainWindow", "Site"))
        self.rdoCustom.setStatusTip(_translate("MainWindow", "Tùy chỉnh số trang bắt đầu chạy và số trang kết thúc"))
        self.rdoCustom.setText(_translate("MainWindow", "Custom"))
        self.label_3.setStatusTip(
            _translate("MainWindow", "Kiểm tra số điện thoại có trùng với bao nhiêu tin đã lấy gần đây"))
        self.label_3.setText(_translate("MainWindow", "Check SDT:"))
        self.ckbExportPhone.setStatusTip(_translate("MainWindow", "Xuất số điện thoại của tin ra file text"))
        self.ckbExportPhone.setText(_translate("MainWindow", "Xuất SDT:  "))
        self.label_18.setText(_translate("MainWindow", "Tùy chọn"))
        self.txtCheckPhone.setStatusTip(
            _translate("MainWindow", "Kiểm tra số điện thoại có trùng với bao nhiêu tin đã lấy gần đây"))
        self.txtCheckPhone.setText(_translate("MainWindow", "1000"))

        self.cbbSite.addItem("Batdongsan.com.vn")
        self.cbbSite.addItem("Muaban.net")
        self.cbbSite.addItem("Chotot.vn")
        self.cbbSite.addItem("Raovat.vnexpress.net")
        self.cbbSite.addItem("Rongbay.com")
        self.cbbSite.addItem("Dichvubds.vn")
        self.cbbSite.addItem("Sosanhnha.com")
        self.cbbSite.addItem("Muabannhachinhchu.vn")
        self.cbbSite.addItem("Homedy.com")
        self.cbbSite.addItem("Nhadattop1.com")
        self.cbbSite.addItem("Dithuenha.com")
        self.cbbSite.addItem("Tinbatdongsan.com")
        self.cbbSite.addItem("Nhaban.vn")
        self.cbbSite.addItem("Dothi.net")
        self.cbbSite.addItem("Nhadatcanban.com.vn")
        self.cbbSite.addItem("Alonhadat.com.vn")
        self.cbbSite.addItem("Bdstuanqua.com")
        self.cbbSite.addItem("Nhadathay.com")
        self.cbbSite.addItem("Muabanchinhchu.net")
        self.cbbProvince.addItem("Hà Nội")
        self.cbbProvince.addItem("Hồ Chí Minh")
        self.cbbDistrict.addItem('Tất cả')
        for quanhuyen in distrTen:
            self.cbbDistrict.addItem(quanhuyen)
        self.cbbLoaiTin.addItem("Bán")
        self.cbbLoaiTin.addItem("Cho thuê")
        self.cbbLoaiTin.addItem('Tất cả')
        self.lbl_sttpage.setText(_translate("MainWindow", "Trang"))
        self.rdoAuto.setText(_translate("MainWindow", "Auto"))
        self.rdoCustom.setText(_translate("MainWindow", "Custom"))
        # self.cal()

        self.ckbExportPhone.setChecked(self.rf['setting']['export_phone'])
        self.txtCheckPhone.setText(str(self.rf['setting']['check_phone']))
        self.progressBar.hide()
        self.lbl_sttpage.hide()
        self.listWidget_2.hide()
        if self.cbbSite.currentIndex() == 0:
            self.rdoAuto.setChecked(True)
        # self.spinStartPage.hide()
        # self.spinEndPage.hide()

        self.btnStart.clicked.connect(self.start)
        self.txtCheckPhone.textChanged.connect(self.check_phone)
        self.ckbExportPhone.clicked.connect(self.export_phone)
        self.listWidget.customContextMenuRequested.connect(self.on_context_menu)
        self.cbbSite.activated.connect(self.onActivated)
        # self.rdoCustom.clicked.connect(self.rdo_custom)
        # self.rdoAuto.clicked.connect(self.rdo_auto)
        # self.cbbDistrict.activated.connect(self.onActivated)
        # self.cbbDistrict.currentIndexChanged.connect(self.cal)
        # self.spinStartPage.valueChanged.connect(self.cal)
        # self.spinEndPage.valueChanged.connect(self.cal)
        # self.cbbLoaiTin.currentIndexChanged.connect(self.cal)

    def onActivated(self, index):
        # return index
        if index == 9:
            self.cbbLoaiTin.setCurrentIndex(0)
        elif index == 10:
            self.cbbLoaiTin.setCurrentIndex(1)
        elif index == 1:
            self.rdoCustom.setChecked(True)
            self.cbbLoaiTin.addItem('Bán nhà')
            self.cbbLoaiTin.addItem('Bán đất + Bán CHCC')
        else:
            self.rdoAuto.setChecked(True)
            self.cbbLoaiTin.removeItem(3)
            self.cbbLoaiTin.removeItem(4)
        # print(self.cbbProvince.currentIndex())

    def on_context_menu(self, pos):
        # show context menu
        menu = QMenu()
        menu.move(123, 123)
        clear_action = menu.addAction("Clear log")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == clear_action:
            self.listWidget.clear()

    def check_phone(self):
        self.rf['setting']['check_phone'] = int(self.txtCheckPhone.text())
        write_json_file('config.json', self.rf)

    def export_phone(self):
        self.rf['setting']['export_phone'] = self.ckbExportPhone.isChecked()
        write_json_file('config.json', self.rf)

    def rdo_custom(self):
        self.spinStartPage.show()
        self.spinEndPage.show()

    def rdo_auto(self):
        self.spinStartPage.hide()
        self.spinEndPage.hide()

    def log(self, mess):
        try:
            self.listWidget.addItem(current_time_2() + mess)
        except TypeError:
            print('Chua co mess')
        self.listWidget.scrollToBottom()

    def return_result(self, rs):
        try:
            if rs:
                self.total_post += int(rs.split(': ')[1])
                sleep(1000)
        except IndexError:
            pass
        try:
            self.log(rs)
            self.listWidget_2.clear()
            self.listWidget_2.addItem(
                f'{strftime("%d/%m/%Y", localtime())} - Tổng số tin đã lấy hôm nay: {self.total_post}')
        except AttributeError as e:
            logging.warning('Chua co total', e)
        except Exception:
            logger_err.error('Loi return result', exc_info=True)
        else:
            put_data(self.total_post)

    def get_mess(self, mess):
        if mess.startswith(' Trang'):
            self.lbl_sttpage.setText(mess)
        else:
            self.log(mess)

    def progress_fn(self, n):
        self.progressBar.setProperty('value', n)

    def execute_this_fn(self, progress_cb, mess_cb):
        logging.error('Execute_this_fn')
        global time_moigioi, moigioi_status
        rerun = self.spinAutoRun.value() * 60
        i = 0
        current_day = get_day()
        while self.isRunning:
            i += 1
            if current_day != get_day():
                self.total_post = 0
                current_day = get_day()
            self.log(f'Chạy lần {i}: {self.cbbSite.currentText()}'
                     f' - {self.cbbProvince.currentText()} - {self.cbbLoaiTin.currentText()}'
                     f' - {strftime("%d/%m/%Y", localtime())}')
            # tracemalloc.start()
            self.start_crawl(progress_cb, mess_cb)
            # snapshot = tracemalloc.take_snapshot()
            # display_top(snapshot)
            c = gc.collect()
            print('execute fn', c)
            self.log(f'Đợi lần chạy tiếp theo: Còn {self.spinAutoRun.value()} phút')
            for x in range(rerun):
                sleep(1000)
                if self.is_stop:
                    self.log('Stopped')
                    break
            else:
                set_first_run(False)
                continue
            break

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("Complete!")
        set_first_run(True)
        self.btnStart.setDisabled(False)
        self.btnStart.setStyleSheet("background-color: rgb(76, 76, 76);\n"
                                    "color: rgb(255, 255, 255);")

    def start_crawl(self, progress_cb, mess_cb):
        start = time.time()
        _site = self.cbbSite.currentIndex() + 1
        _provin = self.cbbProvince.currentIndex() + 1
        _distr = self.cbbDistrict.currentIndex()
        _type = self.cbbLoaiTin.currentText()
        _type_ar = None
        if self.rdoCustom.isChecked(): _tpage = 'custom'
        else: _tpage = 'auto'
        if _tpage == 'custom':
            _startp = self.spinStartPage.value()
            _endp = self.spinEndPage.value()
        else:
            _startp, _endp = None, self.spinEndPage.value()  # TODO

        if _site == 1:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type = 0
            bdscomvn = Bdscomvn(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = bdscomvn.crawl()
            self.return_result(rs)

        elif _site == 3:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    chotot = Chotot(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                    page=_tpage)
                    rs = chotot.crawl()
                    self.return_result(rs)
            else:
                chotot = Chotot(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                page=_tpage)
                rs = chotot.crawl()
                self.return_result(rs)
        elif _site == 2:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            elif _type == 'Bán nhà':
                _type = 3
            elif _type == 'Bán đất + Bán căn hộ chung cư':
                _type = 4
            else:
                _type = 0

            muaban = Muaban(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = muaban.crawl()
            self.return_result(rs)

        elif _site == 4:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type = 0

            vnexpress = Vnexpress(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = vnexpress.crawl()
            self.return_result(rs)

        elif _site == 5:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type = 0

            rongbay = Rongbay(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = rongbay.crawl()
            self.return_result(rs)

        elif _site == 6:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    dichvubds = Dichvubds(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                          page=_tpage)
                    rs = dichvubds.crawl()
                    self.return_result(rs)
            else:
                dichvubds = Dichvubds(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                      page=_tpage)
                rs = dichvubds.crawl()
                self.return_result(rs)

        elif _site == 7:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type = 0

            sosanhnha = Sosanhnha(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = sosanhnha.crawl()
            self.return_result(rs)

        elif _site == 8:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type = 0

            muabannha = Muabannha(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                  page=_tpage)
            rs = muabannha.crawl()
            self.return_result(rs)

        elif _site == 9:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    homedy = Homedy(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                    page=_tpage)
                    rs = homedy.crawl()
                    self.return_result(rs)
            else:
                homedy = Homedy(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
                rs = homedy.crawl()
                self.return_result(rs)

        elif _site == 10:
            _type = 1

            nhadattop1 = Nhadattop1(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                    page=_tpage)
            rs = nhadattop1.crawl()
            self.return_result(rs)

        elif _site == 11:
            _type = 1

            dithuenha = Dithuenha(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = dithuenha.crawl()
            self.return_result(rs)

        elif _site == 12:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    tinbatdongsan = Tinbatdongsan(_provin, type, progress_cb, mess_cb, start_page=_startp,
                                                  end_page=_endp, page=_tpage)
                    rs = tinbatdongsan.crawl()
                    self.return_result(rs)
            else:
                tinbatdongsan = Tinbatdongsan(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                              page=_tpage)
                rs = tinbatdongsan.crawl()
                self.return_result(rs)

        elif _site == 13:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    nhaban = Nhaban(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                    page=_tpage)
                    rs = nhaban.crawl()
                    self.return_result(rs)
            else:
                nhaban = Nhaban(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
                rs = nhaban.crawl()
                self.return_result(rs)

        elif _site == 14:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    dothi = Dothi(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
                    rs = dothi.crawl()
                    self.return_result(rs)
            else:
                dothi = Dothi(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
                rs = dothi.crawl()
                self.return_result(rs)

        elif _site == 15:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    nhadatcanban = Nhadatcanban(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                                page=_tpage)
                    rs = nhadatcanban.crawl()
                    self.return_result(rs)
            else:
                nhadatcanban = Nhadatcanban(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                            page=_tpage)
                rs = nhadatcanban.crawl()
                self.return_result(rs)

        elif _site == 16:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    alonhadat = Alonhadat(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                          page=_tpage)
                    rs = alonhadat.crawl()
                    self.return_result(rs)
            else:
                alonhadat = Alonhadat(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                      page=_tpage)
                rs = alonhadat.crawl()
                self.return_result(rs)

        elif _site == 17:

            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]

            if _type_ar:
                for type in _type_ar:
                    bdstuanqua = Bdstuanqua(_provin, type, progress_cb, mess_cb, start_page=_startp,
                                            end_page=_endp, page=_tpage)
                    rs = bdstuanqua.crawl()
                    self.return_result(rs)
            else:
                bdstuanqua = Bdstuanqua(_provin, _type, progress_cb, mess_cb, start_page=_startp,
                                        end_page=_endp, page=_tpage)
                rs = bdstuanqua.crawl()
                self.return_result(rs)

        elif _site == 18:
            if _type == 'Bán':
                _type = 1
            elif _type == 'Cho thuê':
                _type = 2
            else:
                _type_ar = [1, 2]
            if _type_ar:
                for type in _type_ar:
                    nhadathay = Nhadathay(_provin, type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                          page=_tpage)
                    rs = nhadathay.crawl()
                    self.return_result(rs)
            else:
                nhadathay = Nhadathay(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp,
                                      page=_tpage)
                rs = nhadathay.crawl()
                self.return_result(rs)

        elif _site == 19:
            _type = 1
            muabanchinhchu = Muabanchinhchu(_provin, _type, progress_cb, mess_cb, start_page=_startp, end_page=_endp, page=_tpage)
            rs = muabanchinhchu.crawl()
            self.return_result(rs)

        self.btnStart.setDisabled(False)
        logging.info("Finished in: %s", time.time() - start)

    def start(self):
        if self.isRunning:
            self.isRunning = False
            set_running(False)
            self.is_stop = True
            self.btnStart.setText('START')
            self.btnStart.setDisabled(True)
            self.btnStart.setStyleSheet("background-color: rgb(200, 200, 200);")
            self.log('Stop. Đợi luồng hoàn thành trước khi dừng')
        else:
            self.isRunning = True
            self.is_stop = False
            set_running(True)
            self.btnStart.setText('STOP')

            self.progressBar.show()
            self.lbl_sttpage.show()
            self.listWidget_2.show()
            self.lbl_sttpage.setText('Trang ' + self.spinStartPage.text())

            # Pass the function to execute
            worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
            worker.signals.result.connect(self.print_output)
            worker.signals.finished.connect(self.thread_complete)
            worker.signals.progress.connect(self.progress_fn)
            worker.signals.mess.connect(self.get_mess)

            # Execute
            self.threadpool.start(worker)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    if args.site:
        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_MainWindow()
        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())
    else:
        login = Login()

        if login.exec_() == QtWidgets.QDialog.Accepted:
            MainWindow = QtWidgets.QMainWindow()
            ui = Ui_MainWindow()
            ui.setupUi(MainWindow)
            MainWindow.show()
            sys.exit(app.exec_())
