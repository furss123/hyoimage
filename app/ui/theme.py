BRAND = {
    "blue": "#006EE4",
    "purple": "#8429D3",
    "orange": "#FF6000",
    "teal": "#008684",
}

_TOOL_ACCENT_CYCLE = [BRAND["blue"], BRAND["purple"], BRAND["orange"], BRAND["teal"]]

TOOL_ACCENT = {
    tool_id: _TOOL_ACCENT_CYCLE[i % len(_TOOL_ACCENT_CYCLE)]
    for i, tool_id in enumerate(
        ["resize", "compress", "convert", "rotate", "crop", "merge", "bulk_rename"]
    )
}

DARK = {
    "window": "#1A1A1A",
    "sidebar": "#111111",
    "surface": "#1E1E1E",
    "card": "#242424",
    "border": "#2E2E2E",
    "divider": "#333333",
    "text_1": "#ECECEC",
    "text_2": "#909090",
    "text_3": "#505050",
    "opt_label": "#707070",
    "accent": "#006EE4",
    "accent_hover": "#0057B3",
    "accent_tint": "rgba(0, 110, 228, 0.12)",
    "list_item": "#606060",
    "list_hover_bg": "rgba(255, 255, 255, 0.05)",
    "list_hover_text": "#B0B0B0",
    "list_selected_bg": "rgba(0, 110, 228, 0.12)",
    "list_selected_text": "#006EE4",
    "header_desc": "#888888",
    "sidebar_title": "#444444",
    "tool_header_bg": "#1A1A1A",
    "drop_bg": "#161616",
    "drop_border": "#2A2A2A",
    "drop_zone_border": "#666666",
    "drop_icon_bg": "#1C1C1C",
    "drop_hover_bg": "rgba(0, 110, 228, 0.03)",
    "drop_hover_border": "rgba(0, 110, 228, 0.22)",
    "input_bg": "#1E1E1E",
    "input_border": "#333333",
    "input_focus_bg": "#222222",
    "input_text": "#E8E8E8",
    "combo_popup_bg": "#1E1E1E",
    "combo_popup_border": "#2E2E2E",
    "selection_bg": "rgba(0, 110, 228, 0.12)",
    "btn_bg": "#1E1E1E",
    "btn_border": "#2E2E2E",
    "btn_text": "#808080",
    "btn_hover_bg": "#262626",
    "btn_hover_border": "#383838",
    "btn_hover_text": "#D0D0D0",
    "quick_rotate_border": "#282828",
    "quick_rotate_text": "#606060",
    "quick_rotate_hover_bg": "rgba(0, 110, 228, 0.12)",
    "quick_rotate_hover_border": "rgba(0, 110, 228, 0.38)",
    "quick_rotate_hover_text": "#006EE4",
    "file_btn_border": "#262626",
    "file_btn_text": "#505050",
    "file_btn_hover_bg": "#1E1E1E",
    "file_btn_hover_border": "#363636",
    "file_btn_hover_text": "#909090",
    "theme_btn_border": "#404040",
    "theme_btn_text": "#909090",
    "theme_btn_hover_bg": "#1E1E1E",
    "theme_btn_hover_text": "#808080",
    "slider_groove": "#2A2A2A",
    "checkbox_text": "#707070",
    "checkbox_border": "#303030",
    "checkbox_bg": "#1E1E1E",
    "output_bar_bg": "#111111",
    "output_bar_border": "#202020",
    "preview_label_bg": "#111111",
    "preview_label_text": "#303030",
    "log_panel_bg": "#111111",
    "log_text": "#666666",
    "table_grid": "#252525",
    "table_text": "#666666",
    "table_header": "#505050",
    "scrollbar_handle": "#303030",
    "scrollbar_handle_hover": "#404040",
    "status_bar_text": "#505050",
    "delete_btn_text": "#E57373",
    "delete_btn_border": "#E57373",
    "delete_btn_hover_bg": "rgba(229, 115, 115, 0.12)",
    "color_checkbox_border": "#555555",
}

