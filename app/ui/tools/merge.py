import io
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from app.core.tools.merge import merge_images
from app.models.file_item import FileItem
from app.models.tool_options import MergeOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelComboBox, NoWheelSpinBox
from app.ui.widgets.preview_panel import PreviewPanel
from app.ui.widgets.preview_worker import PREVIEW_DEBOUNCE_MS, close_image
from app.utils.i18n import tr


class _MergePreviewWorker(QThread):
    done = pyqtSignal(bytes, int, int)
    failed = pyqtSignal(str)

    def __init__(self, files: list[FileItem], options: MergeOptions) -> None:
        super().__init__()
        self._files = files
        self._options = options

    def run(self) -> None:
        images: list[Image.Image] = []
        canvas: Image.Image | None = None
        try:
            files = self._files[:6]
            for f in files:
                if self.isInterruptionRequested():
                    return
                img = Image.open(f.path).convert("RGBA")
                images.append(img)
            canvas = merge_images(images, self._options)
            buf = io.BytesIO()
            save_fmt = "PNG" if canvas.mode == "RGBA" else "JPEG"
            canvas.save(buf, format=save_fmt)
            w, h = canvas.size
            self.done.emit(buf.getvalue(), w, h)
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            close_image(canvas)
            for img in images:
                close_image(img)


class MergeToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("merge_title"), tr("merge_desc"))
        self._pw: _MergePreviewWorker | None = None
        self._bg_color = "#FFFFFF"
        self._bg_image_path: Path | None = None
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(PREVIEW_DEBOUNCE_MS)
        self._refresh_timer.timeout.connect(self._refresh)
        self._build_ui()
        self._mode_combo.currentIndexChanged.connect(self._update_mode_visibility)
        self._update_mode_visibility()

        self._preview = PreviewPanel()
        self.add_preview(self._preview)

        self.drop_zone.files_changed.connect(self._schedule_refresh)
        self._mode_combo.currentIndexChanged.connect(self._schedule_refresh)
        self._gap_spin.valueChanged.connect(self._schedule_refresh)
        self._align_combo.currentIndexChanged.connect(self._schedule_refresh)
        self._cols_spin.valueChanged.connect(self._schedule_refresh)
        self._format_combo.currentIndexChanged.connect(self._schedule_refresh)
        self._bg_transparent_cb.toggled.connect(self._schedule_refresh)
        self.retranslate()

    def release_resources(self) -> None:
        self._refresh_timer.stop()
        if self._pw is not None and self._pw.isRunning():
            self._pw.requestInterruption()
            self._pw.wait(100)
        self._pw = None
        self._preview.release_resources()

    def _schedule_refresh(self, *_args) -> None:
        files = self.drop_zone.files
        if not files:
            self.release_resources()
            return
        self._preview.set_before_async(files[0].path)
        self._refresh_timer.start()

    def _build_ui(self) -> None:
        self._mode_combo = NoWheelComboBox()
        self._mode_combo.addItem("", "horizontal")
        self._mode_combo.addItem("", "vertical")
        self._mode_combo.addItem("", "grid")
        self._opt_row(tr("merge_mode"), self._mode_combo)

        self._gap_spin = NoWheelSpinBox()
        self._gap_spin.setRange(0, 100)
        self._gap_spin.setValue(4)
        self._gap_spin.setSingleStep(1)
        self._gap_spin.setSuffix(" px")
        self._opt_row(tr("merge_gap"), self._gap_spin)

        self._align_combo = NoWheelComboBox()
        self._align_row = self._opt_row(tr("merge_align"), self._align_combo)

        self._cols_spin = NoWheelSpinBox()
        self._cols_spin.setRange(0, 10)
        self._cols_spin.setValue(0)
        self._cols_spin.setSingleStep(1)
        self._cols_row = self._opt_row(tr("merge_cols"), self._cols_spin)

        self._format_combo = NoWheelComboBox()
        self._format_combo.addItem("PNG", "PNG")
        self._format_combo.addItem("JPG", "JPG")
        self._opt_row(tr("merge_format"), self._format_combo)

        bg_widget = QWidget()
        bl = QHBoxLayout(bg_widget)
        bl.setContentsMargins(0, 0, 0, 0)
        bl.setSpacing(8)
        bl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._bg_btn = QPushButton()
        self._bg_btn.setObjectName("colorSwatch")
        self._bg_btn.setFixedSize(28, 28)
        self._bg_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self._bg_btn.clicked.connect(self._pick_bg_color)

        self._bg_transparent_cb = QCheckBox()
        self._bg_transparent_cb.setObjectName("colorOptionCheckbox")
        self._bg_transparent_cb.toggled.connect(self._on_bg_mode_changed)

        self._bg_image_btn = QPushButton()
        self._bg_image_btn.setObjectName("fileBtn")
        self._bg_image_btn.setFixedHeight(30)
        self._bg_image_btn.clicked.connect(self._pick_bg_image)

        self._bg_image_clear = QPushButton("✕")
        self._bg_image_clear.setObjectName("fileBtn")
        self._bg_image_clear.setFixedSize(30, 30)
        self._bg_image_clear.setVisible(False)
        self._bg_image_clear.clicked.connect(self._clear_bg_image)

        bl.addWidget(self._bg_btn)
        bl.addWidget(self._bg_transparent_cb)
        bl.addWidget(self._bg_image_btn)
        bl.addWidget(self._bg_image_clear)
        bl.addStretch()

        self._bg_row = self._opt_row(tr("merge_bg"), bg_widget, min_height=48)
        self._update_bg_swatch()

    def _update_bg_swatch(self) -> None:
        self._bg_btn.setStyleSheet(
            f"background: {self._bg_color}; "
            f"border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
        )

    def _pick_bg_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._bg_color), self, tr("merge_bg_dialog_title"))
        if color.isValid():
            self._bg_color = color.name()
            self._update_bg_swatch()
            self._bg_transparent_cb.setChecked(False)
            self._bg_image_path = None
            self._bg_image_clear.setVisible(False)
            self._bg_image_btn.setText(tr("merge_pick_bg_image"))
            self._schedule_refresh()

    def _on_bg_mode_changed(self, checked: bool) -> None:
        self._bg_btn.setEnabled(not checked)
        if checked:
            self._bg_btn.setStyleSheet(
                "background: qlineargradient("
                "x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #ffffff,stop:0.49 #ffffff,"
                "stop:0.5 #cccccc,stop:1 #cccccc);"
                "border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
            )
            self._bg_image_path = None
            self._bg_image_clear.setVisible(False)
            self._bg_image_btn.setText(tr("merge_pick_bg_image"))
        else:
            self._update_bg_swatch()

    def _pick_bg_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            tr("merge_pick_bg_image"),
            "",
            "Images (*.jpg *.jpeg *.png *.webp *.bmp)",
        )
        if path:
            self._bg_image_path = Path(path)
            self._bg_transparent_cb.setChecked(False)
            name = self._bg_image_path.name
            short = name[:20] + "..." if len(name) > 20 else name
            self._bg_image_btn.setText(short)
            self._bg_image_clear.setVisible(True)
            self._schedule_refresh()

    def _clear_bg_image(self) -> None:
        self._bg_image_path = None
        self._bg_image_btn.setText(tr("merge_pick_bg_image"))
        self._bg_image_clear.setVisible(False)
        self._schedule_refresh()

    def _refresh(self) -> None:
        files = self.drop_zone.files
        if len(files) < 2:
            self._preview.set_status(tr("merge_preview_need_files"))
            return
        self._preview.set_status(tr("merge_preview_loading"))
        if self._pw and self._pw.isRunning():
            self._pw.requestInterruption()
            self._pw.wait(100)
        self._pw = _MergePreviewWorker(files, self.get_options())
        self._pw.done.connect(self._on_preview_done)
        self._pw.failed.connect(self._on_preview_failed)
        self._pw.start()

    def _on_preview_done(self, image_bytes: bytes, width: int, height: int) -> None:
        panel_w = self._preview._lbl.width() or 600
        panel_h = self._preview._lbl.height() or 360
        pm = QPixmap()
        pm.loadFromData(image_bytes)
        if pm.isNull():
            return
        fit = min(panel_w / pm.width(), panel_h / pm.height(), 1.0)
        self._preview._after_pm = pm.scaled(
            int(pm.width() * fit),
            int(pm.height() * fit),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview.set_after_preview(
            image_bytes,
            image_bytes,
            tr("merge_preview_status")
            .replace("{w}", str(width))
            .replace("{h}", str(height)),
        )
        self._preview._undo_btn.setVisible(False)

    def _on_preview_failed(self, message: str) -> None:
        self._preview.set_status(message)

    def get_options(self) -> MergeOptions:
        if self._bg_transparent_cb.isChecked():
            bg = "transparent"
        elif self._bg_image_path:
            bg = str(self._bg_image_path)
        else:
            bg = self._bg_color
        return MergeOptions(
            mode=self._mode_combo.currentData(),
            gap=self._gap_spin.value(),
            align=self._align_combo.currentData() or "top",
            grid_cols=self._cols_spin.value(),
            output_format=self._format_combo.currentData(),
            bg_color=bg,
        )

    def validate(self) -> str | None:
        if len(self.files) < 2:
            return tr("merge_min_files")
        return None

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("merge_title"), tr("merge_desc"))
        self._mode_combo.setItemText(0, tr("merge_mode_h"))
        self._mode_combo.setItemText(1, tr("merge_mode_v"))
        self._mode_combo.setItemText(2, tr("merge_mode_grid"))
        self._cols_spin.setSuffix(tr("merge_cols_auto"))
        self._bg_transparent_cb.setText(tr("transparent_bg"))
        self._bg_image_btn.setText(tr("merge_pick_bg_image"))
        self._update_align_combo()
        self._preview.retranslate()

    def _update_align_combo(self) -> None:
        mode = self._mode_combo.currentData()
        current = self._align_combo.currentData()
        self._align_combo.blockSignals(True)
        self._align_combo.clear()
        if mode == "horizontal":
            self._align_combo.addItem(tr("merge_align_top"), "top")
            self._align_combo.addItem(tr("merge_align_center"), "center")
            self._align_combo.addItem(tr("merge_align_bottom"), "bottom")
            defaults = ("top", "center", "bottom")
        elif mode == "vertical":
            self._align_combo.addItem(tr("merge_align_left"), "left")
            self._align_combo.addItem(tr("merge_align_center"), "center")
            self._align_combo.addItem(tr("merge_align_right"), "right")
            defaults = ("left", "center", "right")
        else:
            self._align_combo.blockSignals(False)
            return
        if current in defaults:
            self._align_combo.setCurrentIndex(defaults.index(current))
        self._align_combo.blockSignals(False)

    def _update_mode_visibility(self) -> None:
        mode = self._mode_combo.currentData()
        is_grid = mode == "grid"
        self._align_row.setVisible(not is_grid)
        self._cols_row.setVisible(is_grid)
        if not is_grid:
            self._update_align_combo()
