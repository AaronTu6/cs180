"""Evaluate all supplied and extra plates, saving images, offsets, and timings."""

import argparse
import csv
import json
import platform
from time import perf_counter

import numpy as np
import skimage
from PIL import Image

from code import ROOT, DATA_DIR, colorize, load_channels


def save_preview(rgb, path, max_size=1000):
    image = Image.fromarray(skimage.img_as_ubyte(np.clip(rgb, 0, 1)))
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    image.save(path, quality=85)


def run_batch(metrics, groups):
    output = ROOT / "outputs"
    previews = ROOT / "assets"
    output.mkdir(exist_ok=True)
    previews.mkdir(exist_ok=True)
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    supplied = sorted(p for p in DATA_DIR.iterdir() if p.suffix.lower() in {".jpg", ".tif"})
    extra = [ROOT / "extra_data" / s["filename"] for s in sources]
    jobs = []
    if "single" in groups:
        jobs += [(p, "provided", "single") for p in supplied if p.suffix.lower() == ".jpg"]
    if "provided" in groups:
        jobs += [(p, "provided", "pyramid") for p in supplied]
    if "extra" in groups:
        jobs += [(p, "extra", "pyramid") for p in extra]

    # Preserve other completed groups when rerunning a subset.
    results_path = ROOT / "results.json"
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else []
    for path, group, method in jobs:
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}; run download_extra.py for LoC inputs")
        blue, green, red = load_channels(path)
        baseline = np.dstack([red, green, blue])
        save_preview(baseline, previews / f"{path.stem}_unaligned.jpg")
        del blue, green, red, baseline
        for metric in metrics:
            print(f"{path.name} / {method} / {metric}", flush=True)
            start = perf_counter()
            rgb, offsets = colorize(path, method=method, metric=metric)
            seconds = perf_counter() - start  # Reading, alignment, and RGB assembly; excludes export.
            name = f"{path.stem}_{method}_{metric}.jpg"
            Image.fromarray(skimage.img_as_ubyte(np.clip(rgb, 0, 1))).save(output / name, quality=85)
            save_preview(rgb, previews / name)
            record = {
                "filename": path.name, "group": group, "method": method, "metric": metric,
                "width": rgb.shape[1], "height": rgb.shape[0],
                "green_dx": int(offsets["green"][1]), "green_dy": int(offsets["green"][0]),
                "red_dx": int(offsets["red"][1]), "red_dy": int(offsets["red"][0]),
                "seconds": round(seconds, 3), "output": f"outputs/{name}", "preview": f"assets/{name}"
            }
            results = [r for r in results if (r["filename"], r["method"], r["metric"]) != (path.name, method, metric)]
            results.append(record)
            results.sort(key=lambda r: (r["method"], r["group"], r["filename"], r["metric"]))
            results_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
            with (ROOT / "results.csv").open("w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=list(record))
                writer.writeheader()
                writer.writerows(results)
            print(f'  G (x,y) = ({record["green_dx"]}, {record["green_dy"]}); '
                  f'R (x,y) = ({record["red_dx"]}, {record["red_dy"]}); {seconds:.2f}s', flush=True)
            del rgb
    environment = {
        "python": platform.python_version(), "numpy": np.__version__,
        "scikit_image": skimage.__version__, "platform": platform.platform(),
        "processor": platform.processor(), "timing": "Read + align + RGB assembly; JPEG export excluded",
        "parameters": {"coarse_radius": 15, "refinement_radius": 2, "coarse_max_dimension": 400,
                       "border_fraction": 0.1, "pyramid_scale": 0.5, "anti_aliasing": True,
                       "channel_alignment": "green to blue; red to green; compose red offset relative to blue"}
    }
    (ROOT / "environment.json").write_text(json.dumps(environment, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(results)} measurements to results.csv and results.json", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", nargs="+", choices=["l2", "ncc"], default=["l2", "ncc"])
    parser.add_argument("--groups", nargs="+", choices=["single", "provided", "extra"],
                        default=["single", "provided", "extra"])
    args = parser.parse_args()
    run_batch(args.metrics, args.groups)
