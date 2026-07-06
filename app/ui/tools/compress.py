from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QHBoxLayout, QSlider, QWidget

from app.models.tool_options import CompressOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelSpinBox, SelectAllLineEdit
from app.utils.i18n import tr


class CompressToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("compress_header"), tr("compress_desc"))
        self._build_ui()
        self.retranslate()

    def _build_ui(self) -> None:
        quality_widget = QWidget()
        ql = QHBoxLayout(quality_widget)
        ql.setContentsMargins(0, 0, 0, 0)
        self._quality_slider = QSlider(Qt.Orientation.Horizontal)
        self._quality_slider.setRange(1, 100)
        self._quality_slider.setValue(85)
        self._quality_spin = NoWheelSpinBox()
        self._quality_spin.setRange(1, 100)
        self._quality_spin.setValue(85)
        self._quality_spin.setSingleStep(5)
        self._quality_slider.valueChanged.connect(self._quality_spin.setValue)
        self._quality_spin.valueChanged.connect(self._quality_slider.setValue)
        ql.addWidget(self._quality_slider, 1)
        ql.addWidget(self._quality_spin)
        self._opt_row(tr("compress_quality"), quality_widget)

        self._target_edit = SelectAllLineEdit("0")
        self._opt_row(tr("compress_target_kb"), self._target_edit)

        self._keep_format_cb = QCheckBox()
        self._add_option_checkbox(self._keep_format_cb)

        from app.ui.widgets.result_preview import ResultPreviewWidget

        self._result_preview = ResultPreviewWidget()
        self.add_preview(self._result_preview)

    def get_options(self) -> CompressOptions:
        try:
            target_kb = int(self._target_edit.text().strip() or "0")
        except ValueError:
            target_kb = 0
        return CompressOptions(
            quality=self._quality_spin.value(),
            target_kb=max(0, target_kb),
            keep_format=self._keep_format_cb.isChecked(),
        )

    def validate(self) -> str | None:
        if self._quality_spin.value() > 0:
            return None
        return tr("compress_quality_invalid")

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("compress_header"), tr("compress_desc"))
        self._target_edit.setPlaceholderText("0")
        self._keep_format_cb.setText(tr("compress_keep_format"))
