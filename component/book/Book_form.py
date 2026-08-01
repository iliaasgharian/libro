from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from adapters.author_data_adapter import AuthorDataAdapter

class BookForm(QWidget):

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.btn_save = QPushButton("👉👈")
        layout.addWidget(self.btn_save)

