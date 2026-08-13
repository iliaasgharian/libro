import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize

from styles.styles import APP_STYLE
from PyQt5.QtGui import QIcon

from component.book.book_menu import BookWin
from component.author.Author_menu import AuthorWin
from component.category.Catergory_menu import CategoryWin
from component.designer.Designer_menu import DesignerWin
from component.language.Language_menu import LanguageWin
from component.publisher.Publisher_menu import PublisherWin
from component.resource.Resource_menu import ResourceWin
from component.translator.Translator_menu import TranslatorWin


from component.author.Author_form import AuthorForm
from component.book.Book_form import BookForm
from component.category.category_form import CategoryForm
from component.designer.designer_form import DesignerForm
from component.language.language_form import LanguageForm
from component.publisher.publisher_form import PublisherForm
from component.resource.resource_form import ResourceForm
from component.translator.translator_form import TransForm

from component.book.BookFilterForm import BookFilterForm
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Libro Library")
        self.setGeometry(100, 100, 900, 400)
        self.setup_menu()
        self.setup_central_widget()


    def setup_menu(self):
        menu = self.menuBar()

        book_menu = menu.addMenu("Book")
        member_menu = menu.addMenu("Members")
        Setting_menu = menu.addMenu("Settings")
        help_menu =menu.addMenu("Help")

        book_menu.addAction(QAction("Add", self))
        book_menu.addAction(QAction("Edit", self))
        book_menu.addAction(QAction("Delete", self))
        book_menu.addAction(QAction("Search", self))

        member_menu.addAction(QAction("Add", self))
        member_menu.addAction(QAction("Edit", self))
        member_menu.addAction(QAction("Delete", self))
        member_menu.addAction(QAction("Search", self))

        Setting_menu.addAction(QAction("Theme", self))
        Setting_menu.addAction(QAction("Notification", self))

        help_menu.addAction(QAction("Setting", self))
        help_menu.addAction(QAction("FAQ", self))

        exit_action = QAction("Exit", self)
        help_menu.addAction(exit_action)
        exit_action.triggered.connect(self.close)

    def activate_side_button(self, active_button):

        for btn in self.side_buttons:
            if btn is active_button:
                btn.setStyleSheet("background-color: red; border: none;")
            else:
                btn.setStyleSheet("")

    def setup_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        left_panell = QWidget()
        left_panell.setObjectName("left_panell")
        left_panell.setFixedWidth(45)
        left_layout2 = QVBoxLayout(left_panell)
        left_layout2.setContentsMargins(0, 7, 2, 0)
        left_layout2.setSpacing(0)

        button_book = QPushButton("")
        button_book.setIcon(QIcon("img/book(w).svg"))
        button_book.setObjectName("sideButton")

        button_user = QPushButton("")
        button_user.setIcon(QIcon("img/user(w).svg"))
        button_user.setObjectName("sideButton")

        button_author = QPushButton("")
        button_author.setIcon(QIcon("img/pencil-alt(W).svg"))
        button_author.setObjectName("sideButton")

        button_publisher = QPushButton("")
        button_publisher.setIcon(QIcon("img/newspaper(W).svg"))
        button_publisher.setObjectName("sideButton")

        button_trans = QPushButton("")
        button_trans.setIcon(QIcon("img/earth-americas(W).svg"))
        button_trans.setObjectName("sideButton")

        button_language = QPushButton("")
        button_language.setIcon(QIcon("img/language(W).svg"))
        button_language.setObjectName("sideButton")

        button_category = QPushButton("")
        button_category.setIcon(QIcon("img/layer-group(W).svg"))
        button_category.setObjectName("sideButton")

        button_designer = QPushButton("")
        button_designer.setIcon(QIcon("img/compass-drafting(W).svg"))
        button_designer.setObjectName("sideButton")

        button_resources = QPushButton("")
        button_resources.setIcon(QIcon("img/file-brackets-curly(W).svg"))
        button_resources.setObjectName("sideButton")


        self.side_buttons = [
            button_book, button_user, button_author, button_publisher,
            button_trans, button_language, button_category,
            button_designer, button_resources
        ]


        left_layout2.addWidget(button_book)
        left_layout2.addWidget(button_user)
        left_layout2.addWidget(button_author)
        left_layout2.addWidget(button_publisher)
        left_layout2.addWidget(button_trans)
        left_layout2.addWidget(button_language)
        left_layout2.addWidget(button_category)
        left_layout2.addWidget(button_designer)
        left_layout2.addWidget(button_resources)

        left_layout2.addStretch()

        left_panel = QWidget()
        left_panel.setObjectName("left_panel")
        left_panel.setMinimumWidth(180)
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)


        self.book_page=BookWin()
        self.author_page=AuthorWin()
        self.category_page=CategoryWin()
        self.designer_page=DesignerWin()
        self.language_page=LanguageWin()
        self.publisher_page=PublisherWin()
        self.resource_page=ResourceWin()
        self.translator_page=TranslatorWin()


        self.empty_left_page = QWidget()
        self.empty_left_page.setObjectName("empty_left_page")

        self.left_stack=QStackedWidget()

        self.left_stack.addWidget(self.empty_left_page)
        self.left_stack.addWidget(self.book_page)
        self.left_stack.addWidget(self.author_page)
        self.left_stack.addWidget(self.category_page)
        self.left_stack.addWidget(self.designer_page)
        self.left_stack.addWidget(self.language_page)
        self.left_stack.addWidget(self.publisher_page)
        self.left_stack.addWidget(self.resource_page)
        self.left_stack.addWidget(self.translator_page)

        left_layout.addWidget(self.left_stack)
        button_book.clicked.connect(lambda: (self.left_stack.setCurrentIndex(1), self.activate_side_button(button_book)))
        button_author.clicked.connect(lambda: (self.left_stack.setCurrentIndex(2), self.activate_side_button(button_author)))
        button_category.clicked.connect(lambda: (self.left_stack.setCurrentIndex(3), self.activate_side_button(button_category)))
        button_designer.clicked.connect(lambda: (self.left_stack.setCurrentIndex(4), self.activate_side_button(button_designer)))
        button_language.clicked.connect(lambda: (self.left_stack.setCurrentIndex(5), self.activate_side_button(button_language)))
        button_publisher.clicked.connect(lambda: (self.left_stack.setCurrentIndex(6), self.activate_side_button(button_publisher)))
        button_resources.clicked.connect(lambda: (self.left_stack.setCurrentIndex(7), self.activate_side_button(button_resources)))
        button_trans.clicked.connect(lambda: (self.left_stack.setCurrentIndex(8), self.activate_side_button(button_trans)))
        button_user.clicked.connect(lambda: self.activate_side_button(button_user))



        left_layout.addStretch()
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.book_form = BookForm()
        self.author_form = AuthorForm()
        self.category_form = CategoryForm()
        self.designer_form = DesignerForm()
        self.language_form = LanguageForm()
        self.publisher_form= PublisherForm()
        self.resource_form= ResourceForm()
        self.trans_form= TransForm()

        self.book_filter_form = BookFilterForm()


        self.welcome_page = QWidget()
        self.welcome_page.setObjectName("welcome_page")
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_label = QLabel("Libro")

        welcome_label.setObjectName("welcomeLabel")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("""
            QLabel#welcomeLabel {
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 64px;
                font-weight: 700;
                color: #2c3e50;
                letter-spacing: 3.1px;
            }
        """)
        welcome_layout.addWidget(welcome_label)

        self.right_stack = QStackedWidget()
        self.right_stack.addWidget(self.welcome_page)
        self.right_stack.addWidget(self.book_form)
        self.right_stack.addWidget(self.category_form)
        self.right_stack.addWidget(self.author_form)
        self.right_stack.addWidget(self.designer_form)
        self.right_stack.addWidget(self.language_form)
        self.right_stack.addWidget(self.publisher_form)
        self.right_stack.addWidget(self.resource_form)
        self.right_stack.addWidget(self.trans_form)

        self.right_stack.addWidget(self.book_filter_form)


        self.author_form.right_stack = self.right_stack
        self.category_form.right_stack=self.right_stack
        self.designer_form.right_stack = self.right_stack
        self.language_form.right_stack = self.right_stack
        self.publisher_form.right_stack = self.right_stack
        self.resource_form.right_stack = self.right_stack
        self.trans_form.right_stack = self.right_stack





        self.author_page.author_clicked.connect(self.author_form.on_author_clicked)
        self.category_page.category_clicked.connect(self.category_form.on_category_clicked)
        self.designer_page.designer_clicked.connect(self.designer_form.on_designers_clicked)
        self.language_page.language_clicked.connect(self.language_form.on_language_clicked)
        self.publisher_page.publisher_clicked.connect(self.publisher_form.on_publisher_clicked)
        self.resource_page.resource_clicked.connect(self.resource_form.on_resource_clicked)
        self.translator_page.trans_clicked.connect(self.trans_form.on_translator_clicked)

        self.author_form.author_saved.connect( self.author_page.refresh)
        self.category_form.category_saved.connect( self.category_page.refresh)
        self.designer_form.designer_saved.connect(self.designer_page.refresh)
        self.language_form.language_saved.connect(self.language_page.refresh)
        self.publisher_form.publisher_saved.connect(self.publisher_page.refresh)
        self.resource_form.resource_saved.connect(self.resource_page.refresh)
        self.trans_form.translator_saved.connect(self.translator_page.refresh)


        self.book_page.book_clicked.connect(
            lambda: self.right_stack.setCurrentWidget(self.book_form)
        )
        self.book_page.add_clicked.connect(
            lambda: self.right_stack.setCurrentWidget(self.book_filter_form)
        )


        right_layout.addWidget(self.right_stack)
        main_layout.addWidget(left_panell)
        main_layout.addWidget(left_panel, 1)

        main_layout.addWidget(right_panel, 3)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())