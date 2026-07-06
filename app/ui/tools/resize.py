from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.models.tool_options import ResizeOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelComboBox, NoWheelSpinBox
from app.ui.widgets.preview_panel import PreviewPanel
from app.ui.widgets.preview_worker import ResizePreviewWorker
from app.utils.i18n import tr


class ResizeToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("resize_title"), tr("resize_desc"))
        self._preview_worker: ResizePreviewWorker | None = None

        self._build_resize_ui()
        self._mode_combo.currentIndexChanged.connect(self._update_mode_visibility)
        self._update_mode_visibility()

        self._preview = PreviewPanel()
        self.add_preview(self._preview)

        self.drop_zone.files_changed.connect(self._on_files)
        self._preview_btn.clicked.connect(self._refresh)

        self.retranslate()

    def release_resources(self) -> None:
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
            self._preview.set_status(tr("resize_preview_hint"))
        else:
            self.release_resources()

    def _refresh(self, *_args) -> None:
        files = self.drop_zone.files
        if not files:
            return
        path = Path(files[0].path)
        self._cancel_preview_worker()
        worker = ResizePreviewWorker(
            path,
            self.get_options(),
            self._preview.get_source_bytes(),
        )
        self._preview_worker = worker
        worker.done.connect(self._on_preview_done)
        worker.failed.connect(self._on_preview_failed)
        worker.finished.connect(self._on_preview_worker_finished)
        worker.start()

    def _on_preview_worker_finished(self) -> None:
        sender = self.sender()
        if sender is self._preview_worker:
            self._preview_worker = None

    def _on_preview_done(
        self,
        before_bytes: bytes,
        after_bytes: bytes,
        export_bytes: bytes,
        status: str,
    ) -> None:
        panel_w, panel_h = self._preview._panel_size()
        before_pm = QPixmap()
        before_pm.loadFromData(before_bytes)
        before_pm = before_pm.scaled(
            panel_w,
            panel_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        after_pm = QPixmap()
        after_pm.loadFromData(after_bytes)
        parts = status.split("|")
        if len(parts) == 5:
            orig_w, orig_h, nw, nh, pct = parts
            status_text = (
                tr("resize_preview_status")
                .replace("{ow}", orig_w)
                .replace("{oh}", orig_h)
                .replace("{nw}", nw)
                .replace("{nh}", nh)
                .replace("{pct}", pct)
            )
        else:
            status_text = ""
        fit = before_pm.width() / max(1, int(parts[0]) if parts else 1)
        disp_res_w = max(1, int(int(parts[2]) * fit) if len(parts) > 2 else after_pm.width())
        disp_res_h = max(1, int(int(parts[3]) * fit) if len(parts) > 3 else after_pm.height())
        after_pm = after_pm.scaled(
            disp_res_w,
            disp_res_h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._preview.apply_preview_bytes(
            before_pm,
            after_pm,
            export_bytes,
            status_text,
        )

    def _on_preview_failed(self, exc: str) -> None:
        self._preview.set_status(f"오류: {exc}")

    def _build_resize_ui(self) -> None:
        self._mode_combo = NoWheelComboBox()
        self._mode_combo.addItem("", "percent")
        self._mode_combo.addItem("", "exact")
        self._mode_combo.addItem("", "longest_side")
        self._opt_row(tr("resize_mode"), self._mode_combo)

        self._percent_widget = QWidget()
        pl = QHBoxLayout(self._percent_widget)
        pl.setContentsMargins(0, 0, 0, 0)
        self._percent_spin = NoWheelSpinBox()
        self._percent_spin.setRange(1, 999)
        self._percent_spin.setValue(100)
        self._percent_spin.setSuffix("%")
        self._percent_spin.setSingleStep(10)
        pl.addWidget(self._percent_spin)
        self._percent_row = self._opt_row(tr("resize_percent"), self._percent_widget)

        self._exact_widget = QWidget()
        el = QHBoxLayout(self._exact_widget)
        el.setContentsMargins(0, 0, 0, 0)
        el.setSpacing(8)
        self._width_spin = NoWheelSpinBox()
        self._width_spin.setRange(1, 99999)
        self._width_spin.setValue(1920)
        self._width_spin.setSingleStep(10)
        self._height_spin = NoWheelSpinBox()
        self._height_spin.setRange(1, 99999)
        self._height_spin.setValue(1080)
        self._height_spin.setSingleStep(10)
        self._width_label = QLabel()
        self._height_label = QLabel()
        el.addWidget(self._width_label)
        el.addWidget(self._width_spin)
        el.addWidget(self._height_label)
        el.addWidget(self._height_spin)
        self._exact_row = self._opt_row(tr("resize_exact"), self._exact_widget)

        self._keep_aspect_cb = QCheckBox()
        self._add_option_checkbox(self._keep_aspect_cb)

        self._longest_widget = QWidget()
        ll = QHBoxLayout(self._longest_widget)
        ll.setContentsMargins(0, 0, 0, 0)
        self._longest_spin = NoWheelSpinBox()
        self._longest_spin.setRange(1, 99999)
        self._longest_spin.setValue(1920)
        self._longest_spin.setSingleStep(10)
        ll.addWidget(self._longest_spin)
        self._longest_row = self._opt_row(tr("resize_longest_side"), self._longest_widget)

        self._allow_upscale_cb = QCheckBox()
        self._add_option_checkbox(self._allow_upscale_cb)

        self._resample_combo = NoWheelComboBox()
        self._resample_combo.addItem("", "lanczos")
        self._resample_combo.addItem("", "bicubic")
        self._resample_combo.addItem("", "nearest")
        self._opt_row(tr("resize_resample"), self._resample_combo)

        self._options_layout.addSpacing(4)
        self._preview_btn = QPushButton()
        self._preview_btn.setObjectName("primary")
        self._preview_btn.setFixedHeight(32)
        self._preview_btn.setMinimumWidth(120)
        preview_row = QHBoxLayout()
        preview_row.setContentsMargins(0, 0, 0, 0)
        preview_row.addStretch()
        preview_row.addWidget(self._preview_btn)
        self._options_layout.addLayout(preview_row)

    def get_options(self) -> ResizeOptions:
        return ResizeOptions(
            mode=self._mode_combo.currentData(),
            percent=self._percent_spin.value(),
            width=self._width_spin.value(),
            height=self._height_spin.value(),
            keep_aspect=self._keep_aspect_cb.isChecked(),
            longest_side=self._longest_spin.value(),
            allow_upscale=self._allow_upscale_cb.isChecked(),
            resample=self._resample_combo.currentData(),
        )

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("resize_title"), tr("resize_desc"))
        self._mode_combo.setItemText(0, tr("resize_mode_percent"))
        self._mode_combo.setItemText(1, tr("resize_mode_exact"))
        self._mode_combo.setItemText(2, tr("resize_mode_longest"))
        self._width_label.setText(tr("resize_width"))
        self._height_label.setText(tr("resize_height"))
        self._keep_aspect_cb.setText(tr("resize_keep_aspect"))
        self._allow_upscale_cb.setText(tr("resize_allow_upscale"))
        self._resample_combo.setItemText(0, tr("resize_resample_lanczos"))
        self._resample_combo.setItemText(1, tr("resize_resample_bicubic"))
        self._resample_combo.setItemText(2, tr("resize_resample_nearest"))
        self._preview_btn.setText(tr("resize_preview_btn"))
        self._preview.retranslate()

    def _update_mode_visibility(self) -> None:
        mode = self._mode_combo.currentData()
        self._percent_row.setVisible(mode == "percent")
        self._exact_row.setVisible(mode == "exact")
        self._keep_aspect_cb.setVisible(mode == "exact")
        self._longest_row.setVisible(mode == "longest_side")

