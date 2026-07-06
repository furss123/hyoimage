from PyQt6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.tool_options import BulkRenameOptions
from app.ui.tools.base_tool_widget import BaseToolWidget
from app.ui.widgets.no_wheel_widgets import NoWheelSpinBox, SelectAllLineEdit
from app.utils.i18n import tr


class BulkRenameToolWidget(BaseToolWidget):
    def __init__(self) -> None:
        super().__init__(tr("bulk_rename_title"), tr("bulk_rename_desc"))
        self._prefix_edit = SelectAllLineEdit("image_")
        self._prefix_row = self._opt_row(tr("bulk_rename_prefix"), self._prefix_edit)

        self._start_spin = NoWheelSpinBox()
        self._start_spin.setRange(1, 99999)
        self._start_spin.setValue(1)
        self._start_spin.setSingleStep(1)
        self._start_row = self._opt_row(tr("bulk_rename_start"), self._start_spin)

        self._padding_spin = NoWheelSpinBox()
        self._padding_spin.setRange(1, 6)
        self._padding_spin.setValue(3)
        self._padding_spin.setSingleStep(1)
        self._padding_row = self._opt_row(tr("bulk_rename_padding"), self._padding_spin)

        preview_wrap = QWidget()
        preview_wrap.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        preview_layout = QVBoxLayout(preview_wrap)
        preview_layout.setContentsMargins(0, 12, 0, 0)
        preview_layout.setSpacing(4)
        self._pattern_lbl = QLabel()
        preview_layout.addWidget(self._pattern_lbl)

        self._preview_table = QTableWidget(0, 2)
        self._preview_table.setObjectName("bulkPreviewTable")
        self._preview_table.setHorizontalHeaderLabels(["", ""])
        header = self._preview_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        self._preview_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._preview_table.setShowGrid(False)
        self._preview_table.setFrameShape(QFrame.Shape.NoFrame)
        self._preview_table.setMinimumHeight(140)
        self._preview_table.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        preview_layout.addWidget(self._preview_table, stretch=1)
        self.add_preview(preview_wrap)

        self._prefix_edit.textChanged.connect(self._update_preview)
        self._start_spin.valueChanged.connect(self._update_preview)
        self._padding_spin.valueChanged.connect(self._update_preview)
        self.drop_zone.files_changed.connect(self._update_preview)

        self.retranslate()
        self._update_preview()

    def _update_preview(self, *_args) -> None:
        files = self.drop_zone.files
        if not files:
            self._preview_table.setRowCount(0)
            return
        prefix = self._prefix_edit.text()
        start = self._start_spin.value()
        pad = self._padding_spin.value()
        rows = min(5, len(files))
        self._preview_table.setRowCount(rows)
        for i, f in enumerate(files[:rows]):
            idx = str(start + i).zfill(pad)
            new_name = f"{prefix}{idx}{f.path.suffix}"
            self._preview_table.setItem(i, 0, QTableWidgetItem(f.path.name))
            self._preview_table.setItem(i, 1, QTableWidgetItem(new_name))

    def get_options(self) -> BulkRenameOptions:
        return BulkRenameOptions(
            prefix=self._prefix_edit.text().strip() or "image_",
            start_number=self._start_spin.value(),
            padding=self._padding_spin.value(),
        )

    def retranslate(self) -> None:
        super().retranslate()
        self._update_header(tr("bulk_rename_title"), tr("bulk_rename_desc"))
        self._pattern_lbl.setText(tr("bulk_rename_preview_title"))
        color = self.palette().color(self.foregroundRole())
        self._pattern_lbl.setStyleSheet(
            f"font-size:12px; color:{color.name()}; background:transparent;"
        )
        self._preview_table.setHorizontalHeaderLabels(
            [tr("bulk_rename_col_current"), tr("bulk_rename_col_new")]
        )
