"""Entry point for the news-image-20261118 submission.

The cover picture itself is produced ahead of time by make_cover.py and
ships in this repository as news_image.png.  All this program has to do
is place a copy of that picture where the grader expects it:
``/output/entry.png``.  It uses nothing beyond the standard library and
never touches the network.
"""

import shutil
from pathlib import Path

PICTURE_NAME = "news_image.png"
DESTINATION = Path("/output/entry.png")


def source_picture() -> Path:
    """Locate the bundled cover next to this file, wherever we run from."""
    return Path(__file__).resolve().parent / PICTURE_NAME


def deliver() -> Path:
    src = source_picture()
    if not src.is_file():
        raise FileNotFoundError(f"bundled cover image not found: {src}")
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, DESTINATION)
    return DESTINATION


if __name__ == "__main__":
    written = deliver()
    print(f"entry image written to {written}")
