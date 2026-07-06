from __future__ import annotations

from typing import TYPE_CHECKING

from pathlib import Path

from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.constants import ASSETS_DIR, TOOL_IDS
from app.ui.theme import get_tool_accent
from app.utils.i18n import tr
from app.utils.icon import load_pixmap

if TYPE_CHECKING:
    from app.ui.main_window import MainWindow

_BANNER_PATH = Path(__file__).resolve().parent.parent / "assets" / "banner.png"
_SIDEBAR_WIDTH = 268
_SIDE_INSET = 8
_CONTENT_WIDTH = _SIDEBAR_WIDTH - _SIDE_INSET * 2


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


class _ToolRowWidget(QWidget):
    def __init__(self, tool_id: str, label: str) -> None:
        super().__init__()
        self.setFixedHeight(52)
        self.setAutoFillBackground(False)
        self._accent = get_tool_accent(tool_id)
        r, g, b = _hex_to_rgb(self._accent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(11, 0, 8, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._select_bar = QLabel()
        self._select_bar.setFixedWidth(3)
        self._select_bar.setFixedHeight(24)
        self._select_bar.setStyleSheet("background: transparent; border-radius: 1px;")

        self._icon_chip = QWidget()
        self._icon_chip.setFixedSize(36, 36)
        self._icon_chip.setStyleSheet(
            f"background: rgba({r}, {g}, {b}, 0.16); border-radius: 9px;"
        )
        chip_layout = QHBoxLayout(self._icon_chip)
        chip_layout.setContentsMargins(0, 0, 0, 0)

        self._icon = QLabel()
        self._icon.setObjectName("iconLabel")
        self._icon.setFixedSize(22, 22)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setScaledContents(True)
        self._icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._icon.setStyleSheet("background: transparent;")
        chip_layout.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignCenter)
        icon_path = ASSETS_DIR / "icons" / f"{tool_id}.png"
        self._icon_path = icon_path

        self._label = QLabel(label)
        self._label.setWordWrap(False)
        self._label.setMinimumWidth(0)
        self._label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self._label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout.addWidget(self._select_bar)
        layout.addWidget(self._icon_chip)
        layout.addWidget(self._label, 1)

    def load_icon(self) -> None:
        if self._icon_path.is_file():
            self._icon.setPixmap(load_pixmap(self._icon_path, 22, 22))

    def set_label(self, text: str) -> None:
        self._label.setText(text)

    def set_selected(self, selected: bool) -> None:
        color = self._accent if selected else "transparent"
        self._select_bar.setStyleSheet(f"background: {color}; border-radius: 1px;")


class Sidebar(QWidget):
    tool_selected = pyqtSignal(str)

    def __init__(self, main_window: MainWindow) -> None:
        super().__init__()
        self.setObjectName("sidebar")
        self._main_window = main_window
        self._tool_rows: dict[str, int] = {}
        self._row_widgets: dict[str, _ToolRowWidget] = {}

        self.setMinimumWidth(_SIDEBAR_WIDTH)
        self.setMaximumWidth(_SIDEBAR_WIDTH)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(_SIDE_INSET, 10, _SIDE_INSET, 10)
        layout.setSpacing(4)

        self._banner_label = QLabel()
        self._banner_label.setObjectName("sidebarBanner")
        self._banner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._banner_label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._banner_label.setStyleSheet("background: transparent; padding: 0px;")
        layout.insertWidget(0, self._banner_label)

        self._app_label = QLabel("HyoImage")
        self._app_label.setObjectName("appTitle")
        self._app_label.setVisible(False)

        self._tool_list = QListWidget()
        self._tool_list.setObjectName("toolList")
        self._tool_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._tool_list.setFrameShape(QListWidget.Shape.NoFrame)
        self._tool_list.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._tool_list.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._tool_list.setSpacing(2)
        for row, tool_id in enumerate(TOOL_IDS):
            item = QListWidgetItem()
            item.setSizeHint(QSize(_CONTENT_WIDTH, 52))
            row_widget = _ToolRowWidget(tool_id, tr(tool_id))
            self._row_widgets[tool_id] = row_widget
            self._tool_list.addItem(item)
            self._tool_list.setItemWidget(item, row_widget)
            self._tool_rows[tool_id] = row
        self._tool_list.currentRowChanged.connect(self._on_tool_row_changed)
        layout.addWidget(self._tool_list, 1)

        self.retranslate()
        QTimer.singleShot(0, self._load_assets)

    def _load_assets(self) -> None:
        if _BANNER_PATH.is_file():
            pixmap = load_pixmap(_BANNER_PATH)
            if not pixmap.isNull():
                scaled = pixmap.scaledToWidth(
                    _CONTENT_WIDTH,
                    Qt.TransformationMode.SmoothTransformation,
                )
                if scaled.height() > 72:
                    scaled = pixmap.scaled(
                        _CONTENT_WIDTH,
                        72,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                self._banner_label.setPixmap(scaled)
                self._banner_label.setFixedSize(scaled.size())
        for row_widget in self._row_widgets.values():
            row_widget.load_icon()

    def set_active(self, tool_id: str) -> None:
        row = self._tool_rows.get(tool_id)
        if row is None:
            return
        self._tool_list.blockSignals(True)
        self._tool_list.setCurrentRow(row)
        self._tool_list.blockSignals(False)
        self._update_selection_bars(tool_id)

    def _update_selection_bars(self, active_tool_id: str) -> None:
        for tool_id, row_widget in self._row_widgets.items():
            row_widget.set_selected(tool_id == active_tool_id)

    def retranslate(self) -> None:
        for tool_id, row_widget in self._row_widgets.items():
            row_widget.set_label(tr(tool_id))

    def _on_tool_row_changed(self, row: int) -> None:
        if row < 0 or row >= len(TOOL_IDS):
            return
        tool_id = TOOL_IDS[row]
        self._update_selection_bars(tool_id)
        self.tool_selected.emit(tool_id)
