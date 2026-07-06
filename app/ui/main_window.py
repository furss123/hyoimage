from __future__ import annotations

import ctypes
import importlib
import os
import sys
from pathlib import Path

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QStyleOptionButton,
    QStylePainter,
    QVBoxLayout,
    QWidget,
)

from app.constants import TOOL_IDS
from app.settings import Settings, save_settings
from app.ui.conversion_worker import ConversionTask, ConversionWorker
from app.ui.output_bar import OutputBar
from app.ui.progress_panel import ProgressPanel
from app.ui.sidebar import Sidebar
from app.ui.theme import get_stylesheet
from app.ui.toast import Toast
from app.utils.icon import load_app_icon
from app.utils.i18n import load, tr
from app.utils.notify import play_completion_sound

_PREVIEW_TOOLS = frozenset({"resize", "rotate", "merge"})
_HEADER_BTN_SIZE = 40
_DEFAULT_WIDTH = 960
_MIN_WINDOW_WIDTH = 880
_MIN_WINDOW_HEIGHT = 560
_HD_MAX_WINDOW_HEIGHT = 820


class _HeaderBarButton(QPushButton):
    def paintEvent(self, event) -> None:
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        painter = QStylePainter(self)
        painter.drawControl(QStyle.ControlElement.CE_PushButtonBevel, opt)
        self.style().drawItemText(
            painter,
            self.rect(),
            int(Qt.AlignmentFlag.AlignCenter),
            self.palette(),
            self.isEnabled(),
            self.text(),
        )


def set_title_bar_color(window, dark: bool) -> None:
    if sys.platform != "win32":
        return
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    value = ctypes.c_int(1 if dark else 0)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        int(window.winId()),
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value),
    )


class MainWindow(QMainWindow):
    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self.settings = settings
        load(settings.language)
        self._tool_widgets: dict[str, QWidget] = {}
        self._tool_indices: dict[str, int] = {}
        self._worker: ConversionWorker | None = None
        self._initial_tool_id = (
            settings.last_tool
            if settings.last_tool in TOOL_IDS
            else TOOL_IDS[0]
        )
        self._build_ui()
        QTimer.singleShot(0, self._load_window_icon)
        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(_MIN_WINDOW_WIDTH, _MIN_WINDOW_HEIGHT)
        self._apply_initial_geometry()
        central_layout = self.centralWidget().layout()
        if central_layout is not None:
            central_layout.setContentsMargins(0, 0, 0, 0)
            central_layout.setSpacing(0)
        self.statusBar().setFixedHeight(0)
        self.statusBar().setVisible(False)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(get_stylesheet(settings.theme))
        self.retranslate()
        QTimer.singleShot(0, self._deferred_startup)

    def _apply_initial_geometry(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            self.resize(_DEFAULT_WIDTH, 760)
            return
        geo = screen.availableGeometry()
        width = min(_DEFAULT_WIDTH + 20, max(_MIN_WINDOW_WIDTH, geo.width() - 64))
        height = min(
            _HD_MAX_WINDOW_HEIGHT,
            max(_MIN_WINDOW_HEIGHT, int(geo.height() * 0.78)),
        )
        self.resize(width, height)

    def _load_window_icon(self) -> None:
        app_icon = load_app_icon()
        if app_icon is not None:
            self.setWindowIcon(app_icon)

    def _deferred_startup(self) -> None:
        self._on_tool_selected(self._initial_tool_id)

    def _center_on_primary_screen(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(geo.center())
        self.move(frame.topLeft())
        self.raise_()
        self.activateWindow()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        set_title_bar_color(self, dark=self.settings.theme == "dark")
        if not getattr(self, "_positioned", False):
            self._positioned = True
            self._center_on_primary_screen()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        content_area = QWidget()
        content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.sidebar = Sidebar(self)
        self.sidebar.tool_selected.connect(self._on_tool_selected)
        content_layout.addWidget(self.sidebar)

        right_widget = QWidget()
        right_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._tool_header = QWidget()
        self._tool_header.setObjectName("toolHeader")
        self._tool_header.setFixedHeight(48)
        header_layout = QHBoxLayout(self._tool_header)
        header_layout.setContentsMargins(24, 4, 24, 4)
        header_layout.setSpacing(12)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(0)
        self._header_title = QLabel()
        self._header_title.setObjectName("toolHeaderTitle")
        self._header_desc = QLabel()
        self._header_desc.setObjectName("toolHeaderDesc")
        title_col.addWidget(self._header_title)
        title_col.addWidget(self._header_desc)
        header_layout.addLayout(title_col)
        header_layout.addStretch(1)

        self._lang_btn = _HeaderBarButton()
        self._lang_btn.setObjectName("langBtn")
        self._lang_btn.setFixedSize(_HEADER_BTN_SIZE, _HEADER_BTN_SIZE)
        self._lang_btn.clicked.connect(self._on_language_toggle)
        header_layout.addWidget(
            self._lang_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self._theme_btn = _HeaderBarButton()
        self._theme_btn.setObjectName("themeBtn")
        self._theme_btn.setFixedSize(_HEADER_BTN_SIZE, _HEADER_BTN_SIZE)
        self._theme_btn.clicked.connect(self._on_theme_toggle)
        header_layout.addWidget(
            self._theme_btn, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        right_layout.addWidget(self._tool_header)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        right_layout.addWidget(self.stacked_widget, 1)

        self.progress_panel = ProgressPanel()
        self.progress_panel.cancel_requested.connect(self._on_cancel)
        right_layout.addWidget(self.progress_panel)

        content_layout.addWidget(right_widget, 1)
        main_layout.addWidget(content_area, stretch=1)

        self.output_bar = OutputBar()
        self.output_bar.run_requested.connect(self._on_run_requested)
        main_layout.addWidget(self.output_bar, stretch=0)

    def _create_tool_widget(self, tool_id: str) -> QWidget:
        module = importlib.import_module(f"app.ui.tools.{tool_id}")
        class_name = (
            "".join(part.capitalize() for part in tool_id.split("_")) + "ToolWidget"
        )
        widget_cls = getattr(module, class_name, None) or getattr(
            module, "ToolWidget", None
        )
        if widget_cls is not None:
            try:
                widget = widget_cls()
            except Exception as exc:
                print(f"Tool widget init failed ({tool_id}): {exc}")
                widget = QWidget()
        else:
            widget = QWidget()
        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        return widget

    def _ensure_tool_widget(self, tool_id: str) -> QWidget | None:
        if tool_id not in TOOL_IDS:
            return None
        if tool_id not in self._tool_widgets:
            widget = self._create_tool_widget(tool_id)
            self._tool_widgets[tool_id] = widget
            self._tool_indices[tool_id] = self.stacked_widget.addWidget(widget)
        return self._tool_widgets[tool_id]

    def _clear_tool_preview_cache(self, widget: QWidget) -> None:
        if hasattr(widget, "release_resources"):
            widget.release_resources()
            return
        preview = getattr(widget, "_preview", None)
        if preview is not None and hasattr(preview, "release_resources"):
            preview.release_resources()
        for attr in ("_result_preview", "_empty_preview"):
            result = getattr(widget, attr, None)
            if result is not None and hasattr(result, "release_resources"):
                result.release_resources()
        for attr in ("_pw", "_preview_worker"):
            worker = getattr(widget, attr, None)
            if worker is not None and worker.isRunning():
                worker.requestInterruption()
                worker.wait(100)
        load_worker = getattr(widget, "_load_worker", None)
        if load_worker is not None and load_worker.isRunning():
            load_worker.requestInterruption()
            load_worker.wait(100)

    def _current_tool_widget(self) -> QWidget | None:
        index = self.stacked_widget.currentIndex()
        for widget in self._tool_widgets.values():
            if self.stacked_widget.indexOf(widget) == index:
                return widget
        return None

    def _current_tool_id(self) -> str | None:
        index = self.stacked_widget.currentIndex()
        for tool_id, idx in self._tool_indices.items():
            if idx == index:
                return tool_id
        return None

    def _on_run_requested(self) -> None:
        widget = self._current_tool_widget()
        tool_id = self._current_tool_id()
        if widget is None or tool_id is None or not hasattr(widget, "files"):
            return

        files = widget.files
        if not files:
            QMessageBox.warning(self, tr("status_error"), tr("no_files_selected"))
            return

        if hasattr(widget, "validate"):
            error = widget.validate()
            if error:
                QMessageBox.warning(self, tr("status_error"), error)
                return

        if not hasattr(widget, "get_options"):
            return

        output_dir_path = self.output_bar.output_dir
        if not output_dir_path or not output_dir_path.exists():
            QMessageBox.warning(self, tr("status_error"), tr("output_path_invalid"))
            return
        output_dir = output_dir_path
        overwrite = self.output_bar.overwrite
        suffix = self.output_bar.suffix
        options = widget.get_options()

        crop_img = None
        crop_source_path = None
        if tool_id == "crop" and getattr(widget, "_crop_history", None):
            if widget._crop_history:
                pixmap = widget._canvas._pixmap
                if pixmap is None or pixmap.isNull():
                    return
                from io import BytesIO

                from PIL import Image
                from PyQt6.QtCore import QBuffer, QIODevice

                buf = QBuffer()
                buf.open(QIODevice.OpenModeFlag.ReadWrite)
                pixmap.save(buf, "PNG")
                crop_img = Image.open(BytesIO(bytes(buf.data())))
                crop_source_path = widget._current_path or files[0].path

        preview = getattr(widget, "_preview", None)
        export_img = (
            preview.get_export_image()
            if preview is not None and tool_id in _PREVIEW_TOOLS
            else None
        )

        total = 1 if crop_img is not None else len(files)
        task = ConversionTask(
            tool_id=tool_id,
            files=files,
            options=options,
            output_dir=output_dir,
            overwrite=overwrite,
            suffix=suffix,
            export_img=export_img,
            crop_img=crop_img,
            crop_source_path=crop_source_path,
        )
        self._start_conversion(task, total)

    def _start_conversion(self, task: ConversionTask, total: int) -> None:
        if self._worker is not None and self._worker.isRunning():
            return

        self.output_bar.set_running(True)
        self.output_bar.start_progress(total)

        self._worker = ConversionWorker(task)
        self._worker.progress.connect(self._on_file_done)
        self._worker.finished.connect(self._on_all_done)
        self._worker.start()

    def _on_cancel(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self._worker.cancel()
        self.output_bar.set_running(False)
        self.output_bar.reset_progress()
        self.progress_panel.hide()
        self.progress_panel.reset()

    def _on_file_done(self, current: int, total: int) -> None:
        self.output_bar.update_progress(current, total)
        self.progress_panel.update_overall(current, total)

    def _on_all_done(self, success: int, fail: int, last_output: object = None) -> None:
        self.output_bar.set_running(False)
        self.output_bar.finish_progress()
        self.progress_panel.finish()
        self._worker = None
        widget = self._current_tool_widget()
        if widget is not None and last_output is not None:
            widget.show_conversion_result(last_output)
        if success > 0 or fail > 0:
            play_completion_sound(all_success=success > 0 and fail == 0)
        if success > 0 and fail == 0:
            Toast(
                self,
                tr("toast_success").replace("{n}", str(success)),
                success=True,
            )
        elif fail > 0:
            Toast(self, tr("toast_error"), success=False)

    def _update_tool_header(self, tool_id: str) -> None:
        self._header_title.setText(tr(tool_id))
        desc_key = f"{tool_id}_desc"
        self._header_desc.setText(tr(desc_key))

    def _apply_tool_switch(self, tool_id: str) -> None:
        old = self._current_tool_widget()
        if old is not None:
            self._clear_tool_preview_cache(old)
        widget = self._ensure_tool_widget(tool_id)
        if widget is None:
            return
        self._update_tool_header(tool_id)
        self.stacked_widget.setCurrentWidget(widget)
        self.sidebar.set_active(tool_id)
        self.settings.last_tool = tool_id
        save_settings(self.settings)

    def _on_tool_selected(self, tool_id: str) -> None:
        if tool_id not in TOOL_IDS:
            return

        if self._current_tool_id() == tool_id:
            self.sidebar.set_active(tool_id)
            return

        self._apply_tool_switch(tool_id)

    def _on_theme_toggle(self) -> None:
        new_theme = "light" if self.settings.theme == "dark" else "dark"
        self.switch_theme(new_theme)

    def _on_language_toggle(self) -> None:
        new_lang = "en" if self.settings.language == "ko" else "ko"
        self.switch_language(new_lang)

    def switch_theme(self, theme: str) -> None:
        self.settings.theme = theme
        save_settings(self.settings)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(get_stylesheet(theme))
        set_title_bar_color(self, dark=theme == "dark")
        self.retranslate()

    def switch_language(self, lang: str) -> None:
        self.settings.language = lang
        save_settings(self.settings)
        load(lang)
        self.retranslate()

    def retranslate(self) -> None:
        self.setWindowTitle(tr("app_title"))
        tool_id = self._current_tool_id()
        if tool_id is not None:
            self._update_tool_header(tool_id)
        self.sidebar.retranslate()
        self.output_bar.retranslate()
        self.progress_panel.retranslate()
        for widget in self._tool_widgets.values():
            if hasattr(widget, "retranslate"):
                widget.retranslate()
        self._theme_btn.setText("☀" if self.settings.theme == "dark" else "🌙")
        self._theme_btn.setToolTip(
            tr("theme_light") if self.settings.theme == "dark" else tr("theme_dark")
        )
        self._lang_btn.setText("EN" if self.settings.language == "ko" else "KR")
        self._lang_btn.setToolTip(
            tr("lang_en") if self.settings.language == "ko" else tr("lang_ko")
        )
