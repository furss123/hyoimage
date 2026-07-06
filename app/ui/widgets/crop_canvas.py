from __future__ import annotations

from PyQt6.QtCore import QPoint, QRect, QRectF, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QPixmap, QRegion
from PyQt6.QtWidgets import QWidget


class CropCanvas(QWidget):
    crop_changed = pyqtSignal(QRect)

    def __init__(self) -> None:
        super().__init__()
        self._pixmap: QPixmap | None = None
        self._display_pixmap: QPixmap | None = None
        self._scale = 1.0
        self._offset = QPoint(0, 0)
        self._crop_rect = QRect()
        self._drag_start: QPoint | None = None
        self._drag_mode: str | tuple[str, int] | None = None
        self._drag_rect = QRect()
        self._handle_size = 8
        self._ratio: tuple[int, int] | None = None
        self._show_loupe = False
        self._loupe_pos = QPoint()
        self._loupe_size = 120
        self._loupe_zoom = 4
        self._loupe_src_size = 30
        self.setMinimumHeight(220)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

    def set_image(self, pixmap: QPixmap) -> None:
        self._pixmap = pixmap
        self._update_display()
        if self._display_pixmap is not None:
            self._crop_rect = QRect(
                self._offset,
                QSize(self._display_pixmap.width(), self._display_pixmap.height()),
            )
        self.update()
        self.crop_changed.emit(self.get_crop_rect())

    def set_ratio(self, ratio: tuple[int, int] | None) -> None:
        self._ratio = ratio
        if not ratio or self._display_pixmap is None:
            return
        img_rect = QRect(
            self._offset,
            QSize(self._display_pixmap.width(), self._display_pixmap.height()),
        )
        w = img_rect.width()
        h = int(w * ratio[1] / ratio[0])
        if h > img_rect.height():
            h = img_rect.height()
            w = int(h * ratio[0] / ratio[1])
        x = img_rect.x() + (img_rect.width() - w) // 2
        y = img_rect.y() + (img_rect.height() - h) // 2
        self._crop_rect = QRect(x, y, w, h)
        self.update()
        self.crop_changed.emit(self.get_crop_rect())

    def set_center_square(self) -> None:
        bounds = self._image_bounds()
        if bounds.isEmpty():
            return
        side = min(bounds.width(), bounds.height())
        x = bounds.left() + (bounds.width() - side) // 2
        y = bounds.top() + (bounds.height() - side) // 2
        self._crop_rect = QRect(x, y, side, side)
        self._ratio = (1, 1)
        self.update()
        self.crop_changed.emit(self.get_crop_rect())

    def reset_crop(self) -> None:
        if self._display_pixmap is not None:
            self._crop_rect = QRect(self._offset, self._display_pixmap.size())
            self._crop_rect = self._clamp_to_image(self._crop_rect)
            self.update()
            self.crop_changed.emit(self.get_crop_rect())

    def get_crop_rect(self) -> QRect:
        return self._display_to_image(self._crop_rect)

    def _image_bounds(self) -> QRect:
        if self._display_pixmap is None:
            return QRect()
        return QRect(self._offset, self._display_pixmap.size())

    def _clamp_to_image(self, rect: QRect) -> QRect:
        if self._display_pixmap is None:
            return rect
        img_rect = QRect(
            self._offset,
            QSize(self._display_pixmap.width(), self._display_pixmap.height()),
        )
        return rect.normalized().intersected(img_rect)

    def _update_display(self) -> None:
        if not self._pixmap:
            return
        available = self.size()
        scaled = self._pixmap.scaled(
            available.width(),
            available.height(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self._display_pixmap = scaled
        self._scale = scaled.width() / self._pixmap.width() if self._pixmap.width() else 1.0
        self._offset = QPoint(
            (available.width() - scaled.width()) // 2,
            (available.height() - scaled.height()) // 2,
        )

    def _display_to_image(self, rect: QRect) -> QRect:
        if not self._scale:
            return QRect()
        return QRect(
            int((rect.x() - self._offset.x()) / self._scale),
            int((rect.y() - self._offset.y()) / self._scale),
            max(1, int(rect.width() / self._scale)),
            max(1, int(rect.height() / self._scale)),
        )

    def _image_to_display(self, rect: QRect) -> QRect:
        return QRect(
            self._offset.x() + int(rect.x() * self._scale),
            self._offset.y() + int(rect.y() * self._scale),
            max(1, int(rect.width() * self._scale)),
            max(1, int(rect.height() * self._scale)),
        )

    def set_crop_rect(self, x: int, y: int, w: int, h: int) -> None:
        if self._display_pixmap is None:
            return
        display_rect = self._image_to_display(QRect(x, y, w, h))
        self._crop_rect = self._clamp_to_image(display_rect)
        self.update()
        self.crop_changed.emit(self.get_crop_rect())

    def _get_handles(self) -> list[QPoint]:
        r = self._crop_rect
        return [
            r.topLeft(),
            r.topRight(),
            r.bottomLeft(),
            r.bottomRight(),
            QPoint(r.center().x(), r.top()),
            QPoint(r.center().x(), r.bottom()),
            QPoint(r.left(), r.center().y()),
            QPoint(r.right(), r.center().y()),
        ]

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.fillRect(self.rect(), QColor("#0C0C0C"))

        if not self._display_pixmap:
            return

        p.drawPixmap(self._offset, self._display_pixmap)

        if not self._crop_rect.isEmpty():
            outside = QRegion(QRect(self._offset, self._display_pixmap.size()))
            outside -= QRegion(self._crop_rect)
            p.setClipRegion(outside)
            p.fillRect(self.rect(), QColor(0, 0, 0, 120))
            p.setClipping(False)

            p.setPen(QPen(QColor("#006EE4"), 1.5))
            p.drawRect(self._crop_rect)

            p.setPen(QPen(QColor(255, 255, 255, 40), 0.5))
            r = self._crop_rect
            for i in (1, 2):
                x = r.x() + r.width() * i // 3
                y = r.y() + r.height() * i // 3
                p.drawLine(x, r.y(), x, r.y() + r.height())
                p.drawLine(r.x(), y, r.x() + r.width(), y)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#006EE4"))
            h = self._handle_size
            for corner in self._get_handles():
                p.drawRect(corner.x() - h // 2, corner.y() - h // 2, h, h)

        if self._show_loupe and self._display_pixmap:
            self._draw_loupe(p, self._loupe_pos)

    def _draw_loupe(self, p: QPainter, cursor: QPoint) -> None:
        ls = self._loupe_size
        src = self._loupe_src_size

        src_rect = QRect(
            cursor.x() - src // 2,
            cursor.y() - src // 2,
            src,
            src,
        )

        lx = cursor.x() + 16
        ly = cursor.y() - ls - 16
        if lx + ls > self.width():
            lx = cursor.x() - ls - 16
        if ly < 0:
            ly = cursor.y() + 16

        loupe_rect = QRect(lx, ly, ls, ls)

        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(loupe_rect.adjusted(3, 3, 3, 3))

        path = QPainterPath()
        path.addEllipse(QRectF(loupe_rect))
        p.setClipPath(path)

        pix_src = QRect(
            src_rect.x() - self._offset.x(),
            src_rect.y() - self._offset.y(),
            src,
            src,
        )
        pix_bounds = QRect(0, 0, self._display_pixmap.width(), self._display_pixmap.height())
        pix_src = pix_src.intersected(pix_bounds)
        if not pix_src.isEmpty():
            p.drawPixmap(loupe_rect, self._display_pixmap, pix_src)

        p.setClipping(False)

        pen = QPen(QColor("#006EE4"), 2)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(loupe_rect)

        cx = loupe_rect.center().x()
        cy = loupe_rect.center().y()
        p.setPen(QPen(QColor("#006EE4"), 1))
        p.drawLine(cx - 8, cy, cx + 8, cy)
        p.drawLine(cx, cy - 8, cx, cy + 8)

        img_pt = self._display_to_image(QRect(cursor.x(), cursor.y(), 1, 1))
        coord_text = f"{img_pt.x()}, {img_pt.y()}"
        p.setPen(QColor("#AAAAAA"))
        p.setFont(QFont("Segoe UI", 9))
        p.drawText(
            QRect(lx, ly + ls + 4, ls, 16),
            Qt.AlignmentFlag.AlignCenter,
            coord_text,
        )

        p.restore()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.pos()
        hit = self._handle_size + 4
        for i, handle in enumerate(self._get_handles()):
            if (pos - handle).manhattanLength() < hit:
                self._drag_mode = ("resize", i)
                self._drag_start = pos
                self._drag_rect = QRect(self._crop_rect)
                self._show_loupe = True
                self._loupe_pos = pos
                self.update()
                return
        if self._crop_rect.contains(pos):
            self._drag_mode = "move"
            self._drag_start = pos
            self._drag_rect = QRect(self._crop_rect)
        else:
            self._drag_mode = "create"
            self._drag_start = pos
            self._crop_rect = QRect(pos, pos)
        self._show_loupe = True
        self._loupe_pos = pos
        self.update()

    def mouseMoveEvent(self, event) -> None:
        pos = event.pos()
        h = self._handle_size + 6
        near_handle = any(
            (pos - handle).manhattanLength() < h
            for handle in self._get_handles()
        )
        self._show_loupe = self._drag_mode is not None or near_handle
        self._loupe_pos = pos

        if self._drag_mode and self._drag_start is not None:
            if self._drag_mode == "create":
                rect = QRect(self._drag_start, pos).normalized()
                if self._ratio:
                    w = rect.width()
                    h_ratio = max(1, int(w * self._ratio[1] / self._ratio[0]))
                    rect.setHeight(h_ratio)
                self._crop_rect = self._clamp_to_image(rect)
            elif self._drag_mode == "move":
                delta = pos - self._drag_start
                self._crop_rect = self._clamp_to_image(self._drag_rect.translated(delta))
            elif isinstance(self._drag_mode, tuple) and self._drag_mode[0] == "resize":
                self._crop_rect = self._clamp_to_image(
                    self._resize_from_handle(self._drag_rect, self._drag_mode[1], pos)
                )
            self.crop_changed.emit(self.get_crop_rect())

        self.update()

    def _resize_from_handle(self, rect: QRect, handle: int, pos: QPoint) -> QRect:
        r = QRect(rect)
        if handle in (0, 4, 6):
            r.setLeft(pos.x())
        if handle in (1, 4, 7):
            r.setRight(pos.x())
        if handle in (0, 2, 6):
            r.setTop(pos.y())
        if handle in (1, 3, 7):
            r.setBottom(pos.y())
        if handle == 2:
            r.setBottom(pos.y())
        if handle == 3:
            r.setBottom(pos.y())
            r.setRight(pos.x())
        if handle == 5:
            r.setBottom(pos.y())
        r = r.normalized()
        if self._ratio:
            w = r.width()
            h = max(1, int(w * self._ratio[1] / self._ratio[0]))
            r.setHeight(h)
        return r

    def mouseReleaseEvent(self, event) -> None:
        self._drag_mode = None
        self._drag_start = None
        self._show_loupe = False
        self.update()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._pixmap:
            old = self.get_crop_rect()
            self._update_display()
            if self._display_pixmap is not None:
                self._crop_rect = QRect(
                    self._offset.x() + int(old.x() * self._scale),
                    self._offset.y() + int(old.y() * self._scale),
                    int(old.width() * self._scale),
                    int(old.height() * self._scale),
                )
                self._crop_rect = self._clamp_to_image(self._crop_rect)
            self.update()
