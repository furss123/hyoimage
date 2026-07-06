from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from app.models.tool_options import ConvertOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelComboBox
from app.utils.i18n import tr


class ConvertToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("convert_title"), tr("convert_desc"))
        self._bg_color = "#FFFFFF"
        self._selected_quality = 90
        self._build_ui()
        self._format_combo.currentIndexChanged.connect(self._update_visibility)
        self._update_bg_swatch()
        self._update_visibility()
        self.retranslate()

    def _build_ui(self) -> None:
        self._format_combo = NoWheelComboBox()
        for fmt in ("JPEG", "PNG", "WEBP", "BMP", "TIFF", "GIF", "ICO"):
            self._format_combo.addItem("", fmt)
        self._opt_row(tr("convert_format"), self._format_combo)

        quality_widget = QWidget()
        ql = QHBoxLayout(quality_widget)
        ql.setContentsMargins(0, 0, 0, 0)
        ql.setSpacing(6)

        self._quality_btns: list[QPushButton] = []
        self._quality_keys = [
            ("convert_quality_low", 40),
            ("convert_quality_medium", 65),
            ("convert_quality_good", 80),
            ("convert_quality_high", 90),
            ("convert_quality_best", 95),
        ]
        for key, value in self._quality_keys:
            btn = QPushButton()
            btn.setObjectName("quickRotate")
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setProperty("quality_value", value)
            btn.setProperty("quality_key", key)
            btn.clicked.connect(lambda checked, b=btn: self._select_quality(b))
            ql.addWidget(btn)
            self._quality_btns.append(btn)

        self._quality_btns[3].setChecked(True)
        self._quality_row = self._opt_row(
            tr("convert_quality"), quality_widget, min_height=48
        )

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
        self._bg_btn.setToolTip(tr("convert_pick_color"))
        self._bg_btn.clicked.connect(self._pick_color)

        self._transparent_cb = QCheckBox()
        self._transparent_cb.setObjectName("colorOptionCheckbox")
        self._transparent_cb.setChecked(False)
        self._transparent_cb.toggled.connect(self._on_transparent_toggle)

        bl.addWidget(self._bg_btn)
        bl.addWidget(self._transparent_cb)
        bl.addStretch()
        self._bg_row = self._opt_row(
            tr("convert_bg_color"), bg_widget, min_height=48
        )

        from app.ui.widgets.result_preview import ResultPreviewWidget

        self._result_preview = ResultPreviewWidget()
        self.add_preview(self._result_preview)

    def _select_quality(self, clicked_btn: QPushButton) -> None:
        for btn in self._quality_btns:
            btn.setChecked(btn is clicked_btn)
        self._selected_quality = int(clicked_btn.property("quality_value"))

    def get_options(self) -> ConvertOptions:
        return ConvertOptions(
            format=self._format_combo.currentData(),
            quality=self._selected_quality,
            bg_color=(
                "transparent"
                if self._transparent_cb.isChecked()
                else self._bg_color
            ),
        )

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("convert_title"), tr("convert_desc"))
        self._format_combo.setItemText(0, "JPG")
        self._format_combo.setItemText(1, "PNG")
        self._format_combo.setItemText(2, "WEBP")
        self._format_combo.setItemText(3, "BMP")
        self._format_combo.setItemText(4, "TIFF")
        self._format_combo.setItemText(5, "GIF")
        self._format_combo.setItemText(6, "ICO")
        for btn in self._quality_btns:
            key = btn.property("quality_key")
            if key:
                btn.setText(tr(str(key)))
        self._transparent_cb.setText(tr("transparent_bg"))
        self._bg_btn.setToolTip(tr("convert_pick_color"))

    def _update_visibility(self) -> None:
        fmt = self._format_combo.currentData()
        self._quality_row.setVisible(fmt in ("JPEG", "WEBP"))
        self._bg_row.setVisible(fmt == "JPEG")

    def _update_bg_swatch(self) -> None:
        self._bg_btn.setStyleSheet(
            f"background: {self._bg_color}; "
            f"border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
        )

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._bg_color), self, tr("convert_bg_color"))
        if color.isValid():
            self._bg_color = color.name()
            self._update_bg_swatch()
            self._transparent_cb.setChecked(False)

    def _on_transparent_toggle(self, checked: bool) -> None:
        self._bg_btn.setEnabled(not checked)
        if checked:
            self._bg_btn.setStyleSheet(
                "background: qlineargradient("
                "x1:0,y1:0,x2:1,y2:1,"
                "stop:0 #ffffff,stop:0.5 #cccccc,"
                "stop:0.5 #999999,stop:1 #666666);"
                "border: 1px solid rgba(128, 128, 128, 0.45); border-radius: 4px; padding: 0;"
            )
        else:
            self._update_bg_swatch()
