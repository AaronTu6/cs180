"""Download three full-resolution, stacked grayscale negatives from the LoC."""

import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent


def download_extra():
    folder = ROOT / "extra_data"
    folder.mkdir(exist_ok=True)
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    for source in sources:
        path = folder / source["filename"]
        if not path.exists():
            print(f'Downloading {source["title"]}...', flush=True)
            temporary = path.with_suffix(".part")
            request = Request(source["download_url"], headers={"User-Agent": "Mozilla/5.0"})
            with urlopen(request, timeout=120) as response:
                with temporary.open("wb") as output:
                    while chunk := response.read(1024 * 1024):
                        output.write(chunk)
            temporary.replace(path)
        source["bytes"] = path.stat().st_size
        with path.open("rb") as image:
            source["sha256"] = hashlib.file_digest(image, "sha256").hexdigest()
        print(f'{path.name}: {source["bytes"]:,} bytes', flush=True)
    (ROOT / "sources.json").write_text(json.dumps(sources, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    download_extra()
