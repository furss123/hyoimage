from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.drop_zone import DropZone
from app.utils.i18n import tr

TOOL_CONTENT_HORIZONTAL_MARGIN = 24
_OPT_LABEL_WIDTH = 120
_OPT_LABEL_SPACING = 16
_OPT_CONTROL_OFFSET = _OPT_LABEL_WIDTH + _OPT_LABEL_SPACING


class BaseToolWidget(QWidget):
    def __init__(self, title: str = "", desc: str = "") -> None:
        super().__init__()
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._page_title = title
        self._page_desc = desc

        self._body = QWidget()
        self._body.setObjectName("toolContent")
        self._body.setAutoFillBackground(False)
        self._body.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._layout = QVBoxLayout(self._body)
        self._layout.setContentsMargins(
            TOOL_CONTENT_HORIZONTAL_MARGIN,
            12,
            TOOL_CONTENT_HORIZONTAL_MARGIN,
            12,
        )
        self._layout.setSpacing(0)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.drop_zone = DropZone()
        self._layout.addWidget(self.drop_zone)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 6, 0, 10)
        btn_row.setSpacing(6)
        self._add_btn = QPushButton()
        self._add_btn.setObjectName("fileBtn")
        self._folder_btn = QPushButton()
        self._folder_btn.setObjectName("fileBtn")
        self._clear_btn = QPushButton()
        self._clear_btn.setObjectName("deleteBtn")
        self._add_btn.clicked.connect(self.drop_zone.add_files_dialog)
        self._folder_btn.clicked.connect(self.drop_zone.add_folder_dialog)
        self._clear_btn.clicked.connect(self.drop_zone.clear)
        btn_row.addWidget(self._add_btn)
        btn_row.addWidget(self._folder_btn)
        btn_row.addWidget(self._clear_btn)
        btn_row.addStretch()
        self._layout.addLayout(btn_row)

        self._options_wrap = QWidget()
        self._options_wrap.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Maximum,
        )
        self._options_layout = QVBoxLayout(self._options_wrap)
        self._options_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._options_layout.setSpacing(12)
        self._options_layout.setContentsMargins(16, 10, 16, 10)
        self._layout.addWidget(self._options_wrap)

        self._preview_area = QWidget()
        self._preview_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._preview_layout = QVBoxLayout(self._preview_area)
        self._preview_layout.setContentsMargins(0, 0, 0, 0)
        self._preview_layout.setSpacing(0)
        self._layout.addWidget(self._preview_area, stretch=1)

        root.addWidget(self._body, stretch=1)

        self.content_layout = self._options_layout

        self._content = self._body
        self._content_wrapper = self._body

    @property
    def main_layout(self) -> QVBoxLayout:
        return self._layout

    @property
    def files(self) -> list:
        return self.drop_zone.files

    def add_preview(self, widget: QWidget) -> None:
        self._preview_layout.addWidget(widget, stretch=1)

    def show_conversion_result(self, path) -> None:
        preview = getattr(self, "_result_preview", None)
        if preview is not None and path is not None:
            preview.show_image(path)

    def get_options(self):
        return None

    def validate(self) -> str | None:
        return None

    def retranslate(self) -> None:
        self.drop_zone.retranslate()
        self._add_btn.setText(tr("add_files"))
        self._folder_btn.setText(tr("add_folder"))
        self._clear_btn.setText(tr("clear"))
        preview = getattr(self, "_result_preview", None)
        if preview is not None:
            pm = preview._label.pixmap()
            if pm is None or pm.isNull():
                preview.show_placeholder()

    def _update_header(self, title: str, desc: str) -> None:
        self._page_title = title
        self._page_desc = desc

    def _opt_row(
        self, label: str, widget: QWidget, *, min_height: int = 44
    ) -> QWidget:
        row = QWidget()
        row.setObjectName("optionRow")
        row.setMinimumHeight(min_height)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(_OPT_LABEL_SPACING)
        lbl = QLabel(label)
        lbl.setObjectName("optLabel")
        lbl.setFixedWidth(_OPT_LABEL_WIDTH)
        lbl.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        hl.addWidget(lbl)
        hl.addWidget(widget, stretch=1)
        self._options_layout.addWidget(row)
        return row

    def _add_option_checkbox(self, checkbox: QCheckBox) -> None:
        row = QWidget()
        row.setObjectName("optionRow")
        row.setMinimumHeight(32)
        hl = QHBoxLayout(row)
        hl.setContentsMargins(_OPT_CONTROL_OFFSET, 0, 0, 0)
        hl.setSpacing(0)
        hl.addWidget(checkbox)
        hl.addStretch()
        self._options_layout.addWidget(row)
