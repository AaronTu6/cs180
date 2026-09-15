# Project 1: Images of the Russian Empire

[Project webpage](https://aarontu6.github.io/cs180/proj1/) ·
[Assignment](https://cal-cs180.github.io/fa26/hw/proj1/index.html)

## Run

From the repository root, using Python 3.11 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r proj1/requirements.txt
.\.venv\Scripts\python.exe proj1/download_extra.py
.\.venv\Scripts\python.exe proj1/batch.py
.\.venv\Scripts\python.exe proj1/build_page.py
```

Place the assignment's 14 images in `proj1/CS180_fa2026_proj1_data/` before
running the batch. The three additional LoC negatives are downloaded into
`proj1/extra_data/`. Both raw-data directories are ignored by Git.

The default batch performs 40 runs: single-scale L2 and NCC on three JPEGs,
plus pyramid L2 and NCC on all 17 plates. It saves full-size reconstructed
JPEGs in `outputs/`, web previews in `assets/`, and measurements in
`results.csv` and `results.json`. Times include reading, alignment, and RGB
assembly, excluding image export. Offsets in the results are the applied
`(x, y)` shifts relative to blue; the code internally uses `(dy, dx)`.
Green is matched to blue, red is matched to green, and those offsets are
added to express the red displacement relative to blue.

To run a subset:

```powershell
.\.venv\Scripts\python.exe proj1/batch.py --groups provided --metrics ncc
```

Available groups: `single`, `provided`, `extra`. Other completed groups and
metrics are retained in the result files. Rerun `build_page.py` to refresh
the report after changing results, and update `reviews.json` after visually
inspecting new outputs. The current report's experiment discussion describes
the checked-in runs and should be revisited if alignment parameters change.

For one image, edit the three settings in the main block of `code.py` and run it.

## Files

- `code.py`: splitting, L2/NCC, shifting, single-scale and pyramid alignment.
- `batch.py`: reproducible evaluation and image export.
- `download_extra.py`, `sources.json`: LoC downloads, attribution, and checksums.
- `results.csv`, `results.json`, `environment.json`: measured results and run environment.
- `reviews.json`: qualitative visual inspection notes, separate from measurements.
- `build_page.py`, `page_template.html`, `style.css`, `gallery.js`: static report generation.
- `index.html`: generated report, ready for GitHub Pages.

## Results and limitations

Matching red through green fixes the conspicuous Emir failure seen with the
previous direct red-to-blue NCC match. The page includes native-resolution
face details before and after the change. It also fixes the previous L2
failure on Church. Colored borders, casts, and small local fringes remain;
visual inspection should not be interpreted as a perfect-alignment score.
No ground-truth offsets
were available, and no automatic cropping, contrast adjustment, white balance,
or edge-feature extension is claimed. Full resolution is preserved for alignment
and the output JPEG dimensions; only the web previews are resized.

Synthetic checks covered known shifts, a nonzero search center, NCC brightness
invariance, multi-level alignment with odd input dimensions, and composition
of the red-to-green and green-to-blue offsets into an exactly reconstructed
synthetic RGB image.

## Submission

The webpage contains the required image galleries, explanations, offsets,
runtime measurements, three additional plates, and failure discussion.
Include the webpage URL in the Gradescope submission and submit it to the
class gallery as specified by the assignment. Submit code without image files
to Gradescope; GitHub Pages serves the images separately.
