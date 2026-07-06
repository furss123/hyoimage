from __future__ import annotations

from pathlib import Path

from PIL import Image
from PyQt6.QtCore import QObject, QRunnable, Qt, QThreadPool, pyqtSignal
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QDragEnterEvent,
    QDragMoveEvent,
    QDropEvent,
    QMouseEvent,
    QPainter,
    QPen,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.models.file_item import FileItem
from app.settings import load_settings
from app.ui.theme import get_theme_color
from app.utils.i18n import tr

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".gif",
}

_IMAGE_FILTER = ";;".join(
    [
        "Images (*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif *.gif)",
        "All Files (*)",
    ]
)

_EMPTY_HEIGHT = 152
_WITH_FILES_HEIGHT = 148
_THUMB_SIZE = 56
_MAX_VISIBLE_THUMBS = 4
_DROP_ICON_SIZE = 52
_ICON_FRAME_WIDTH = 72
_ICON_FRAME_HEIGHT = 64


def _make_drop_icon_pixmap(color: QColor, size: int = _DROP_ICON_SIZE) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(color)
    pen.setWidthF(max(1.4, size / 17.0))
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    inset = max(4, size // 6)
    radius = max(3, size // 8)
    painter.drawRoundedRect(
        inset,
        inset,
        size - inset * 2,
        size - inset * 2,
        radius,
        radius,
    )
    base_y = size - inset - max(3, size // 8)
    mid_x = size // 2
    peak_y = inset + size // 3
    side = max(4, size // 6)
    painter.drawLine(inset + side, base_y, mid_x, peak_y)
    painter.drawLine(mid_x, peak_y, size - inset - side, base_y)
    sun = max(4, size // 6)
    painter.setBrush(QBrush(color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(size - inset - sun - 2, inset + size // 6, sun, sun)
    painter.end()
    return pixmap


def _is_image_path(path: Path) -> bool:
    name = path.name.lower()
    if "preview" in name or "tmp" in name:
        return False
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def _mime_has_images(mime_data) -> bool:
    if not mime_data.hasUrls():
        return False
    return any(_is_image_path(Path(url.toLocalFile())) for url in mime_data.urls())


def _paths_from_mime(mime_data) -> list[Path]:
    paths: list[Path] = []
    for url in mime_data.urls():
        path = Path(url.toLocalFile())
        if _is_image_path(path):
            paths.append(path.resolve())
    return paths


def _collect_images_from_folder(folder: Path) -> list[Path]:
    found: set[Path] = set()
    for path in folder.rglob("*"):
        if _is_image_path(path):
            found.add(path.resolve())
    return sorted(found)


def _make_thumbnail_label(path: Path, size: int = _THUMB_SIZE) -> QLabel:
    label = QLabel()
    label.setObjectName("dropThumb")
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pixmap = QPixmap(str(path))
    if not pixmap.isNull():
        scaled = pixmap.scaled(
            size,
            size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation,
        )
        x = max(0, (scaled.width() - size) // 2)
        y = max(0, (scaled.height() - size) // 2)
        label.setPixmap(scaled.copy(x, y, size, size))
    return label


def _make_more_label(count: int, size: int = _THUMB_SIZE) -> QLabel:
    label = QLabel(f"+{count}")
    label.setObjectName("dropThumbMore")
    label.setFixedSize(size, size)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return label


class _MetadataSignals(QObject):
    loaded = pyqtSignal(Path, int, int, str)


class _MetadataWorker(QRunnable):
    def __init__(self, path: Path, signals: _MetadataSignals) -> None:
        super().__init__()
        self._path = path
        self._signals = signals

    def run(self) -> None:
        width = 0
        height = 0
        fmt = ""
        try:
            with Image.open(self._path) as img:
                width, height = img.size
                fmt = (img.format or self._path.suffix.lstrip(".")).upper()
        except Exception:
            pass
        self._signals.loaded.emit(self._path, width, height, fmt)


class _DropContent(QFrame):
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._empty_widget = QWidget()
        empty_layout = QVBoxLayout(self._empty_widget)
        empty_layout.setContentsMargins(16, 12, 16, 12)
        empty_layout.setSpacing(0)

        self._icon_frame = QWidget()
        self._icon_frame.setObjectName("dropIconFrame")
        self._icon_frame.setFixedSize(_ICON_FRAME_WIDTH, _ICON_FRAME_HEIGHT)
        icon_frame_layout = QVBoxLayout(self._icon_frame)
        icon_frame_layout.setContentsMargins(0, 0, 0, 0)
        icon_frame_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon = QLabel()
        self._icon.setObjectName("dropIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setFixedSize(_DROP_ICON_SIZE, _DROP_ICON_SIZE)
        icon_frame_layout.addWidget(self._icon)

        empty_layout.addStretch(1)
        empty_layout.addWidget(self._icon_frame, alignment=Qt.AlignmentFlag.AlignHCenter)
        empty_layout.addSpacing(12)

        self._hint = QLabel()
        self._hint.setObjectName("dropHint")
        self._hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint.setWordWrap(True)
        empty_layout.addWidget(self._hint, alignment=Qt.AlignmentFlag.AlignHCenter)
        empty_layout.addSpacing(6)

        self._sub_hint = QLabel()
        self._sub_hint.setObjectName("dropSubHint")
        self._sub_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_hint.setWordWrap(True)
        empty_layout.addWidget(self._sub_hint, alignment=Qt.AlignmentFlag.AlignHCenter)
        empty_layout.addStretch(1)

        layout.addWidget(self._empty_widget, 1)

        self._files_widget = QWidget()
        files_layout = QVBoxLayout(self._files_widget)
        files_layout.setContentsMargins(12, 12, 12, 12)
        files_layout.setSpacing(8)
        files_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._thumb_row_host = QWidget()
        self._thumb_row = QHBoxLayout(self._thumb_row_host)
        self._thumb_row.setContentsMargins(0, 0, 0, 0)
        self._thumb_row.setSpacing(8)
        self._thumb_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        files_layout.addWidget(self._thumb_row_host)

        self._filename_lbl = QLabel()
        self._filename_lbl.setObjectName("dropFilename")
        self._filename_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._filename_lbl.setWordWrap(False)
        files_layout.addWidget(self._filename_lbl)

        self._count_lbl = QLabel()
        self._count_lbl.setObjectName("dropCount")
        self._count_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        files_layout.addWidget(self._count_lbl)

        self._files_widget.hide()
        layout.addWidget(self._files_widget, 1)
        self._update_icon_color()

    def _update_icon_color(self) -> None:
        theme = load_settings().theme
        color = QColor(get_theme_color(theme, "text_3"))
        self._icon.setPixmap(_make_drop_icon_pixmap(color))

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self._update_icon_color()

    def update_drop_zone(self, files: list[FileItem]) -> None:
        while self._thumb_row.count():
            item = self._thumb_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if not files:
            self._empty_widget.setVisible(True)
            self._files_widget.setVisible(False)
            return

        self._empty_widget.setVisible(False)
        self._files_widget.setVisible(True)

        for item in files[:_MAX_VISIBLE_THUMBS]:
            self._thumb_row.addWidget(_make_thumbnail_label(item.path))

        remaining = len(files) - _MAX_VISIBLE_THUMBS
        if remaining > 0:
            self._thumb_row.addWidget(_make_more_label(remaining))

        first_name = files[0].filename
        metrics = self._filename_lbl.fontMetrics()
        elided = metrics.elidedText(
            first_name,
            Qt.TextElideMode.ElideMiddle,
            max(self.width() - 48, 120),
        )
        self._filename_lbl.setText(elided)
        self._filename_lbl.setToolTip(first_name)
        self._count_lbl.setText(
            tr("drop_files_count").replace("{count}", str(len(files)))
        )

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if not self._files_widget.isVisible() and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if _mime_has_images(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent) -> None:
        if _mime_has_images(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        paths = _paths_from_mime(event.mimeData())
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()
        else:
            event.ignore()


class DropZone(QWidget):
    files_changed = pyqtSignal(list)

    def __init__(self) -> None:
        super().__init__()
        self._files: list[FileItem] = []
        self._pool = QThreadPool.globalInstance()
        self._metadata_signals = _MetadataSignals()
        self._metadata_signals.loaded.connect(self._on_metadata_loaded)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._content = _DropContent()
        self._content.files_dropped.connect(self.add_files)
        self._content.clicked.connect(self.add_files_dialog)
        layout.addWidget(self._content, 1)

        self._update_height()
        self.retranslate()

    @property
    def files(self) -> list[FileItem]:
        return list(self._files)

    def update_drop_zone(self, files: list[FileItem] | None = None) -> None:
        if files is None:
            files = self._files
        self._content.update_drop_zone(files)
        self._update_height()

    def add_files(self, paths: list[Path]) -> None:
        paths = [
            Path(p)
            for p in paths
            if _is_image_path(Path(p).resolve())
        ]
        existing = {item.path for item in self._files}
        for raw in paths:
            path = Path(raw).resolve()
            if path in existing:
                continue
            existing.add(path)
            item = FileItem(path=path)
            self._files.append(item)
            self._queue_metadata(item)
        self.update_drop_zone()
        self.files_changed.emit(self._files)

    def clear(self) -> None:
        self._files.clear()
        self.update_drop_zone()
        self.files_changed.emit(self._files)

    def add_files_dialog(self) -> None:
        selected, _ = QFileDialog.getOpenFileNames(
            self,
            tr("add_files"),
            "",
            _IMAGE_FILTER,
        )
        if selected:
            self.add_files([Path(p) for p in selected])

    def add_folder_dialog(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, tr("add_folder"))
        if folder:
            self.add_files(_collect_images_from_folder(Path(folder)))

    def retranslate(self) -> None:
        self._content._hint.setText(tr("drop_hint"))
        self._content._sub_hint.setText(tr("drop_hint_sub"))
        self._content._update_icon_color()
        if self._files:
            self.update_drop_zone()

    def _update_height(self) -> None:
        height = _EMPTY_HEIGHT if not self._files else _WITH_FILES_HEIGHT
        self.setMinimumHeight(height)
        self.setMaximumHeight(height)

    def _queue_metadata(self, item: FileItem) -> None:
        worker = _MetadataWorker(item.path, self._metadata_signals)
        self._pool.start(worker)

    def _on_metadata_loaded(self, path: Path, width: int, height: int, fmt: str) -> None:
        item = next((f for f in self._files if f.path == path), None)
        if item is None:
            return

        if width > 0 and height > 0:
            item.width = width
            item.height = height
        if fmt:
            item.format = fmt
