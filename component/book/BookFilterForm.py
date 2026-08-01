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


class MultiSelectBox(QPushButton):
    """
    A dropdown-like box that lets the user pick several options.
    Clicking it opens a checklist menu; selected options are shown
    (comma separated) inside the box itself, like a mini "chip" field.
    """
    selection_changed = pyqtSignal()

    def __init__(self, placeholder="Select...", parent=None):
        super().__init__(parent)
        self.setObjectName("multiSelectBox")
        self.placeholder = placeholder
        self.setText(placeholder)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setLayoutDirection(Qt.LeftToRight)

        self._items = {}          # id -> display text
        self._objects = {}        # id -> original adapter object
        self._checked_ids = set()

        self.menu = QMenu(self)
        self.menu.setObjectName("multiSelectMenu")

        self.setStyleSheet("""
            QPushButton#multiSelectBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #4a4a4a;
                border-radius: 6px;
                padding: 4px 8px;
                min-height: 25px;
                text-align: left;
            }
            QPushButton#multiSelectBox:hover {
                border: 1px solid #0078d7;
            }
            QMenu#multiSelectMenu {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QMenu#multiSelectMenu::item {
                padding: 6px 10px;
                border-radius: 4px;
            }
            QMenu#multiSelectMenu::item:selected {
                background-color: #4a4a4a;
            }
        """)

        self.clicked.connect(self._show_menu)

    def set_items(self, items):
        """items: iterable of (id, display_text, original_object)"""
        self._items = {}
        self._objects = {}
        for item_id, text, obj in items:
            self._items[item_id] = text
            self._objects[item_id] = obj
        self._checked_ids.clear()
        self._rebuild_menu()
        self._update_text()

    def _rebuild_menu(self):
        self.menu.clear()
        for item_id, text in self._items.items():
            action = QWidgetAction(self.menu)
            checkbox = QCheckBox(text, self.menu)
            checkbox.setChecked(item_id in self._checked_ids)
            checkbox.stateChanged.connect(
                lambda state, i=item_id: self._on_check_changed(i, state)
            )
            action.setDefaultWidget(checkbox)
            self.menu.addAction(action)

    def _on_check_changed(self, item_id, state):
        if state == Qt.Checked:
            self._checked_ids.add(item_id)
        else:
            self._checked_ids.discard(item_id)
        self._update_text()
        self.selection_changed.emit()

    def _update_text(self):
        if not self._checked_ids:
            self.setText(self.placeholder)
            return
        selected_texts = [self._items[i] for i in self._checked_ids if i in self._items]
        self.setText(", ".join(selected_texts))

    def _show_menu(self):
        self.menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))

    def selected_ids(self):
        return list(self._checked_ids)

    def selected_objects(self):
        return [self._objects[i] for i in self._checked_ids if i in self._objects]

    def clear_selection(self):
        self._checked_ids.clear()
        self._rebuild_menu()
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
        self.author_multi = MultiSelectBox(placeholder="Select authors...")
        layout.addLayout(self._labeled_field("Authors", self.author_multi))

        # --- Languages (multi select) ---
        self.language_multi = MultiSelectBox(placeholder="Select languages...")
        layout.addLayout(self._labeled_field("Languages", self.language_multi))

        # --- Categories (multi select) ---
        self.category_multi = MultiSelectBox(placeholder="Select categories...")
        layout.addLayout(self._labeled_field("Categories", self.category_multi))

        # --- Cover Designers (multi select) ---
        self.designer_multi = MultiSelectBox(placeholder="Select cover designers...")
        layout.addLayout(self._labeled_field("Cover Designers", self.designer_multi))

        # --- Translators (multi select) ---
        self.translator_multi = MultiSelectBox(placeholder="Select translators...")
        layout.addLayout(self._labeled_field("Translators", self.translator_multi))

        # --- Resources (multi select) ---
        self.resource_multi = MultiSelectBox(placeholder="Select resources...")
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
            QMessageBox.critical(self, "Error", str(e))
            return

        QMessageBox.information(self, "Success", "The book was successfully added.")
        self.filters_applied.emit(values)
        self.book_saved.emit()
        self.reset_filters()