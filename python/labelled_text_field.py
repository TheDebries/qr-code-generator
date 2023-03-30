from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt5.QtGui import QFont


class LabelledTextField(QWidget):
    def __init__(self, title, initial_value=None, hint=None):
        QWidget.__init__(self)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel()
        self.label.setText(title)
        self.label.setFixedWidth(150)
        self.label.setFont(QFont("Arial", weight=QFont.Bold))
        layout.addWidget(self.label)

        self.lineEdit = QLineEdit(self)
        self.lineEdit.setFixedWidth(150)

        if initial_value is not None:
            self.lineEdit.setText(str(initial_value))
        if hint is not None:
            self.lineEdit.setPlaceholderText(str(hint))
        layout.addWidget(self.lineEdit)
        layout.addStretch()

    def setLabelWidth(self, width):
        self.label.setFixedWidth(width)

    def setInputWidth(self, width):
        self.lineEdit.setFixedWidth(width)

    def text(self):
        return str(self.lineEdit.text())

    def getBody(self):
        return self.lineEdit
