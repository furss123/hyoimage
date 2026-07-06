import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
BUILD = ROOT / "build"
OUTPUT = DIST / "HyoImage"


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def main() -> None:
    for directory in (DIST, BUILD):
        if directory.exists():
            shutil.rmtree(directory)

    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "build.spec"],
        cwd=ROOT,
        check=True,
    )

    print(f"Output path: {OUTPUT}/")

    if not OUTPUT.exists():
        print("Build finished, but output directory was not found.")
        return

    files = [path for path in OUTPUT.rglob("*") if path.is_file()]
    total_size = sum(path.stat().st_size for path in files)
    print(f"File count: {len(files)}")
    print(f"Total size: {_format_size(total_size)}")


if __name__ == "__main__":
    main()
