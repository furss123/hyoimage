from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from app.constants import APP_VERSION

MANIFEST_URL = "https://hyot.dev/updates/hyoimage.json"
_HTTP_TIMEOUT_SECONDS = 20
_DOWNLOAD_TIMEOUT_SECONDS = 90


def prepare_update() -> dict[str, str] | None:
    try:
        with urllib.request.urlopen(MANIFEST_URL, timeout=_HTTP_TIMEOUT_SECONDS) as res:
            manifest = json.loads(res.read().decode("utf-8"))
        latest = manifest.get("latest", {}).get("stable")
        if not isinstance(latest, str):
            return None
        if _version_tuple(latest) <= _version_tuple(APP_VERSION):
            return None
        release = next(
            (item for item in manifest.get("releases", []) if item.get("version") == latest),
            None,
        )
        asset = release.get("primaryAsset") if release else None
        if not _is_valid_asset(asset):
            return None

        update_dir = Path(tempfile.gettempdir()) / "HyoT" / "hyoimage-updates"
        update_dir.mkdir(parents=True, exist_ok=True)
        path = update_dir / asset["filename"]
        partial_path = path.with_suffix(f"{path.suffix}.part")

        with urllib.request.urlopen(asset["url"], timeout=_DOWNLOAD_TIMEOUT_SECONDS) as res:
            data = res.read()
        digest = hashlib.sha256(data).hexdigest()
        if asset.get("sha256") and digest != asset["sha256"].lower():
            return None
        if asset.get("size") and len(data) != int(asset["size"]):
            return None
        partial_path.write_bytes(data)
        partial_path.replace(path)
        return {"version": latest, "path": str(path)}
    except Exception:
        return None


def install_ready_update(path: str) -> None:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".msi":
        subprocess.Popen(["msiexec", "/i", path, "/quiet", "/norestart"])
    elif ext == ".exe":
        subprocess.Popen([path, "/S", "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART", "/SP-"])
    else:
        subprocess.Popen(["explorer", path])


def _version_tuple(value: str) -> tuple[int, int, int]:
    clean = value.strip().lstrip("v").split("-", 1)[0]
    parts = [int(part) for part in clean.split(".") if part.isdigit()]
    return tuple((parts + [0, 0, 0])[:3])


def _is_valid_asset(asset: Any) -> bool:
    return (
        isinstance(asset, dict)
        and isinstance(asset.get("filename"), str)
        and isinstance(asset.get("url"), str)
    )
