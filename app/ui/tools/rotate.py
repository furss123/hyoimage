from pathlib import Path

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QSizePolicy,
    QWidget,
)

from app.models.tool_options import RotateOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelSpinBox
from app.ui.widgets.preview_panel import PreviewPanel
from app.ui.widgets.preview_worker import PREVIEW_DEBOUNCE_MS, RotatePreviewWorker
from app.utils.i18n import tr


class RotateToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("rotate_title"), tr("rotate_desc"))
        self._fill_color = "#000000"
        self._quick_rotate_buttons: list[QPushButton] = []
        self._preview_worker: RotatePreviewWorker | None = None
        self._refresh_timer = QTimer()
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(PREVIEW_DEBOUNCE_MS)
        self._refresh_timer.timeout.connect(self._refresh)
        self._build_ui()
        self._update_fill_swatch()
        self._update_visibility()

        self._preview = PreviewPanel()
        self.add_preview(self._preview)

        self._angle_slider.valueChanged.connect(self._schedule_refresh)
        self._angle_spin.valueChanged.connect(self._schedule_refresh)
        self._angle_spin.valueChanged.connect(self._update_visibility)
        self._flip_h_cb.toggled.connect(self._schedule_refresh)
        self._flip_v_cb.toggled.connect(self._schedule_refresh)
        self._auto_exif_cb.toggled.connect(self._schedule_refresh)
        self._fill_transparent_cb.toggled.connect(self._schedule_refresh)
        for btn in self._quick_rotate_buttons:
            btn.clicked.connect(self._schedule_refresh)
        self.drop_zone.files_changed.connect(self._on_files)
        self.retranslate()

    def release_resources(self) -> None:
        self._refresh_timer.stop()
        self._cancel_preview_worker()
        self._preview.release_resources()

    def _cancel_preview_worker(self) -> None:
        if self._preview_worker is not None and self._preview_worker.isRunning():
            self._preview_worker.requestInterruption()
            self._preview_worker.wait(100)
        self._preview_worker = None

    def _on_files(self, files) -> None:
        if files:
            self._preview.set_before_async(files[0].path)
            self._preview.set_status(tr("rotate_preview_hint"))
            self._schedule_refresh()
        else:
            self.release_resources()

    def _schedule_refresh(self, *_args) -> None:
        if not self.drop_zone.files:
            return
        self._refresh_timer.start()

    def _build_ui(self) -> None:
        angle_widget = QWidget()
        al = QHBoxLayout(angle_widget)
        al.setContentsMargins(0, 0, 0, 0)
        self._angle_slider = QSlider(Qt.Orientation.Horizontal)
        self._angle_slider.setRange(0, 359)
        self._angle_spin = NoWheelSpinBox()
        self._angle_spin.setRange(0, 359)
        self._angle_slider.valueChanged.connect(self._angle_spin.setValue)
        self._angle_spin.valueChanged.connect(self._angle_slider.setValue)
        al.addWidget(self._angle_slider, 1)
        al.addWidget(self._angle_spin)
        self._opt_row(tr("rotate_angle"), angle_widget)

        quick_widget = QWidget()
        ql = QHBoxLayout(quick_widget)
        ql.setContentsMargins(0, 0, 0, 0)
        ql.setSpacing(8)
        self._cw_btn = QPushButton()
        self._cw_btn.setObjectName("quickRotate")
        self._cw_btn.clicked.connect(lambda: self._adjust_angle(90))
        self._ccw_btn = QPushButton()
        self._ccw_btn.setObjectName("quickRotate")
        self._ccw_btn.clicked.connect(lambda: self._adjust_angle(-90))
        self._flip180_btn = QPushButton()
        self._flip180_btn.setObjectName("quickRotate")
        self._flip180_btn.clicked.connect(lambda: self._adjust_angle(180))
        for btn in (self._cw_btn, self._ccw_btn, self._flip180_btn):
            ql.addWidget(btn)
            self._quick_rotate_buttons.append(btn)
        ql.addStretch(1)
        self._opt_row(tr("rotate_quick"), quick_widget, min_height=48)

        self._flip_h_cb = QCheckBox()
        self._add_option_checkbox(self._flip_h_cb)
        self._flip_v_cb = QCheckBox()
        self._add_option_checkbox(self._flip_v_cb)
        self._auto_exif_cb = QCheckBox()
        self._auto_exif_cb.setChecked(True)
        self._add_option_checkbox(self._auto_exif_cb)

        fill_widget = QWidget()
        fl = QHBoxLayout(fill_widget)
        fl.setContentsMargins(0, 0, 0, 0)
        fl.setSpacing(8)
        fl.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._fill_btn = QPushButton()
        self._fill_btn.setObjectName("colorSwatch")
        self._fill_btn.setFixedSize(32, 32)
        self._fill_btn.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        self._fill_btn.clicked.connect(self._pick_fill_color)

        self._fill_transparent_cb = QCheckBox()
        self._fill_transparent_cb.setObjectName("colorOptionCheckbox")
        self._fill_transparent_cb.setChecked(False)
        self._fill_transparent_cb.toggled.connect(self._on_fill_transparent)

        fl.addWidget(self._fill_btn)
        fl.addWidget(self._fill_transparent_cb)
        fl.addStretch()

        self._fill_row = self._opt_row(
            tr("rotate_fill_color"), fill_widget, min_height=48
        )

    def _refresh(self, *_args) -> None:
        files = self.drop_zone.files
        if not files:
            return
        self._cancel_preview_worker()
        worker = RotatePreviewWorker(Path(files[0].path), self.get_options())
        self._preview_worker = worker
        worker.done.connect(self._on_preview_done)
        worker.failed.connect(self._on_preview_failed)
        worker.finished.connect(self._on_preview_worker_finished)
        worker.start()

    def _on_preview_worker_finished(self) -> None:
        sender = self.sender()
        if sender is self._preview_worker:
            self._preview_worker = None

    def _on_preview_done(self, image_bytes: bytes) -> None:
        opts = self.get_options()
        pm = QPixmap()
        pm.loadFromData(image_bytes)
        if pm.isNull():
            return
        panel_w = self._preview._lbl.width() or 600
        panel_h = self._preview._lbl.height() or 360
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
            tr("rotate_preview_status")
            .replace("{angle}", str(opts.angle))
            .replace(
                "{flip_h}",
                tr("rotate_flip_h_suffix") if opts.flip_h else "",
            )
            .replace(
                "{flip_v}",
                tr("rotate_flip_v_suffix") if opts.flip_v else "",
            ),
        )

    def _on_preview_failed(self, exc: str) -> None:
        self._preview.set_status(f"오류: {exc}")

    def get_options(self) -> RotateOptions:
        fill = (
            None
            if self._fill_transparent_cb.isChecked()
            else self._fill_color
        )
        return RotateOptions(
            angle=self._angle_spin.value(),
            flip_h=self._flip_h_cb.isChecked(),
            flip_v=self._flip_v_cb.isChecked(),
            auto_exif=self._auto_exif_cb.isChecked(),
            fill_color=fill,
        )

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("rotate_title"), tr("rotate_desc"))
        self._cw_btn.setText(tr("rotate_90_cw"))
        self._ccw_btn.setText(tr("rotate_90_ccw"))
        self._flip180_btn.setText(tr("rotate_180"))
        self._flip_h_cb.setText(tr("rotate_flip_h"))
        self._flip_v_cb.setText(tr("rotate_flip_v"))
        self._auto_exif_cb.setText(tr("rotate_auto_exif"))
        self._fill_transparent_cb.setText(tr("transparent_bg"))
        self._preview.retranslate()

    def _adjust_angle(self, delta: int) -> None:
        self._angle_spin.setValue((self._angle_spin.value() + delta) % 360)

    def _update_visibility(self) -> None:
        self._fill_row.setVisible(self._angle_spin.value() != 0)

    def _update_fill_swatch(self) -> None:
        self._fill_btn.setStyleSheet(
            f"background: {self._fill_color}; "
            f"border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
        )

    def _pick_fill_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._fill_color), self, tr("rotate_fill_color"))
        if color.isValid():
            self._fill_color = color.name()
            self._update_fill_swatch()
            self._fill_transparent_cb.setChecked(False)
            self._schedule_refresh()

    def _on_fill_transparent(self, checked: bool) -> None:
        self._fill_btn.setEnabled(not checked)
        if checked:
            self._fill_btn.setStyleSheet(
                "background: qlineargradient("
                "x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #ffffff,stop:0.49 #ffffff,"
                "stop:0.5 #cccccc,stop:1 #cccccc);"
                "border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
            )
        else:
            self._update_fill_swatch()

