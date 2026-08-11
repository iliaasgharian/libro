from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QCursor, QIntValidator, QDoubleValidator

from adapters.author_data_adapter import AuthorDataAdapter
from adapters.publisher_data_adapter import PublisherDataAdapter
from adapters.category_data_adapter import CategoryDataAdapter
from adapters.language_data_adapter import LanguageDataAdapter
from adapters.resource_data_adapter import ResourcesDataAdapter
from adapters.translator_data_adapter import TranslatorDataAdapter
from adapters.designer_data_adapter import DesignerDataAdapter
from adapters.book_data_adapter import BookDataAdapter

from models.book import Book


def _display_text(item):
    """
    Adapter objects don't all share the same field name
    (Book uses .title, most others use .name) so try both.
    """
    for attr in ("name", "title"):
        if hasattr(item, attr):
            return getattr(item, attr)
    return str(item)


class MultiSelectDialog(QDialog):
    """
    A full page/dialog for picking several options out of a list,
    with a live search box at the top that filters the list as you type.
    """

    def __init__(self, items, checked_ids, title="Select items", parent=None):
        super().__init__(parent)
        self.setObjectName("multiSelectDialog")
        self.setWindowTitle(title)
        self.resize(360, 440)

        self._items = list(items)          # list of (id, display_text)
        self._checked_ids = set(checked_ids)
        self._checkboxes = {}              # id -> QCheckBox
        self._rows = {}                    # id -> row widget (for hide/show while searching)

        self.setStyleSheet("""
            QDialog#multiSelectDialog {
                background-color: #202020;
            }
            QLineEdit#dialogSearchInput {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 6px 10px;
            }
            QScrollArea#multiSelectScroll {
                background-color: #202020;
                border: none;
            }
            QScrollArea#multiSelectScroll > QWidget > QWidget {
                background-color: #202020;
            }
            QWidget#multiSelectListContent {
                background-color: #202020;
            }
            QCheckBox {
                color: #f0f0f0;
                padding: 6px 4px;
                background-color: transparent;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #5a5a5a;
                border-radius: 3px;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:hover {
                border: 1px solid #7C3AED;
            }
            QCheckBox::indicator:checked {
                background-color: #7C3AED;
                border: 1px solid #7C3AED;
            }
            QCheckBox:hover {
                background-color: #2f2f2f;
                border-radius: 4px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #d0d0d0;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background: #ffffff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: transparent;
            }
            QLabel#noResultsLabel {
                color: #888888;
                padding: 10px;
            }
            QPushButton#btn_send {
                background-color: #7C3AED;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 16px;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("dialogSearchInput")
        self.search_edit.setPlaceholderText("Search...")
        self.search_edit.textChanged.connect(self.filter_items)
        layout.addWidget(self.search_edit)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("multiSelectScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.list_content = QWidget()
        self.list_content.setObjectName("multiSelectListContent")
        self.list_layout = QVBoxLayout(self.list_content)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(2)

        for item_id, text in self._items:
            checkbox = QCheckBox(text)
            checkbox.setChecked(item_id in self._checked_ids)
            checkbox.stateChanged.connect(
                lambda state, i=item_id: self._on_check_changed(i, state)
            )
            self._checkboxes[item_id] = checkbox
            self.list_layout.addWidget(checkbox)

        self.no_results_label = QLabel("No matches found")
        self.no_results_label.setObjectName("noResultsLabel")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.hide()
        self.list_layout.addWidget(self.no_results_label)

        self.list_layout.addStretch()
        self.scroll.setWidget(self.list_content)
        layout.addWidget(self.scroll)

        btn_layout = QHBoxLayout()
        self.btn_clear = QPushButton("Clear all")
        self.btn_done = QPushButton("Done")
        self.btn_done.setObjectName("btn_send")
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_done)
        layout.addLayout(btn_layout)

        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_done.clicked.connect(self.accept)

    def _on_check_changed(self, item_id, state):
        if state == Qt.Checked:
            self._checked_ids.add(item_id)
        else:
            self._checked_ids.discard(item_id)

    def filter_items(self, text):
        text = text.strip().lower()
        any_visible = False
        for item_id, checkbox in self._checkboxes.items():
            match = text in checkbox.text().lower()
            checkbox.setVisible(match)
            any_visible = any_visible or match
        self.no_results_label.setVisible(not any_visible)

    def clear_all(self):
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)

    def selected_ids(self):
        return list(self._checked_ids)


class MultiSelectBox(QWidget):
    """
    A compact field for picking several options: a small read-only
    box that shows the currently selected names, plus a tiny "..."
    button next to it that opens the full-page picker dialog.
    Sized to its content, not stretched across the row.
    """
    selection_changed = pyqtSignal()

    def __init__(self, title="Select...", placeholder="None selected", parent=None):
        super().__init__(parent)
        self.setObjectName("multiSelectBox")
        self.title = title
        self.placeholder = placeholder

        self._items = {}          # id -> display text
        self._objects = {}        # id -> original adapter object
        self._checked_ids = set()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.display = QLineEdit()
        self.display.setObjectName("multiSelectDisplay")
        self.display.setReadOnly(True)
        self.display.setPlaceholderText(placeholder)
        self.display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.display.setCursor(QCursor(Qt.ArrowCursor))

        self.open_btn = QPushButton("...")
        self.open_btn.setObjectName("multiSelectOpenBtn")
        self.open_btn.setFixedWidth(32)
        self.open_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.open_btn.clicked.connect(self._show_dialog)

        layout.addWidget(self.display)
        layout.addWidget(self.open_btn)

        self.setStyleSheet("""
            QLineEdit#multiSelectDisplay {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 25px;
            }
            QPushButton#multiSelectOpenBtn {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                min-height: 25px;
            }
            QPushButton#multiSelectOpenBtn:hover {
                border: 1px solid #7C3AED;
                color: #7C3AED;
            }
        """)

    def set_items(self, items):
        """items: iterable of (id, display_text, original_object)"""
        self._items = {}
        self._objects = {}
        for item_id, text, obj in items:
            self._items[item_id] = text
            self._objects[item_id] = obj
        self._checked_ids.clear()
        self._update_text()

    def _show_dialog(self):
        items = list(self._items.items())
        dialog = MultiSelectDialog(items, self._checked_ids, title=self.title, parent=self.window())
        if dialog.exec_() == QDialog.Accepted:
            self._checked_ids = set(dialog.selected_ids())
            self._update_text()
            self.selection_changed.emit()

    def _update_text(self):
        if not self._checked_ids:
            self.display.setText("")
            return
        selected_texts = [self._items[i] for i in self._checked_ids if i in self._items]
        self.display.setText(", ".join(selected_texts))

    def selected_ids(self):
        return list(self._checked_ids)

    def selected_objects(self):
        return [self._objects[i] for i in self._checked_ids if i in self._objects]

    def clear_selection(self):
        self._checked_ids.clear()
        self._update_text()


class BookFilterForm(QWidget):
    filters_applied = pyqtSignal(dict)
    book_saved = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setObjectName("book_filter_form")
        self.setup_ui()
        self.load_data()

    def _labeled_field(self, label_text, widget, label_width=110):
        """Builds a horizontal row: label on the left, input on the right."""
        row = QHBoxLayout()
        row.setSpacing(8)
        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        row.addWidget(label)
        row.addWidget(widget)
        return row

    def _field_row(self, label1, widget1, label2, widget2):
        """Builds a horizontal row with two label+input pairs side by side."""
        row = QHBoxLayout()
        row.setSpacing(20)
        row.addLayout(self._labeled_field(label1, widget1))
        row.addLayout(self._labeled_field(label2, widget2))
        return row

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Add Book")
        title.setObjectName("filterTitle")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        # --- Title / Product code ---
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Book title...")

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("e.g. 12345")
        self.code_edit.setValidator(QIntValidator(0, 999999999, self))

        layout.addLayout(self._field_row(
            "Title", self.title_edit,
            "Product Code", self.code_edit,
        ))

        # --- Age group / Release date ---
        self.age_group_edit = QLineEdit()
        self.age_group_edit.setPlaceholderText("e.g. Adult")

        self.release_date_edit = QDateEdit()
        self.release_date_edit.setCalendarPopup(True)
        self.release_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.release_date_edit.setDate(QDate.currentDate())

        layout.addLayout(self._field_row(
            "Age Group", self.age_group_edit,
            "Release Date", self.release_date_edit,
        ))

        # --- Price / Publisher ---
        self.price_edit = QLineEdit()
        self.price_edit.setPlaceholderText("e.g. 150000")
        self.price_edit.setValidator(QDoubleValidator(0, 999999999, 2, self))

        self.publisher_combo = QComboBox()
        self.publisher_combo.setObjectName("publisher_combo")
        try:
            self.publisher_combo.setPlaceholderText("Select publisher...")
        except AttributeError:
            pass  # older PyQt5 (<5.15) has no setPlaceholderText

        layout.addLayout(self._field_row(
            "Price", self.price_edit,
            "Publisher", self.publisher_combo,
        ))

        # --- Authors (multi select) ---
        self.author_multi = MultiSelectBox(title="Select authors...")
        layout.addLayout(self._labeled_field("Authors", self.author_multi))

        # --- Languages (multi select) ---
        self.language_multi = MultiSelectBox(title="Select languages...")
        layout.addLayout(self._labeled_field("Languages", self.language_multi))

        # --- Categories (multi select) ---
        self.category_multi = MultiSelectBox(title="Select categories...")
        layout.addLayout(self._labeled_field("Categories", self.category_multi))

        # --- Cover Designers (multi select) ---
        self.designer_multi = MultiSelectBox(title="Select cover designers...")
        layout.addLayout(self._labeled_field("Cover Designers", self.designer_multi))

        # --- Translators (multi select) ---
        self.translator_multi = MultiSelectBox(title="Select translators...")
        layout.addLayout(self._labeled_field("Translators", self.translator_multi))

        # --- Resources (multi select) ---
        self.resource_multi = MultiSelectBox(title="Select resources...")
        layout.addLayout(self._labeled_field("Resources", self.resource_multi))

        layout.addStretch()

        btn_layout = QHBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_apply = QPushButton("Add book")
        self.btn_apply.setObjectName("btn_send")
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_apply)
        layout.addLayout(btn_layout)

        self.btn_reset.clicked.connect(self.reset_filters)
        self.btn_apply.clicked.connect(self.apply_filters)

    def load_data(self):
        # Publisher (single select, starts with no selection)
        self.publisher_combo.clear()
        for publisher in PublisherDataAdapter.get_all():
            self.publisher_combo.addItem(_display_text(publisher), publisher)
        self.publisher_combo.setCurrentIndex(-1)

        # Authors (multi select)
        authors = [
            (getattr(a, "id", _display_text(a)), _display_text(a), a)
            for a in AuthorDataAdapter.get_all()
        ]
        self.author_multi.set_items(authors)

        # Languages (multi select)
        languages = [
            (getattr(l, "id", _display_text(l)), _display_text(l), l)
            for l in LanguageDataAdapter.get_all()
        ]
        self.language_multi.set_items(languages)

        # Categories (multi select)
        categories = [
            (getattr(c, "id", _display_text(c)), _display_text(c), c)
            for c in CategoryDataAdapter.get_all()
        ]
        self.category_multi.set_items(categories)

        # Cover designers (multi select)
        designers = [
            (getattr(d, "id", _display_text(d)), _display_text(d), d)
            for d in DesignerDataAdapter.get_all()
        ]
        self.designer_multi.set_items(designers)

        # Translators (multi select)
        translators = [
            (getattr(t, "id", _display_text(t)), _display_text(t), t)
            for t in TranslatorDataAdapter.get_all()
        ]
        self.translator_multi.set_items(translators)

        # Resources (multi select)
        resources = [
            (getattr(r, "id", _display_text(r)), _display_text(r), r)
            for r in ResourcesDataAdapter.get_all()
        ]
        self.resource_multi.set_items(resources)

    def reset_filters(self):
        self.title_edit.clear()
        self.code_edit.clear()
        self.age_group_edit.clear()
        self.release_date_edit.setDate(QDate.currentDate())
        self.price_edit.clear()

        self.publisher_combo.setCurrentIndex(-1)
        self.author_multi.clear_selection()
        self.language_multi.clear_selection()
        self.category_multi.clear_selection()
        self.designer_multi.clear_selection()
        self.translator_multi.clear_selection()
        self.resource_multi.clear_selection()

    def get_filters(self):
        return {
            "title": self.title_edit.text().strip(),
            "product_code": self.code_edit.text().strip(),
            "age_group": self.age_group_edit.text().strip(),
            "release_date": self.release_date_edit.date().toString("yyyy-MM-dd"),
            "price": self.price_edit.text().strip(),
            "publisher_id": self.publisher_combo.currentData(),
            "author_ids": self.author_multi.selected_ids(),
            "language_ids": self.language_multi.selected_ids(),
            "category_ids": self.category_multi.selected_ids(),
            "designer_ids": self.designer_multi.selected_ids(),
            "translator_ids": self.translator_multi.selected_ids(),
            "resource_ids": self.resource_multi.selected_ids(),
        }

    def validate_filters(self):
        missing = []

        if not self.title_edit.text().strip():
            missing.append("Title")
        if not self.code_edit.text().strip():
            missing.append("Product Code")
        if not self.age_group_edit.text().strip():
            missing.append("Age Group")
        if not self.price_edit.text().strip():
            missing.append("Price")
        if self.publisher_combo.currentIndex() == -1:
            missing.append("Publisher")
        if not self.author_multi.selected_ids():
            missing.append("Authors")
        if not self.language_multi.selected_ids():
            missing.append("Languages")
        if not self.category_multi.selected_ids():
            missing.append("Categories")
        if not self.designer_multi.selected_ids():
            missing.append("Cover Designers")
        if not self.translator_multi.selected_ids():
            missing.append("Translators")
        if not self.resource_multi.selected_ids():
            missing.append("Resources")

        return missing

    def print_values(self, values):
        print("----- Add Book -----")
        for key, value in values.items():
            print(f"{key}: {value}")
        print("---------------------")

    def build_book(self):
        return Book(
            id=None,
            title=self.title_edit.text().strip(),
            product_code=int(self.code_edit.text().strip()),
            categories=self.category_multi.selected_objects(),
            age_group=self.age_group_edit.text().strip(),
            authors=self.author_multi.selected_objects(),
            publisher=self.publisher_combo.currentData(),
            release_date=self.release_date_edit.date().toPyDate(),
            price=float(self.price_edit.text().strip()),
            languages=self.language_multi.selected_objects(),
            cover_designers=self.designer_multi.selected_objects(),
            translators=self.translator_multi.selected_objects(),
            resources=self.resource_multi.selected_objects(),
        )

    def apply_filters(self):
        missing = self.validate_filters()
        if missing:
            QMessageBox.warning(
                self,
                "Missing fields",
                "PLease Enter These:\n- " + "\n- ".join(missing),
            )
            return

        values = self.get_filters()
        self.print_values(values)

        book = self.build_book()
        try:
            BookDataAdapter.insert(book)
        except Exception as e:
            QMessageBox.critical(self, "Error ", str(e))
            return

        QMessageBox.information(self, "Success", "The book was successfully added.")
        self.filters_applied.emit(values)
        self.book_saved.emit()
        self.reset_filters()