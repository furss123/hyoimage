from pathlib import Path

from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.file_item import FileItem
from app.models.tool_options import CropOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.crop_canvas import CropCanvas
from app.ui.widgets.no_wheel_widgets import NoWheelComboBox, NoWheelSpinBox
from app.ui.widgets.result_preview import ResultPreviewWidget
from app.ui.widgets.preview_worker import FilePixmapWorker
from app.utils.i18n import tr

_RATIO_MAP = {
    "1:1": (1, 1),
    "4:3": (4, 3),
    "16:9": (16, 9),
    "3:4": (3, 4),
    "9:16": (9, 16),
}


class CropToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("crop_title"), tr("crop_desc"))
        self._current_path: Path | None = None
        self._ratio_buttons: list[QPushButton] = []
        self._manual_spins: list[NoWheelSpinBox] = []
        self._build_crop_ui()
        self.retranslate()

    def _build_crop_ui(self) -> None:
        self._mode_combo = NoWheelComboBox()
        self._mode_combo.addItems(
            ["비율로 자르기", "직접 입력", "가운데 정사각형"]
        )
        self._mode_row = self._opt_row(tr("crop_mode"), self._mode_combo)

        self._ratio_combo = NoWheelComboBox()
        self._ratio_combo.addItems(["1:1", "4:3", "16:9", "3:4", "9:16"])
        self._ratio_row = self._opt_row(tr("crop_ratio"), self._ratio_combo)

        manual_widget = QWidget()
        ml = QHBoxLayout(manual_widget)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(8)
        for label in ["X", "Y", tr("crop_w"), tr("crop_h")]:
            ml.addWidget(QLabel(label))
            spin = NoWheelSpinBox()
            spin.setRange(0, 99999)
            spin.setValue(0)
            ml.addWidget(spin)
            self._manual_spins.append(spin)
        self._manual_row = self._opt_row(tr("crop_manual"), manual_widget)

        self._editor_container = QWidget()
        self._editor_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._editor_container.setVisible(False)
        ec = QVBoxLayout(self._editor_container)
        ec.setContentsMargins(0, 0, 0, 0)
        ec.setSpacing(8)

        self._canvas = CropCanvas()
        self._canvas.setMinimumHeight(220)
        ec.addWidget(self._canvas, stretch=1)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)
        ratios = [
            ("crop_ratio_free", None),
            ("crop_ratio_1_1", (1, 1)),
            ("crop_ratio_4_3", (4, 3)),
            ("crop_ratio_16_9", (16, 9)),
            ("crop_ratio_3_4", (3, 4)),
            ("crop_ratio_9_16", (9, 16)),
        ]
        for key, ratio in ratios:
            btn = QPushButton()
            btn.setObjectName("quickRotate")
            btn.setFixedWidth(48)
            btn.clicked.connect(lambda _, r=ratio: self._canvas.set_ratio(r))
            ctrl.addWidget(btn)
            self._ratio_buttons.append((btn, key, ratio))

        ctrl.addStretch()

        self._reset_btn = QPushButton()
        self._reset_btn.setObjectName("fileBtn")
        self._reset_btn.clicked.connect(self._canvas.reset_crop)
        ctrl.addWidget(self._reset_btn)

        self._change_btn = QPushButton()
        self._change_btn.setObjectName("fileBtn")
        self._change_btn.clicked.connect(self._change_image)
        ctrl.addWidget(self._change_btn)

        ec.addLayout(ctrl)

        preview_row = QHBoxLayout()
        preview_row.setSpacing(8)
        preview_row.setContentsMargins(0, 8, 0, 0)

        self._preview_btn = QPushButton()
        self._preview_btn.setObjectName("primary")
        self._preview_btn.setFixedHeight(32)
        self._preview_btn.clicked.connect(self._apply_crop_preview)

        self._undo_btn = QPushButton()
        self._undo_btn.setObjectName("fileBtn")
        self._undo_btn.setFixedHeight(32)
        self._undo_btn.setVisible(False)
        self._undo_btn.clicked.connect(self._undo_crop)

        preview_row.addStretch()
        preview_row.addWidget(self._undo_btn)
        preview_row.addWidget(self._preview_btn)
        ec.addLayout(preview_row)

        self._crop_history: list[QPixmap] = []
        self._load_worker: FilePixmapWorker | None = None
        self._load_token = 0

        self._info_lbl = QLabel("")
        self._info_lbl.setObjectName("cropInfo")
        self._canvas.crop_changed.connect(self._update_info)
        ec.addWidget(self._info_lbl)

        self._empty_preview = ResultPreviewWidget()
        self._empty_preview._label.setMinimumHeight(120)
        self.add_preview(self._empty_preview)

        self.add_preview(self._editor_container)
        self.drop_zone.files_changed.connect(self._on_files_changed)
        self._mode_combo.currentIndexChanged.connect(self._update_mode_ui)
        self._ratio_combo.currentTextChanged.connect(self._on_ratio_combo_changed)
        for spin in self._manual_spins:
            spin.valueChanged.connect(self._on_manual_changed)
        self._update_mode_ui(0)

        self.drop_zone.setVisible(True)
        self._editor_container.setVisible(False)

    def _update_mode_ui(self, idx: int) -> None:
        self._ratio_row.setVisible(idx == 0)
        self._manual_row.setVisible(idx == 1)
        self._apply_mode_to_canvas()

    def _on_ratio_combo_changed(self, text: str) -> None:
        if self._current_path is None or self._mode_combo.currentIndex() != 0:
            return
        self._canvas.set_ratio(_RATIO_MAP.get(text))

    def _on_manual_changed(self) -> None:
        if self._current_path is None or self._mode_combo.currentIndex() != 1:
            return
        x, y, w, h = (s.value() for s in self._manual_spins)
        if w > 0 and h > 0:
            self._canvas.set_crop_rect(x, y, w, h)

    def _apply_mode_to_canvas(self) -> None:
        if self._current_path is None:
            return
        idx = self._mode_combo.currentIndex()
        if idx == 0:
            self._canvas.set_ratio(_RATIO_MAP.get(self._ratio_combo.currentText()))
        elif idx == 2:
            self._canvas.set_center_square()

    @property
    def files(self) -> list[FileItem]:
        if self._current_path is not None:
            return [FileItem(path=self._current_path)]
        return self.drop_zone.files

    def release_resources(self) -> None:
        if self._load_worker is not None and self._load_worker.isRunning():
            self._load_worker.requestInterruption()
            self._load_worker.wait(100)
        self._load_worker = None
        self._crop_history.clear()
        self._empty_preview.release_resources()

    def _on_files_changed(self, files: list) -> None:
        if files:
            self._load_image(files[0].path)

    def _apply_crop_preview(self) -> None:
        rect = self._canvas.get_crop_rect()
        if rect.width() < 1 or rect.height() < 1:
            return
        pixmap = self._canvas._pixmap
        if pixmap is None or pixmap.isNull():
            return

        self._crop_history.append(pixmap.copy())
        cropped = pixmap.copy(rect)
        self._canvas.set_image(cropped)
        self._canvas._pixmap = cropped

        self._undo_btn.setVisible(True)
        self._info_lbl.setText(
            tr("crop_applied_status")
            .replace("{w}", str(rect.width()))
            .replace("{h}", str(rect.height()))
        )

    def _undo_crop(self) -> None:
        if not self._crop_history:
            return
        prev = self._crop_history.pop()
        self._canvas.set_image(prev)
        self._canvas._pixmap = prev
        self._undo_btn.setVisible(len(self._crop_history) > 0)
        self._info_lbl.setText(tr("preview_undo_done"))

    def _reset_crop_history(self) -> None:
        self._crop_history.clear()
        self._undo_btn.setVisible(False)

    def _load_image(self, path: Path) -> None:
        self._load_token += 1
        token = self._load_token
        if self._load_worker is not None and self._load_worker.isRunning():
            self._load_worker.requestInterruption()
            self._load_worker.wait(100)
        worker = FilePixmapWorker(path)
        self._load_worker = worker
        worker.loaded.connect(
            lambda data, t=token, p=path: self._on_image_loaded(t, p, data)
        )
        worker.failed.connect(lambda _msg, t=token: self._on_image_load_failed(t))
        worker.finished.connect(self._on_load_worker_finished)
        worker.start()

    def _on_load_worker_finished(self) -> None:
        sender = self.sender()
        if sender is self._load_worker:
            self._load_worker = None

    def _on_image_load_failed(self, token: int) -> None:
        if token != self._load_token:
            return

    def _on_image_loaded(self, token: int, path: Path, data: bytes) -> None:
        if token != self._load_token:
            return
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if pixmap.isNull():
            return
        self._current_path = path
        self._reset_crop_history()
        self._canvas.set_image(pixmap)
        self._apply_mode_to_canvas()
        self.drop_zone.setVisible(False)
        self._add_btn.setVisible(False)
        self._folder_btn.setVisible(False)
        self._clear_btn.setVisible(False)
        self._empty_preview.setVisible(False)
        self._editor_container.setVisible(True)

    def _change_image(self) -> None:
        self._reset_crop_history()
        self._current_path = None
        self.drop_zone.clear()
        self._editor_container.setVisible(False)
        self._empty_preview.setVisible(True)
        self._empty_preview.show_placeholder()
        self.drop_zone.setVisible(True)
        self._add_btn.setVisible(True)
        self._folder_btn.setVisible(True)
        self._clear_btn.setVisible(True)

    def _update_info(self, rect: QRect) -> None:
        self._info_lbl.setText(
            tr("crop_selection_info")
            .replace("{w}", str(rect.width()))
            .replace("{h}", str(rect.height()))
            .replace("{x}", str(rect.x()))
            .replace("{y}", str(rect.y()))
        )
        if self._mode_combo.currentIndex() == 1:
            spins = self._manual_spins
            for spin, value in zip(spins, (rect.x(), rect.y(), rect.width(), rect.height())):
                spin.blockSignals(True)
                spin.setValue(value)
                spin.blockSignals(False)

    def get_options(self) -> CropOptions:
        if self._current_path is not None:
            rect = self._canvas.get_crop_rect()
            return CropOptions(
                mode="manual",
                x=rect.x(),
                y=rect.y(),
                width=rect.width(),
                height=rect.height(),
            )
        spins = self._manual_spins
        return CropOptions(
            mode="manual",
            x=spins[0].value(),
            y=spins[1].value(),
            width=spins[2].value(),
            height=spins[3].value(),
        )

    def validate(self) -> str | None:
        if self._current_path is None and not self.drop_zone.files:
            return tr("crop_no_image")
        return None

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("crop_title"), tr("crop_desc"))
        mode_items = [
            tr("crop_mode_ratio"),
            tr("crop_mode_manual"),
            tr("crop_mode_center"),
        ]
        for i, text in enumerate(mode_items):
            self._mode_combo.setItemText(i, text)
        for btn, key, _ in self._ratio_buttons:
            btn.setText(tr(key))
        self._reset_btn.setText(tr("crop_reset"))
        self._change_btn.setText(tr("crop_change_image"))
        self._preview_btn.setText(tr("crop_preview_btn"))
        self._undo_btn.setText(tr("crop_undo_btn"))
        if self._canvas.get_crop_rect().isValid():
            self._update_info(self._canvas.get_crop_rect())
