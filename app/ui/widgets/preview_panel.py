import io
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import Qt, QBuffer, QIODevice
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.preview_worker import BeforePreviewWorker, close_image
from app.utils.i18n import tr


class PreviewPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._before_pm: QPixmap | None = None
        self._after_pm: QPixmap | None = None
        self._before_image: Image.Image | None = None
        self._current_after: Image.Image | None = None
        self._history: list[tuple[QPixmap, Image.Image]] = []
        self._mode = "before"
        self._before_worker: BeforePreviewWorker | None = None
        self._load_token = 0
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 6, 0, 0)
        root.setSpacing(6)

        toggle = QHBoxLayout()
        toggle.setSpacing(4)
        self._btn_before = QPushButton()
        self._btn_after = QPushButton()
        for btn in (self._btn_before, self._btn_after):
            btn.setObjectName("quickRotate")
            btn.setFixedSize(52, 26)
        self._btn_before.clicked.connect(lambda: self._switch("before"))
        self._btn_after.clicked.connect(lambda: self._switch("after"))
        toggle.addWidget(self._btn_before)
        toggle.addWidget(self._btn_after)
        toggle.addStretch()
        self._undo_btn = QPushButton()
        self._undo_btn.setObjectName("fileBtn")
        self._undo_btn.setFixedHeight(26)
        self._undo_btn.setVisible(False)
        toggle.addWidget(self._undo_btn)
        root.addLayout(toggle)

        self._undo_btn.clicked.connect(self._undo)

        self._status = QLabel()
        self._update_status_style()
        self._status.setVisible(False)
        root.addWidget(self._status)

        self._lbl = QLabel()
        self._lbl.setObjectName("resultPreview")
        self._lbl.setScaledContents(False)
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl.setMinimumHeight(120)
        self._lbl.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._lbl.setText(tr("preview_empty_hint"))
        root.addWidget(self._lbl, stretch=1)
        self.retranslate()

    @staticmethod
    def _pixmap_to_pil(pm: QPixmap) -> Image.Image:
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pm.save(buffer, "PNG")
        pil = Image.open(io.BytesIO(buffer.data().data())).copy()
        buffer.close()
        return pil

    @staticmethod
    def _pil_to_pixmap(pil_image: Image.Image) -> QPixmap:
        buf = io.BytesIO()
        fmt = "PNG" if pil_image.mode == "RGBA" else "JPEG"
        pil_image.save(buf, format=fmt)
        pm = QPixmap()
        pm.loadFromData(buf.getvalue())
        return pm

    def _panel_size(self) -> tuple[int, int]:
        avail_w = max(self._lbl.width() or self.width() - 48, 200)
        avail_h = max(self._lbl.height() or self.height() - 80, 200)
        return avail_w, avail_h

    def _fit_pixmap(self, pm: QPixmap) -> QPixmap:
        w, h = self._panel_size()
        return pm.scaled(
            w,
            h,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _cancel_before_worker(self) -> None:
        if self._before_worker is not None and self._before_worker.isRunning():
            self._before_worker.requestInterruption()
            self._before_worker.wait(100)
        self._before_worker = None

    def _close_stored_images(self) -> None:
        close_image(self._before_image)
        self._before_image = None
        close_image(self._current_after)
        self._current_after = None
        for _, pil in self._history:
            close_image(pil)
        self._history.clear()

    def release_resources(self) -> None:
        self._cancel_before_worker()
        self._close_stored_images()
        self._before_pm = None
        self._after_pm = None
        self._undo_btn.setVisible(False)
        self._lbl.setPixmap(QPixmap())
        self._lbl.setText(tr("preview_empty_hint"))
        self._status.clear()
        self._status.setVisible(False)

    def set_before_async(self, path) -> None:
        path = Path(path)
        self._cancel_before_worker()
        self._load_token += 1
        token = self._load_token
        worker = BeforePreviewWorker(path, self._panel_size())
        self._before_worker = worker
        worker.loaded.connect(
            lambda thumb, full, t=token: self._on_before_loaded(t, thumb, full)
        )
        worker.failed.connect(self._on_before_failed)
        worker.finished.connect(self._on_before_worker_finished)
        worker.start()

    def _on_before_worker_finished(self) -> None:
        sender = self.sender()
        if sender is self._before_worker:
            self._before_worker = None

    def _on_before_loaded(self, token: int, thumb_bytes: bytes, full_bytes: bytes) -> None:
        if token != self._load_token:
            return
        self._close_stored_images()
        pm = QPixmap()
        pm.loadFromData(thumb_bytes)
        if pm.isNull():
            return
        self._before_pm = self._fit_pixmap(pm)
        opened = Image.open(io.BytesIO(full_bytes))
        self._before_image = opened.copy()
        close_image(opened)
        self._after_pm = None
        self._undo_btn.setVisible(False)
        self._switch("before")

    def _on_before_failed(self, _message: str) -> None:
        pass

    def commit_preview(
        self,
        before_pm: QPixmap,
        after_pm: QPixmap,
        result_image: Image.Image,
        status: str,
    ) -> None:
        if self._before_pm is not None and self._before_image is not None:
            self._history.append((self._before_pm.copy(), self._before_image.copy()))
            if len(self._history) > 10:
                _, old = self._history.pop(0)
                close_image(old)
        close_image(self._before_image)
        close_image(self._current_after)
        self._before_pm = before_pm
        self._after_pm = after_pm
        self._before_image = result_image.copy()
        self._current_after = result_image.copy()
        self._switch("after")
        self._undo_btn.setVisible(True)
        self.set_status(status)

    def apply_preview(self, result_image: Image.Image, status: str) -> None:
        after_pm = self._fit_pixmap(self._pil_to_pixmap(result_image))
        before_pm = self._before_pm or after_pm
        self.commit_preview(before_pm, after_pm, result_image, status)

    def apply_preview_bytes(
        self,
        before_pm: QPixmap,
        after_pm: QPixmap,
        export_bytes: bytes,
        status: str,
    ) -> None:
        opened = Image.open(io.BytesIO(export_bytes))
        export_copy = opened.copy()
        close_image(opened)
        self.commit_preview(before_pm, after_pm, export_copy, status)
        close_image(export_copy)

    def set_after_preview(self, after_bytes: bytes, export_bytes: bytes, status: str) -> None:
        pm = QPixmap()
        pm.loadFromData(after_bytes)
        if pm.isNull():
            return
        after_pm = self._fit_pixmap(pm)
        close_image(self._current_after)
        opened = Image.open(io.BytesIO(export_bytes))
        self._current_after = opened.copy()
        close_image(opened)
        self._after_pm = after_pm
        self._switch("after")
        self.set_status(status)

    def set_status(self, text: str) -> None:
        self._status.setText(text)
        self._status.setVisible(bool(text))

    def clear(self) -> None:
        self.release_resources()

    def get_current_image(self) -> QPixmap | None:
        return self._before_pm

    def get_source_pil(self) -> Image.Image | None:
        if self._before_image is not None:
            return self._before_image.copy()
        return None

    def get_source_bytes(self) -> bytes | None:
        if self._before_image is None:
            return None
        buf = io.BytesIO()
        self._before_image.save(buf, format="PNG")
        return buf.getvalue()

    def get_export_image(self) -> Image.Image | None:
        if self._current_after is not None:
            return self._current_after.copy()
        return None

    def _undo(self) -> None:
        if not self._history:
            return
        close_image(self._before_image)
        close_image(self._current_after)
        self._before_pm, self._before_image = self._history.pop()
        self._after_pm = None
        self._current_after = self._before_image.copy()
        self._switch("before")
        self._undo_btn.setVisible(len(self._history) > 0)
        self.set_status(tr("preview_undo_done"))

    def retranslate(self) -> None:
        self._btn_before.setText(tr("preview_before"))
        self._btn_after.setText(tr("preview_after"))
        self._undo_btn.setText(tr("preview_undo"))
        self._update_status_style()
        if not (self._before_pm or self._after_pm):
            self._lbl.setText(tr("preview_empty_hint"))

    def _update_status_style(self) -> None:
        color = self.palette().color(self.foregroundRole())
        self._status.setStyleSheet(
            f"font-size:11px; color:{color.name()}; background:transparent;"
        )

    def _switch(self, mode: str) -> None:
        self._mode = mode
        pm = self._before_pm if mode == "before" else self._after_pm
        if pm and not pm.isNull():
            self._lbl.setPixmap(self._fit_pixmap(pm))
            self._lbl.setText("")
        else:
            self._lbl.setPixmap(QPixmap())
            self._lbl.setText(tr("preview_empty_hint"))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        pm = self._before_pm if self._mode == "before" else self._after_pm
        if pm and not pm.isNull():
            self._lbl.setPixmap(self._fit_pixmap(pm))