LIGHT = {
    "window": "#F5F5F5",
    "sidebar": "#EBEBEB",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "border": "#E0E0E0",
    "divider": "#E0E0E0",
    "text_1": "#111111",
    "text_2": "#666666",
    "text_3": "#BBBBBB",
    "opt_label": "#666666",
    "accent": "#006EE4",
    "accent_hover": "#0057B3",
    "accent_tint": "rgba(0, 110, 228, 0.12)",
    "list_item": "#666666",
    "list_hover_bg": "rgba(0, 0, 0, 0.04)",
    "list_hover_text": "#333333",
    "list_selected_bg": "rgba(0, 110, 228, 0.12)",
    "list_selected_text": "#006EE4",
    "header_desc": "#888888",
    "sidebar_title": "#BBBBBB",
    "tool_header_bg": "#F5F5F5",
    "drop_bg": "#FAFAFA",
    "drop_border": "#D8D8D8",
    "drop_zone_border": "#999999",
    "drop_icon_bg": "#F0F0F0",
    "drop_hover_bg": "rgba(0, 110, 228, 0.04)",
    "drop_hover_border": "rgba(0, 110, 228, 0.28)",
    "input_bg": "#FFFFFF",
    "input_border": "#E0E0E0",
    "input_focus_bg": "#FFFFFF",
    "input_text": "#111111",
    "combo_popup_bg": "#FFFFFF",
    "combo_popup_border": "#E4E4E4",
    "selection_bg": "rgba(0, 110, 228, 0.12)",
    "btn_bg": "#FFFFFF",
    "btn_border": "#E4E4E4",
    "btn_text": "#666666",
    "btn_hover_bg": "#F5F5F5",
    "btn_hover_border": "#D0D0D0",
    "btn_hover_text": "#111111",
    "quick_rotate_border": "#E0E0E0",
    "quick_rotate_text": "#666666",
    "quick_rotate_hover_bg": "rgba(0, 110, 228, 0.12)",
    "quick_rotate_hover_border": "rgba(0, 110, 228, 0.38)",
    "quick_rotate_hover_text": "#006EE4",
    "file_btn_border": "#E4E4E4",
    "file_btn_text": "#888888",
    "file_btn_hover_bg": "#F5F5F5",
    "file_btn_hover_border": "#D0D0D0",
    "file_btn_hover_text": "#555555",
    "theme_btn_border": "#B8B8B8",
    "theme_btn_text": "#555555",
    "theme_btn_hover_bg": "#FFFFFF",
    "theme_btn_hover_text": "#666666",
    "slider_groove": "#E4E4E4",
    "checkbox_text": "#666666",
    "checkbox_border": "#D0D0D0",
    "checkbox_bg": "#FFFFFF",
    "output_bar_bg": "#F0F0F0",
    "output_bar_border": "#ECECEC",
    "preview_label_bg": "#F0F0F0",
    "preview_label_text": "#CCCCCC",
    "log_panel_bg": "#F0F0F0",
    "log_text": "#777777",
    "table_grid": "#ECECEC",
    "table_text": "#666666",
    "table_header": "#BBBBBB",
    "scrollbar_handle": "#D0D0D0",
    "scrollbar_handle_hover": "#BBBBBB",
    "status_bar_text": "#BBBBBB",
    "delete_btn_text": "#E57373",
    "delete_btn_border": "#E57373",
    "delete_btn_hover_bg": "rgba(229, 115, 115, 0.12)",
    "color_checkbox_border": "#BBBBBB",
}


def get_theme_color(theme: str, key: str) -> str:
    palette = LIGHT if theme == "light" else DARK
    return palette[key]


def get_tool_accent(tool_id: str) -> str:
    return TOOL_ACCENT.get(tool_id, BRAND["blue"])


