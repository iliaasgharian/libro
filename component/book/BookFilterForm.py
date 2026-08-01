from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

from adapters.author_data_adapter import AuthorDataAdapter
from adapters.publisher_data_adapter import PublisherDataAdapter
from adapters.category_data_adapter import CategoryDataAdapter
from adapters.language_data_adapter import LanguageDataAdapter
from adapters.resource_data_adapter import ResourcesDataAdapter
from adapters.translator_data_adapter import TranslatorDataAdapter
from adapters.designer_data_adapter import DesignerDataAdapter


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
        """items: iterable of (id, display_text)"""
        self._items = {item_id: text for item_id, text in items}
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

    def clear_selection(self):
        self._checked_ids.clear()
        self._rebuild_menu()
        self._update_text()


class BookFilterForm(QWidget):
    filters_applied = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setObjectName("book_filter_form")
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("Add Book")
        title.setObjectName("filterTitle")
        title.setStyleSheet("font-size: 14pt; font-weight: bold;")
        layout.addWidget(title)

        # --- Publisher (single select, no default value) ---
        layout.addWidget(QLabel("Publisher"))
        self.publisher_combo = QComboBox()
        self.publisher_combo.setObjectName("publisher_combo")
        try:
            self.publisher_combo.setPlaceholderText("Select publisher...")
        except AttributeError:
            pass  # older PyQt5 (<5.15) has no setPlaceholderText
        layout.addWidget(self.publisher_combo)

        # --- Authors (multi select) ---
        layout.addWidget(QLabel("Authors"))
        self.author_multi = MultiSelectBox(placeholder="Select authors...")
        layout.addWidget(self.author_multi)

        # --- Languages (multi select) ---
        layout.addWidget(QLabel("Languages"))
        self.language_multi = MultiSelectBox(placeholder="Select languages...")
        layout.addWidget(self.language_multi)

        # --- Categories (multi select) ---
        layout.addWidget(QLabel("Categories"))
        self.category_multi = MultiSelectBox(placeholder="Select categories...")
        layout.addWidget(self.category_multi)

        # --- Cover Designers (multi select) ---
        layout.addWidget(QLabel("Cover Designers"))
        self.designer_multi = MultiSelectBox(placeholder="Select cover designers...")
        layout.addWidget(self.designer_multi)

        # --- Translators (multi select) ---
        layout.addWidget(QLabel("Translators"))
        self.translator_multi = MultiSelectBox(placeholder="Select translators...")
        layout.addWidget(self.translator_multi)

        # --- Resources (multi select) ---
        layout.addWidget(QLabel("Resources"))
        self.resource_multi = MultiSelectBox(placeholder="Select resources...")
        layout.addWidget(self.resource_multi)

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
            self.publisher_combo.addItem(_display_text(publisher), getattr(publisher, "id", None))
        self.publisher_combo.setCurrentIndex(-1)

        # Authors (multi select)
        authors = [
            (getattr(a, "id", _display_text(a)), _display_text(a))
            for a in AuthorDataAdapter.get_all()
        ]
        self.author_multi.set_items(authors)

        # Languages (multi select)
        languages = [
            (getattr(l, "id", _display_text(l)), _display_text(l))
            for l in LanguageDataAdapter.get_all()
        ]
        self.language_multi.set_items(languages)

        # Categories (multi select)
        categories = [
            (getattr(c, "id", _display_text(c)), _display_text(c))
            for c in CategoryDataAdapter.get_all()
        ]
        self.category_multi.set_items(categories)

        # Cover designers (multi select)
        designers = [
            (getattr(d, "id", _display_text(d)), _display_text(d))
            for d in DesignerDataAdapter.get_all()
        ]
        self.designer_multi.set_items(designers)

        # Translators (multi select)
        translators = [
            (getattr(t, "id", _display_text(t)), _display_text(t))
            for t in TranslatorDataAdapter.get_all()
        ]
        self.translator_multi.set_items(translators)

        # Resources (multi select)
        resources = [
            (getattr(r, "id", _display_text(r)), _display_text(r))
            for r in ResourcesDataAdapter.get_all()
        ]
        self.resource_multi.set_items(resources)

    def reset_filters(self):
        self.publisher_combo.setCurrentIndex(-1)
        self.author_multi.clear_selection()
        self.language_multi.clear_selection()
        self.category_multi.clear_selection()
        self.designer_multi.clear_selection()
        self.translator_multi.clear_selection()
        self.resource_multi.clear_selection()

    def get_filters(self):
        return {
            "publisher_id": self.publisher_combo.currentData(),
            "author_ids": self.author_multi.selected_ids(),
            "language_ids": self.language_multi.selected_ids(),
            "category_ids": self.category_multi.selected_ids(),
            "designer_ids": self.designer_multi.selected_ids(),
            "translator_ids": self.translator_multi.selected_ids(),
            "resource_ids": self.resource_multi.selected_ids(),
        }

    def apply_filters(self):
        self.filters_applied.emit(self.get_filters())