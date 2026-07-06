import os
from pathlib import Path

APP_NAME = "HyoImage"
APP_VERSION = "1.0.1"

APPDATA_DIR = Path(os.getenv("APPDATA")) / "HyoT" / "ImageTools"
SETTINGS_FILE = APPDATA_DIR / "settings.json"

ASSETS_DIR = Path(__file__).parent.parent / "assets"
I18N_DIR = ASSETS_DIR / "i18n"
THIRD_PARTY_DIR = Path(__file__).parent.parent / "third_party"

TOOL_IDS = [
    "resize",
    "compress",
    "convert",
    "rotate",
    "crop",
    "merge",
    "bulk_rename",
]
