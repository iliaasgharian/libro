import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, pyqtSignal


from PyQt5.QtGui import QIcon
from adapters.book_data_adapter import BookDataAdapter
class BookWin(QWidget):
    book_clicked = pyqtSignal()
    add_clicked = pyqtSignal()
    def __init__(self):

        super().__init__()
        self.setObjectName("book_page")
        self.setup_ui()
    def setup_ui(self):
        self.setStyleSheet(open("styles/leftpanelstyles.qss").read())
        layout = QVBoxLayout(self)
        top_layout = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("search_input")
        self.search_edit.setPlaceholderText("search...")

        self.search_btn = QPushButton()
        self.search_btn.setObjectName("addbutton")
        self.search_btn.setIcon(QIcon("img/plus-large(W).svg"))
        self.search_btn.clicked.connect(self.add_clicked.emit)
        # self.search_edit.setFixedHeight()
        # self.search_btn.setFixedHeight(20)
        self.search_btn.setIconSize(QSize(15, 15))


        top_layout.addWidget(self.search_edit)
        top_layout.addWidget(self.search_btn)

        layout.addLayout(top_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(180)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFixedHeight(self.height())
        scroll.setContentsMargins(0, 0, 0, 0)

        content = QWidget()

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content.setObjectName("contentWidget")

        scroll.setObjectName("mainScroll")
        s=BookDataAdapter.get_all()

        for i in s :
            btn_add = QPushButton(i.title)
            btn_add.setObjectName("boButton")
            btn_add.clicked.connect(lambda: print("clicked book"))
            btn_add.clicked.connect(self.book_clicked.emit)
            content_layout.addWidget(btn_add)
        content_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll)