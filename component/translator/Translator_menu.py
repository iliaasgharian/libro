import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize,pyqtSignal


from PyQt5.QtGui import QIcon
from adapters.translator_data_adapter import TranslatorDataAdapter
class TranslatorWin(QWidget):
    trans_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("translator_page")
        self.setup_ui()
    def on_search(self, text):
        if text.strip():
            trans = TranslatorDataAdapter.search(name=text)
        else:
            trans = TranslatorDataAdapter.get_all()

        self.load_trans(trans)
    def load_trans(self, trans):

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        for tran in trans:
            btn = QPushButton(tran.name)
            btn.setObjectName("boButton")

            btn.clicked.connect(
                lambda checked, name=tran.name: self.trans_clicked.emit(name)
            )

            self.content_layout.addWidget(btn)

        self.content_layout.addStretch()
    def refresh(self):
        self.search_edit.clear()
        self.load_trans(TranslatorDataAdapter.get_all())

    def setup_ui(self):
            self.setStyleSheet(open("styles/leftpanelstyles.qss").read())

            layout = QVBoxLayout(self)

            top_layout = QHBoxLayout()

            self.search_edit = QLineEdit()
            self.search_edit.setObjectName("search_input")
            self.search_edit.setPlaceholderText("search...")
            self.search_edit.textEdited.connect(self.on_search)

            self.search_btn = QPushButton()
            self.search_btn.setObjectName("addbutton")
            self.search_btn.setIcon(QIcon("img/plus-large(W).svg"))
            self.search_btn.setIconSize(QSize(15, 15))

            top_layout.addWidget(self.search_edit)
            top_layout.addWidget(self.search_btn)

            layout.addLayout(top_layout)

            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setFixedWidth(180)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setContentsMargins(0, 0, 0, 0)
            scroll.setObjectName("mainScroll")

            self.content = QWidget()
            self.content.setObjectName("contentWidget")

            self.content_layout = QVBoxLayout(self.content)
            self.content_layout.setContentsMargins(0, 0, 0, 0)
            self.content_layout.setSpacing(0)

            scroll.setWidget(self.content)
            layout.addWidget(scroll)

            self.load_trans(TranslatorDataAdapter.get_all())

if __name__ == "__main__":
        app = QApplication(sys.argv)
        win = TranslatorWin()
        win.show()
        sys.exit(app.exec_())