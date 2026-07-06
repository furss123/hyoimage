# HyoImage — Development Context

Last updated: 2026-06-28

## Repositories

| Repo | URL | Purpose |
|------|-----|---------|
| **hyoimage** | https://github.com/furss123/hyoimage | Application source, releases |
| **hyot-software-center** | https://github.com/furss123/hyot-software-center | Software catalog site (`data/software/*/`) |

## Product

- **Name:** HyoImage v1.0.0
- **Platform:** Windows 10 22H2+ x64
- **Stack:** Python 3.11, PyQt6, Pillow, rembg, opencv-python-headless, pytesseract, numpy
- **12 tools:** compress, resize, convert, crop, bg_remove, rotate, watermark, merge, color_adjust, ocr, ai_upscale, bulk_rename

## Project Layout

```
HyoT Image Tools/
├── main.py                 # QApplication entry
├── app/
│   ├── constants.py        # paths, TOOL_IDS
│   ├── settings.py         # JSON settings in %APPDATA%\HyoT\ImageTools
│   ├── ui/                 # main_window, sidebar, drop_zone, output_bar, progress/log panels, theme
│   │   └── tools/          # *ToolWidget per tool (12)
│   ├── core/               # worker, job (stubs), tools/*.py processors
│   ├── models/             # FileItem, ProcessResult, *Options dataclasses
│   └── utils/              # image, file, exif, i18n, dep_check (stub)
├── assets/i18n/            # ko.json, en.json
├── assets/icons/           # tool SVGs (optional), app.ico (optional)
├── third_party/realesrgan/ # realesrgan-ncnn-vulkan.exe + models/
├── build.spec              # PyInstaller onedir, windowed
├── scripts/build.py
├── installer/setup.iss     # Inno Setup x64
└── .github/workflows/release.yml  # tag v* → build + release
```

## Implemented vs Stub

### Done
- Project scaffold, constants, settings, i18n, theme
- UI shell: MainWindow, Sidebar, DropZone, OutputBar, ProgressPanel, LogPanel
- Theme/language switching wired
- Core + UI: **compress, resize, convert, crop, bg_remove, rotate, ocr, ai_upscale**
- Models: FileItem (basic), ProcessResult, partial tool_options
- Build: build.spec, scripts/build.py, installer, GitHub Actions release workflow
- Software Center catalog JSON in `data/software/hyoimage/` (lives in **hyot-software-center** repo)

### Still stub (`pass` only)
- `app/core/worker.py`, `app/core/job.py` — batch job runner not wired to UI Run button
- `app/core/tools/`: watermark, merge, color_adjust, bulk_rename
- `app/ui/tools/`: watermark, merge, color_adjust, bulk_rename
- `app/utils/dep_check.py`
- Tool widgets are not embedded in MainWindow stack with DropZone/OutputBar per tool (stack shows tool options only)

## Conventions

- Tool widget class: `{Name}ToolWidget` in `app/ui/tools/{tool_id}.py` (e.g. `CompressToolWidget`)
- Core processor: `process(file, options, output_dir, overwrite, suffix) -> ProcessResult` in `app/core/tools/{tool_id}.py`
- Options dataclass: `{Tool}Options` in `app/models/tool_options.py`
- i18n: `tr("key")` with keys in `assets/i18n/ko.json` and `en.json`
- Output paths: `app/utils/file.resolve_output()`
- Images: `app/utils/image.open_image()`, `save_image()`

## Settings ( `%APPDATA%\HyoT\ImageTools\settings.json` )

```json
{
  "theme": "dark",
  "language": "ko",
  "last_output_dir": "",
  "overwrite": false,
  "suffix": "_processed",
  "last_tool": "compress"
}
```

## Third-party: Real-ESRGAN

- Binary: `third_party/realesrgan/realesrgan-ncnn-vulkan.exe`
- Models: `third_party/realesrgan/models/` (ncnn `.param`/`.bin`)
- CLI model names: `realesrgan-x4plus`, `realesrgan-x4plus-anime` (not PyTorch `.pth` names)
- Source: [Real-ESRGAN v0.2.5.0 windows zip](https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip)

## Build & Release

```powershell
pip install -r requirements.txt pyinstaller
python scripts/build.py
# Output: dist/HyoImage/

# Installer (Inno Setup 6)
iscc installer\setup.iss
# Output: dist/HyoImage-1.0.0-x64-setup.exe
```

**CI:** push tag `v*` → `.github/workflows/release.yml` builds setup + portable zip + sha256.txt → GitHub Release.

## Software Center Catalog

Copy to `hyot-software-center/data/software/hyoimage/`:
- `meta.json` — app metadata
- `releases.json` — version assets (setup, portable, sha256 URLs)

## Next Development Priorities

1. **Wire worker/job** — connect OutputBar `run_requested` to batch processing with progress/log updates
2. **Integrate DropZone + tool layout** — each tool page should include file list + options + run flow
3. **Implement remaining tools:** watermark, merge, color_adjust, bulk_rename (core + ui)
4. **Complete models** — align `FileItem`, `ProcessResult`, `tool_options` with full spec if not done
5. **dep_check** — Tesseract path detection, rembg model notice
6. **Icons** — `assets/icons/{tool_id}.svg`, `app.ico` for installer
7. **Update `ProcessResult`** usage if migrating to `input_path`/`error`/`duration_ms` schema

## Run Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

**External deps (user-installed):** Tesseract OCR (for OCR tool).

## Git

```powershell
git tag v1.0.0
git push origin main --tags
```

Release assets:
- `HyoImage-1.0.0-x64-setup.exe`
- `HyoImage-1.0.0-x64-portable.zip`
- `sha256.txt`
