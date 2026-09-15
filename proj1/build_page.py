"""Build the static project report from the measured batch results."""

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_page():
    results = json.loads((ROOT / "results.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    reviews = json.loads((ROOT / "reviews.json").read_text(encoding="utf-8"))
    environment = json.loads((ROOT / "environment.json").read_text(encoding="utf-8"))
    lookup = {(r["filename"], r["method"], r["metric"]): r for r in results}
    supplied = sorted({r["filename"] for r in results if r["group"] == "provided"})
    extra = [s["filename"] for s in sources]
    assert len(supplied) == 14 and len(extra) == 3
    for filename in supplied + extra:
        for metric in ("l2", "ncc"):
            assert (filename, "pyramid", metric) in lookup, f"Missing {filename} / {metric}"
    titles = {s["filename"]: s["title"] for s in sources}
    titles["religous_painting.tif"] = "Religious painting"

    def title(filename):
        return titles.get(filename, Path(filename).stem.replace("_", " ").capitalize())

    def offsets(record):
        return (f'G ({record["green_dx"]}, {record["green_dy"]}) · '
                f'R ({record["red_dx"]}, {record["red_dy"]}) · {record["seconds"]:.2f} s')

    def card(filename, method):
        row = lookup[filename, method, "ncc"]
        note = reviews[filename]["ncc"]
        return f'''<article class="result-card" data-filename="{filename}" data-method="{method}">
          <a class="result-link" href="{row['output']}" aria-label="Open full-resolution {html.escape(title(filename))}">
            <img class="result-image" src="{row['preview']}" alt="{html.escape(title(filename))}, aligned with {method} NCC"
                 width="{row['width']}" height="{row['height']}" loading="lazy" decoding="async">
          </a>
          <div class="card-body"><h3>{html.escape(title(filename))}</h3>
            <p class="result-offsets">{offsets(row)}</p>
            <p class="result-note">{html.escape(note)}</p>
          </div></article>'''

    def controls(section):
        return f'''<div class="view-controls" role="group" aria-label="Image comparison for {section}">
          <button type="button" data-view="ncc" aria-pressed="true">NCC alignment</button>
          <button type="button" data-view="l2" aria-pressed="false">L2 alignment</button>
          <button type="button" data-view="unaligned" aria-pressed="false">Before alignment</button>
        </div><p class="view-hint">Switch views to compare. Click an aligned image for the full-resolution JPEG.</p>'''

    def table(method, filenames, metric):
        rows = []
        for filename in filenames:
            r = lookup[filename, method, metric]
            rows.append(f'''<tr><th scope="row"><a href="{r['output']}">{html.escape(title(filename))}</a></th>
            <td>{r['width']} × {r['height']}</td><td>({r['green_dx']}, {r['green_dy']})</td>
            <td>({r['red_dx']}, {r['red_dy']})</td><td>{r['seconds']:.2f}</td></tr>''')
        return f'''<div class="table-scroll" tabindex="0" role="region" aria-label="{method} {metric.upper()} measurements">
          <table><caption>{method.capitalize()} · {metric.upper()} · applied offsets in (x, y) pixels</caption>
          <thead><tr><th scope="col">Image</th><th scope="col">Output dimensions</th>
          <th scope="col">Green → blue</th><th scope="col">Red → blue</th><th scope="col">Seconds</th></tr></thead>
          <tbody>{''.join(rows)}</tbody></table></div>'''

    source_list = ''.join(f'''<li><a href="{s['item_url']}">{html.escape(s['title'])}</a>:
      {html.escape(s['description'])} <span class="source-id">{s['negative_id']}</span>.
      <a href="{s['download_url']}">Original stacked TIFF</a>.</li>''' for s in sources)
    ncc_pyramid = [r for r in results if r["method"] == "pyramid" and r["metric"] == "ncc"]
    replacements = {
        "SINGLE_CONTROLS": controls("single-scale results"),
        "SINGLE_CARDS": ''.join(card(f, "single") for f in supplied if f.endswith(".jpg")),
        "PROVIDED_CONTROLS": controls("provided plates"),
        "PROVIDED_CARDS": ''.join(card(f, "pyramid") for f in supplied),
        "EXTRA_CONTROLS": controls("additional plates"),
        "EXTRA_CARDS": ''.join(card(f, "pyramid") for f in extra),
        "SINGLE_TABLES": ''.join(table("single", [f for f in supplied if f.endswith(".jpg")], m) for m in ("ncc", "l2")),
        "NCC_TABLE": table("pyramid", supplied + extra, "ncc"),
        "L2_TABLE": table("pyramid", supplied + extra, "l2"),
        "SOURCES": source_list,
        "RUN_COUNT": str(len(results)),
        "MAX_TIME": f'{max(r["seconds"] for r in ncc_pyramid):.1f}',
        "TOTAL_TIME": f'{sum(r["seconds"] for r in results):.1f}',
        "ENVIRONMENT": html.escape(f'Python {environment["python"]}, NumPy {environment["numpy"]}, '
                                   f'scikit-image {environment["scikit_image"]}; {environment["processor"]}.'),
        "DATA": json.dumps({"results": results, "reviews": reviews}).replace("<", "\\u003c")
    }
    page = (ROOT / "page_template.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        page = page.replace(f"@@{key}@@", value)
    assert "@@" not in page, "Unfilled page placeholder"
    (ROOT / "index.html").write_text(page, encoding="utf-8")
    print(f"Built index.html from {len(results)} measured runs")


if __name__ == "__main__":
    build_page()
