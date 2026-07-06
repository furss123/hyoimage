from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget

from app.ui.widgets.preview_worker import FilePixmapWorker
from app.utils.i18n import tr


class ResultPreviewWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._source_path = None
        self._cached_pixmap: QPixmap | None = None
        self._load_worker: FilePixmapWorker | None = None
        self._load_token = 0
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(0)

        self._label = QLabel()
        self._label.setObjectName("resultPreview")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumHeight(120)
        self._label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        layout.addWidget(self._label, stretch=1)
        self.show_placeholder()

    def release_resources(self) -> None:
        if self._load_worker is not None and self._load_worker.isRunning():
            self._load_worker.requestInterruption()
            self._load_worker.wait(100)
        self._load_worker = None
        self._cached_pixmap = None
        self._source_path = None
        self._label.setPixmap(QPixmap())
        self._label.setText(tr("result_preview_placeholder"))

    def show_placeholder(self, text: str | None = None) -> None:
        self.release_resources()
        if text is not None:
            self._label.setText(text)

    def show_image(self, path) -> None:
        self._source_path = Path(path)
        self._load_token += 1
        token = self._load_token
        if self._load_worker is not None and self._load_worker.isRunning():
            self._load_worker.requestInterruption()
            self._load_worker.wait(100)
        worker = FilePixmapWorker(self._source_path)
        self._load_worker = worker
        worker.loaded.connect(
            lambda data, t=token: self._on_image_loaded(t, data)
        )
        worker.failed.connect(lambda _msg, t=token: self._on_image_failed(t))
        worker.finished.connect(self._on_load_worker_finished)
        worker.start()

    def _on_load_worker_finished(self) -> None:
        sender = self.sender()
        if sender is self._load_worker:
            self._load_worker = None

    def _on_image_failed(self, token: int) -> None:
        if token != self._load_token:
            return
        self.show_placeholder()

    def _on_image_loaded(self, token: int, data: bytes) -> None:
        if token != self._load_token:
            return
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        if pixmap.isNull():
            self.show_placeholder()
            return
        self._cached_pixmap = pixmap
        self._apply_scaled_pixmap()

    def _apply_scaled_pixmap(self) -> None:
        if self._cached_pixmap is None or self._cached_pixmap.isNull():
            return
        target = self._label.size()
        if target.width() < 2 or target.height() < 2:
            target = self._cached_pixmap.size()
        scaled = self._cached_pixmap.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._label.setPixmap(scaled)
        self._label.setText("")

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._cached_pixmap is not None:
            self._apply_scaled_pixmap()
