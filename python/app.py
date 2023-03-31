from PyQt5.QtWidgets import \
    QApplication, \
    QWidget, \
    QMainWindow, \
    QFileDialog, \
    QInputDialog, \
    QLineEdit, \
    QDesktopWidget, \
    QPushButton, \
    QGridLayout, \
    QLabel, \
    QHBoxLayout, \
    QVBoxLayout, QMessageBox

from PyQt5.QtCore import \
    Qt, \
    QRect, QDir

from PyQt5.QtGui import \
    QPixmap, \
    QPainter, \
    QBrush, \
    QIcon

from qrcodegen import QrCode

from labelled_text_field import LabelledTextField
from labelled_int_field import LabelledIntField

import convert_url

import sys, os
import json


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "QR Code Generator"
        self.setWindowIcon(QIcon("./data/icon.png"))
        self.left = 5
        self.top = 5
        self.width = 640
        self.height = 480
        self.btn_file = QPushButton()
        self.btn_apply = QPushButton()
        self.btn_save = QPushButton()
        self.buttons = QHBoxLayout()
        self.buttons.addWidget(self.btn_file)
        self.buttons.addWidget(self.btn_apply)
        self.buttons.addWidget(self.btn_save)

        self.w = QWidget()
        self.grid = QGridLayout(self.w)
        self.preview = QLabel()
        self.setImageSize()

        self.filename = ""
        self.filename_display = QLabel()
        self.filename_display.setWordWrap(True)
        self.filename_display.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.filename_display.setMinimumWidth(int(self.width / 2.5))
        self.img_width = -1
        self.img_height = -1
        self.hasLoadedImage = False
        self.dimensions = QLabel()
        self.pm = None
        self.input_url = LabelledTextField("URL", hint="URL, e.g. https://www.google.com/")
        self.input_url.setMinimumWidth(200)
        self.input_url.getBody().returnPressed.connect(self.generateQrCode)
        self.input_url.setEnabled(False)
        self.qrcode = None

        self.qrcode_size = LabelledIntField("QR size (px)")
        self.qrcode_offset_x = LabelledIntField("X-offset (px)")
        self.qrcode_offset_y = LabelledIntField("Y-offset (px)")
        self.qrcode_size.setEnabled(False)
        self.qrcode_offset_x.setEnabled(False)
        self.qrcode_offset_y.setEnabled(False)

        self.config_offset = QHBoxLayout(self)
        self.config_offset.addWidget(self.qrcode_offset_x)
        self.config_offset.addWidget(self.qrcode_offset_y)

        self.config_w = QVBoxLayout(self)
        self.config_w.addWidget(self.input_url)
        self.config_w.addWidget(self.qrcode_size)
        self.config_w.addLayout(self.config_offset)

        self.qrcode_size.lineEdit.returnPressed.connect(self.draw)
        self.qrcode_offset_x.lineEdit.returnPressed.connect(self.draw)
        self.qrcode_offset_y.lineEdit.returnPressed.connect(self.draw)

        self.buttons_config = QHBoxLayout(self)
        self.btn_config_save = QPushButton()
        self.btn_config_load = QPushButton()

        self.buttons_config.addWidget(self.btn_config_load)
        self.buttons_config.addWidget(self.btn_config_save)

        self.input_url.getBody().returnPressed.connect(self.draw)
        self.rects = []
        self.initUI()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.draw()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setStyleSheet("background-color: LightSteelBlue;")
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowTitle(self.title)

        self.setCentralWidget(self.w)
        self.btn_file.setText("Select")
        self.btn_file.clicked.connect(self.openFileNameDialog)

        self.btn_apply.setText("Apply")
        self.btn_apply.clicked.connect(self.generateQrCode)
        self.btn_apply.clicked.connect(self.draw)

        self.btn_save.setText("Save")
        self.btn_save.clicked.connect(self.saveImage)

        self.btn_config_load.setText("Load Config")
        self.btn_config_load.clicked.connect(self.loadConfig)

        self.btn_config_save.setText("Save Config")
        self.btn_config_save.clicked.connect(self.saveConfig)

        # --- #
        self.grid.addWidget(self.preview, 1, 1, Qt.AlignCenter | Qt.AlignTop)
        self.grid.addLayout(self.buttons, 2, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.grid.addLayout(self.config_w, 1, 0, Qt.AlignLeft)
        self.grid.addLayout(self.buttons_config, 3, 0, Qt.AlignCenter)
        self.show()

    def openFileNameDialog(self):
        os.makedirs("./data/templates/", exist_ok=True)
        fname, _ = QFileDialog.getOpenFileName(self, "Select base image", "./data/templates", "Image files (*.jpg *.png)")
        if not fname:
            return
        self.processFileNameDialog(fname)

    def processFileNameDialog(self, filename: str):
        self.filename = filename
        self.pm = QPixmap(self.filename)
        self.img_width = self.pm.width()
        self.img_height = self.pm.height()

        self.dimensions.setText(f"Dimensions: {self.img_width}px by {self.img_height}px")
        self.filename_display.setText(self.filename)
        new_qrcode_size = int(min(self.img_width, self.img_height) / 2.5)
        self.qrcode_size.setValue(new_qrcode_size)
        self.qrcode_offset_x.setValue(int((self.img_width - new_qrcode_size) / 2.))
        self.qrcode_offset_y.setValue(int((self.img_height - new_qrcode_size) / 2.))
        self.pm = self.pm.scaled(self.preview.width(), self.preview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview.setFixedSize(self.pm.width(), self.pm.height())
        self.draw()
        if not self.hasLoadedImage:
            self.hasLoadedImage = True
            self.grid.addWidget(self.dimensions, 0, 1, Qt.AlignCenter)
            self.grid.addWidget(self.filename_display, 2, 1, Qt.AlignCenter)
            self.input_url.setEnabled(True)
            self.qrcode_size.setEnabled(True)
            self.qrcode_offset_x.setEnabled(True)
            self.qrcode_offset_y.setEnabled(True)

    def saveImage(self):
        if not self.filename:
            QMessageBox.warning(self, "No template selected", "You must first select a template.")
            return
        if not self.input_url.text():
            QMessageBox.warning(self, "No URL given", "You must first specify a URL to convert.")
            return
        target, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath(), '*.png')
        if not target:
            return
        convert_url.to_image(self.qrcode, target, self.filename, self.qrcode_size.getValue(), self.qrcode_offset_x.getValue(), self.qrcode_offset_y.getValue())

    def setImageSize(self):
        imsize = int(0.8 * min(self.width, self.height))
        self.preview.setMinimumSize(imsize, imsize)

    def generateQrCode(self):
        if not self.input_url.text():
            return
        self.qrcode = QrCode.encode_text(self.input_url.text(), QrCode.Ecc.LOW)
        self.draw()

    def draw(self):

        if not self.pm:
            return
        self.preview.setPixmap(self.pm)
        if not self.qrcode:
            return
        self.pm = QPixmap(self.filename).scaled(self.preview.width(), self.preview.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        qrd = QPainter(self.pm)
        qrd.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        self.rects = []

        x0 = int((self.qrcode_offset_x.getValue() / self.img_width) * self.preview.width())
        y0 = int((self.qrcode_offset_y.getValue() / self.img_height) * self.preview.height())

        d = int((self.qrcode_size.getValue() * self.preview.width()) / (self.img_width * self.qrcode.get_size()))
        for x in range(self.qrcode.get_size()):
            for y in range(self.qrcode.get_size()):
                if self.qrcode.get_module(x, y):
                    self.rects.append(QRect(x0 + x*d, y0 + y*d, d, d))
        qrd.drawRects(self.rects)

    def loadConfig(self):
        os.makedirs("./data/configs/", exist_ok=True)
        conffile, _ = QFileDialog.getOpenFileName(self, "Select configuration", "./data/configs", "Config file (*.qrconfig)")
        if not conffile:
            return
        with open(conffile, 'r') as file:
            qrconf = json.load(file)
            if "image" in qrconf:
                self.processFileNameDialog(qrconf["image"])
            if "size" in qrconf:
                self.qrcode_size.lineEdit.setText(str(int(qrconf["size"])))
            if "dx" in qrconf:
                self.qrcode_offset_x.lineEdit.setText(str(int(qrconf["dx"])))
            if "dy" in qrconf:
                self.qrcode_offset_y.lineEdit.setText(str(int(qrconf["dy"])))
        self.generateQrCode()
        self.draw()

    def saveConfig(self):
        os.makedirs("./data/configs/", exist_ok=True)
        if not self.filename:
            QMessageBox.warning(self, "Invalid config", "Config file must contain path to a file")
            return
        target, _ = QFileDialog.getSaveFileName(self, 'Save Config', './data/configs', 'Config file (*.qrconfig)')
        if not target:
            return
        conf = dict()
        conf["image"] = self.filename
        conf["size"] = self.qrcode_size.getValue()
        conf["dx"] = self.qrcode_offset_x.getValue()
        conf["dy"] = self.qrcode_offset_y.getValue()
        with open(target, "w+") as dumpfile:
            json.dump(conf, dumpfile)


if __name__ == "__main__":
    app = QApplication([])
    ex = App()
    sys.exit(app.exec_())
