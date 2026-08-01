from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from adapters.author_data_adapter import AuthorDataAdapter
from datetime import datetime
import os

class AuthorForm(QWidget):
    author_saved = pyqtSignal()
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
        s=AuthorDataAdapter.update(id=int(self.txt_id.text()),
                                   name=self.txt_name.text(),
                                   nationality=self.txt_nationality.text(),
                                   birthdate = datetime.strptime(self.txt_birth_date.text(), "%Y-%m-%d").date())
        print("Author {} saved".format(self.txt_id.text()))
        self.author_saved.emit()
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        #title
        til=QHBoxLayout()
        til.setSpacing(10)
        label_til = QLabel("Authors")
        label_til.setObjectName("title")
        label_til.setFixedWidth(80)
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

        # Birth Date
        row_birth = QHBoxLayout()
        row_birth.setSpacing(10)
        label_birth = QLabel("Birth Date:")
        label_birth.setFixedWidth(80)
        self.txt_birth_date = QLineEdit()
        row_birth.addWidget(label_birth, alignment=Qt.AlignTop)
        row_birth.addWidget(self.txt_birth_date, alignment=Qt.AlignTop)
        layout.addLayout(row_birth)

        # Nationality
        row_nat = QHBoxLayout()
        row_nat.setSpacing(10)
        label_nat = QLabel("Nationality:")
        label_nat.setFixedWidth(80)
        self.txt_nationality = QLineEdit()
        row_nat.addWidget(label_nat, alignment=Qt.AlignTop)
        row_nat.addWidget(self.txt_nationality, alignment=Qt.AlignTop)
        layout.addLayout(row_nat)

        self.btn_save = QPushButton("Save")
        self.btn_save.clicked.connect(self.save)
        layout.addWidget(self.btn_save)
        layout.addStretch()

    def on_author_clicked(self, name):
        if self.right_stack is not None:
            self.right_stack.setCurrentWidget(self)
        author=AuthorDataAdapter.search(name=name)[0]


        self.txt_id.setText(str(author.id))
        self.txt_name.setText(author.name)
        self.txt_nationality.setText(author.nationality)
        self.txt_birth_date.setText(author.birthdate)