def get_stylesheet(theme: str) -> str:
    t = LIGHT if theme == "light" else DARK

    return f"""
QMainWindow, QWidget {{
    background: {t["window"]};
    color: {t["text_1"]};
    font-family: 'Segoe UI', system-ui;
    font-size: 14px;
    border: none;
    outline: none;
}}

QWidget#sidebar {{
    background: {t["sidebar"]};
    border-right: 1px solid {t["divider"]};
}}

QLabel#iconLabel {{
    background: transparent;
}}

QLabel#appTitle,
QLabel#sidebarTitle {{
    font-size: 12px;
    font-weight: 600;
    color: {t["sidebar_title"]};
    letter-spacing: 1px;
    padding: 16px 16px 10px;
    background: transparent;
}}

QListWidget,
QListWidget#toolList {{
    background: transparent;
    border: none;
    padding: 2px 0px;
    outline: none;
}}

QListWidget::item {{
    font-size: 15px;
    font-weight: 400;
    color: {t["list_item"]};
    padding: 0px;
    margin: 0px;
    border-radius: 8px;
    min-height: 48px;
}}

QListWidget::item:hover:!selected {{
    background: {t["list_hover_bg"]};
    color: {t["list_hover_text"]};
}}

QListWidget::item:selected {{
    background: {t["list_selected_bg"]};
    color: {t["list_selected_text"]};
    font-weight: 600;
}}

QListWidget::item:focus {{
    outline: none;
}}

QWidget#toolContent {{
    background: transparent;
}}

QWidget#toolHeader {{
    background: {t["tool_header_bg"]};
}}

QFrame#headerDivider {{
    background: {t["divider"]};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

QLabel#toolHeaderTitle,
QLabel#toolTitle {{
    font-size: 18px;
    font-weight: 700;
    color: {t["text_1"]};
    letter-spacing: -0.3px;
    background: transparent;
}}

QLabel#toolHeaderDesc,
QLabel#toolDesc {{
    font-size: 12px;
    color: {t["header_desc"]};
    background: transparent;
}}

QLabel#optionLabel,
QLabel#optLabel {{
    color: {t["opt_label"]};
    font-size: 13px;
    background: transparent;
}}

QLabel#cropInfo {{
    font-size: 11px;
    color: {t["text_2"]};
    background: transparent;
}}

QFrame#optionDivider,
QFrame#divider {{
    background: {t["divider"]};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

QFrame#dropZone {{
    background: {t["drop_bg"]};
    border: 2px dashed {t["drop_zone_border"]};
    border-radius: 8px;
}}

QFrame#dropZone:hover {{
    border-color: {t["drop_hover_border"]};
    background: {t["drop_hover_bg"]};
}}

QWidget#dropIconFrame {{
    background: {t["drop_icon_bg"]};
    border-radius: 10px;
    min-width: 72px;
    max-width: 72px;
    min-height: 64px;
    max-height: 64px;
}}

QLabel#dropIcon {{
    background: transparent;
}}

QLabel#dropHint {{
    font-size: 16px;
    color: {t["text_2"]};
    background: transparent;
    padding: 0px;
    margin: 0px;
    min-height: 22px;
}}

QLabel#dropSubHint {{
    font-size: 13px;
    color: {t["text_3"]};
    background: transparent;
    padding: 0px;
    margin: 0px;
    min-height: 18px;
}}

QLabel#dropThumb {{
    border-radius: 8px;
    background: {t["card"]};
}}

QLabel#dropThumbMore {{
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    color: {t["text_2"]};
    background: {t["card"]};
}}

QLabel#dropFilename {{
    font-size: 13px;
    color: {t["text_1"]};
    background: transparent;
}}

QLabel#dropCount {{
    font-size: 13px;
    color: {t["text_2"]};
    background: transparent;
}}

QWidget#optionRow {{
    background: transparent;
}}

QLabel#infoNote {{
    color: {t["text_2"]};
    font-size: 12px;
    background: transparent;
    padding: 4px 0;
}}

QLineEdit, QSpinBox, QDoubleSpinBox {{
    background: {t["input_bg"]};
    border: 1px solid {t["input_border"]};
    border-radius: 6px;
    color: {t["input_text"]};
    font-size: 13px;
    min-height: 34px;
    max-height: 34px;
    padding: 6px 10px;
    selection-background-color: {t["selection_bg"]};
}}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border: 1px solid {t["accent"]};
    background: {t["input_focus_bg"]};
}}

QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    width: 0px;
    height: 0px;
    border: none;
}}

QComboBox {{
    background: {t["input_bg"]};
    border: 1px solid {t["input_border"]};
    border-radius: 6px;
    color: {t["input_text"]};
    min-height: 34px;
    max-height: 34px;
    padding: 6px 10px;
    font-size: 13px;
    selection-background-color: {t["selection_bg"]};
}}

QComboBox:focus {{
    border: 1px solid {t["accent"]};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 8px;
}}

QComboBox QAbstractItemView {{
    background: {t["combo_popup_bg"]};
    border: 1px solid {t["combo_popup_border"]};
    border-radius: 7px;
    selection-background-color: {t["selection_bg"]};
    color: {t["text_1"]};
    padding: 4px;
}}

QPushButton {{
    background: {t["btn_bg"]};
    border: 1px solid {t["btn_border"]};
    border-radius: 6px;
    color: {t["btn_text"]};
    font-size: 13px;
    min-height: 32px;
    max-height: 32px;
    padding: 6px 14px;
}}

QPushButton:hover {{
    background: {t["btn_hover_bg"]};
    border-color: {t["btn_hover_border"]};
    color: {t["btn_hover_text"]};
}}

QPushButton#convertBtn {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {BRAND["blue"]}, stop:1 {BRAND["purple"]});
    border: none;
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 600;
    border-radius: 8px;
    padding: 10px 28px;
    min-width: 100px;
    min-height: 38px;
    max-height: 38px;
}}

QPushButton#convertBtn:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {t["accent_hover"]}, stop:1 #6B20A8);
}}

QPushButton#primary {{
    background: {t["accent"]};
    border: none;
    color: #FFFFFF;
    font-size: 13px;
    font-weight: 600;
    border-radius: 8px;
    padding: 6px 18px;
    min-height: 32px;
    max-height: 32px;
}}

QPushButton#primary:hover {{
    background: {t["accent_hover"]};
}}

QPushButton#quickRotate {{
    background: transparent;
    border: 1px solid {t["quick_rotate_border"]};
    border-radius: 6px;
    color: {t["quick_rotate_text"]};
    font-size: 12px;
    min-height: 30px;
    padding: 4px 10px;
}}

QPushButton#quickRotate:hover {{
    background: {t["quick_rotate_hover_bg"]};
    border-color: {t["quick_rotate_hover_border"]};
    color: {t["quick_rotate_hover_text"]};
}}

QPushButton#quickRotate:checked {{
    background: {t["accent_tint"]};
    border-color: {t["accent"]};
    color: {t["quick_rotate_hover_text"]};
}}

QPushButton#fileBtn {{
    background: transparent;
    border: 1px solid {t["file_btn_border"]};
    border-radius: 6px;
    color: {t["file_btn_text"]};
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    padding: 6px 14px;
}}

QPushButton#fileBtn:hover {{
    border-color: {t["file_btn_hover_border"]};
    color: {t["file_btn_hover_text"]};
    background: {t["file_btn_hover_bg"]};
}}

QPushButton#outputBtn {{
    background: transparent;
    border: 1px solid {t["file_btn_border"]};
    border-radius: 8px;
    color: {t["file_btn_text"]};
    font-size: 14px;
    min-height: 38px;
    max-height: 38px;
    padding: 0 16px;
}}

QPushButton#outputBtn:hover {{
    border-color: {t["file_btn_hover_border"]};
    color: {t["file_btn_hover_text"]};
    background: {t["file_btn_hover_bg"]};
}}

QPushButton#outputGoBtn {{
    background: transparent;
    border: 1px solid {t["file_btn_border"]};
    border-radius: 8px;
    color: {t["file_btn_text"]};
    font-size: 14px;
    font-weight: 600;
    min-width: 38px;
    max-width: 38px;
    min-height: 38px;
    max-height: 38px;
    padding: 0;
}}

QPushButton#outputGoBtn:hover {{
    border-color: {t["file_btn_hover_border"]};
    color: {t["file_btn_hover_text"]};
    background: {t["file_btn_hover_bg"]};
}}

QLineEdit#outputInput {{
    min-height: 38px;
    max-height: 38px;
    font-size: 15px;
    border-radius: 8px;
    padding: 0 12px;
}}

QPushButton#deleteBtn {{
    background: transparent;
    border: 1px solid {t["delete_btn_border"]};
    border-radius: 6px;
    color: {t["delete_btn_text"]};
    font-size: 13px;
    min-height: 30px;
    max-height: 30px;
    padding: 6px 14px;
}}

QPushButton#deleteBtn:hover {{
    background: {t["delete_btn_hover_bg"]};
    border-color: {t["delete_btn_border"]};
    color: {t["delete_btn_text"]};
}}

QPushButton#themeBtn, QPushButton#langBtn {{
    background: {t["input_bg"]};
    border: 1px solid {t["theme_btn_border"]};
    border-radius: 8px;
    color: {t["theme_btn_text"]};
    min-width: 40px;
    max-width: 40px;
    min-height: 40px;
    max-height: 40px;
    text-align: center;
    padding: 0px;
}}

QPushButton#themeBtn {{
    font-size: 18px;
}}

QPushButton#langBtn {{
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.5px;
}}

QPushButton#themeBtn:hover, QPushButton#langBtn:hover {{
    background: {t["theme_btn_hover_bg"]};
    color: {t["theme_btn_hover_text"]};
}}

QSlider::groove:horizontal {{
    height: 3px;
    background: {t["slider_groove"]};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {t["accent"]};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: #FFFFFF;
    border: 2px solid {t["accent"]};
    border-radius: 7px;
    width: 14px;
    height: 14px;
    margin: -6px 0;
}}

QCheckBox {{
    color: {t["checkbox_text"]};
    font-size: 14px;
    spacing: 8px;
    background: transparent;
}}

QCheckBox::indicator {{
    width: 15px;
    height: 15px;
    border: 1.5px solid {t["checkbox_border"]};
    border-radius: 4px;
    background: {t["checkbox_bg"]};
}}

QCheckBox::indicator:checked {{
    background: {t["accent"]};
    border-color: {t["accent"]};
}}

QCheckBox#colorOptionCheckbox {{
    font-size: 14px;
    spacing: 8px;
}}

QCheckBox#colorOptionCheckbox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
    border: 2px solid {t["color_checkbox_border"]};
}}

QCheckBox#colorOptionCheckbox::indicator:checked {{
    background: {t["accent"]};
    border: 2px solid {t["accent"]};
}}

QWidget#outputBar {{
    background: {t["output_bar_bg"]};
    border-top: 1px solid {t["output_bar_border"]};
    padding: 0;
}}

QLabel#outputLabel {{
    color: {t["text_3"]};
    font-size: 14px;
    background: transparent;
}}

QLabel#previewLabel {{
    background: {t["preview_label_bg"]};
    border-radius: 10px;
    color: {t["preview_label_text"]};
    min-height: 200px;
}}

QLabel#resultPreview {{
    background: {t["surface"]};
    border: 1px solid {t["divider"]};
    border-radius: 8px;
    color: {t["text_3"]};
    min-height: 120px;
    padding: 8px;
}}

QWidget#progressPanel {{
    background: {t["output_bar_bg"]};
    border-top: 1px solid {t["divider"]};
    min-height: 36px;
    max-height: 36px;
}}

QLabel#progressLabel {{
    color: {t["text_2"]};
    font-size: 12px;
    background: transparent;
    min-width: 120px;
}}

QPushButton#cancelLink {{
    background: transparent;
    border: none;
    color: {t["text_3"]};
    font-size: 12px;
    min-height: 36px;
    max-height: 36px;
    padding: 0 4px;
    text-decoration: underline;
}}

QPushButton#cancelLink:hover {{
    color: {t["text_2"]};
}}

QWidget#logPanel {{
    background: {t["log_panel_bg"]};
    border-top: 1px solid {t["divider"]};
    min-height: 32px;
}}

QPushButton#logToggle, QPushButton#logClear {{
    background: transparent;
    border: none;
    color: {t["text_3"]};
    font-size: 12px;
    min-height: 32px;
    max-height: 32px;
    padding: 0 4px;
}}

QPushButton#logToggle:hover, QPushButton#logClear:hover {{
    color: {t["text_2"]};
}}

QLabel#logCount {{
    color: {t["text_2"]};
    font-size: 11px;
    background: transparent;
}}

QPlainTextEdit {{
    background: {t["window"]};
    border: none;
    color: {t["log_text"]};
    font-family: 'Consolas', monospace;
    font-size: 12px;
}}

QTableWidget {{
    background: transparent;
    border: none;
    gridline-color: transparent;
    font-size: 12px;
    color: {t["table_text"]};
}}

QTableWidget#bulkPreviewTable {{
    border: 1px solid {t["divider"]};
    border-radius: 8px;
}}

QHeaderView::section {{
    background: transparent;
    border: none;
    border-bottom: 1px solid {t["divider"]};
    color: {t["table_header"]};
    font-size: 11px;
    padding: 4px 8px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 4px;
}}

QScrollBar::handle:vertical {{
    background: {t["scrollbar_handle"]};
    border-radius: 2px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background: {t["scrollbar_handle_hover"]};
}}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 4px;
}}

QScrollBar::handle:horizontal {{
    background: {t["scrollbar_handle"]};
    border-radius: 2px;
    min-width: 20px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {t["scrollbar_handle_hover"]};
}}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {{
    width: 0;
}}

QStatusBar {{
    background: {t["output_bar_bg"]};
    color: {t["status_bar_text"]};
    font-size: 11px;
    border-top: 1px solid {t["divider"]};
}}

QLabel {{
    background: transparent;
    color: {t["text_1"]};
}}
""".strip()
