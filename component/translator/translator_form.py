from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from adapters.translator_data_adapter import TranslatorDataAdapter

import os

class TransForm(QWidget):
    translator_saved = pyqtSignal()

    def __init__(self, right_stack=None):
        super().__init__()
        self.setObjectName("form")
        self.right_stack = right_stack
        style_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "styles",
            "formstyles.qss"
        )

        with open(style_path, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        self.setup_ui()
    def save(self):
        language = self.txt_birth_date.text()
        print(language)
        s=TranslatorDataAdapter.update(id=int(self.txt_id.text()),
                                   name=self.txt_name.text(),
                                    language=self.txt_birth_date.text())
        print("Translator {} saved".format(self.txt_id.text()))
        self.translator_saved.emit()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)


        #title
        til=QHBoxLayout()
        til.setSpacing(10)
        label_til = QLabel("Translators")
        label_til.setObjectName("title")
        label_til.setFixedWidth(90)
        til.addWidget(label_til, alignment=Qt.AlignLeft)
        layout.addLayout(til)
        # Id
        row_id = QHBoxLayout()
        row_id.setSpacing(10)
        label_id = QLabel("Id:")
        label_id.setFixedWidth(80)
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        row_id.addWidget(label_id, alignment=Qt.AlignTop)
        row_id.addWidget(self.txt_id, alignment=Qt.AlignTop)
        layout.addLayout(row_id)
        # Name
        row_name = QHBoxLayout()
        row_name.setSpacing(10)
        label_name = QLabel("Name:")
        label_name.setFixedWidth(80)
        self.txt_name = QLineEdit()
        row_name.addWidget(label_name, alignment=Qt.AlignTop)
        row_name.addWidget(self.txt_name, alignment=Qt.AlignTop)
        layout.addLayout(row_name)
        # address
        row_birth = QHBoxLayout()
        row_birth.setSpacing(10)
        label_birth = QLabel("language:")
        label_birth.setFixedWidth(80)
        self.txt_birth_date = QLineEdit()
        row_birth.addWidget(label_birth, alignment=Qt.AlignTop)
        row_birth.addWidget(self.txt_birth_date, alignment=Qt.AlignTop)
        layout.addLayout(row_birth)



        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def on_translator_clicked(self, name):
        if self.right_stack is not None:
            self.right_stack.setCurrentWidget(self)
        trans = TranslatorDataAdapter.search(name=name)[0]

        self.txt_id.setText(str(trans.id))
        self.txt_name.setText(trans.name)
        self.txt_birth_date.setText(trans.languages)


