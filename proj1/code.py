from pathlib import Path

import numpy as np
import skimage as sk
import skimage.io as skio
from skimage.transform import rescale

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "CS180_fa2026_proj1_data"


def load_channels(path):
    """Read a stacked plate as floats in [0, 1]; return blue, green, red."""
    image = sk.img_as_float32(skio.imread(path))
    height = image.shape[0] // 3
    return image[:height], image[height:2 * height], image[2 * height:3 * height]


def crop_interior(image, fraction=0.1):
    """Return the center, removing fraction of each dimension from each side."""
    height, width = image.shape[:2]
    row_margin = int(height * fraction)
    col_margin = int(width * fraction)
    return image[row_margin:height - row_margin,
                 col_margin:width - col_margin]


def l2_score(a, b):
    """L2 distance between equally shaped float images; smaller is better."""
    difference = a - b
    return np.sqrt(np.sum(difference ** 2))


def ncc_score(a, b):
    """Mean-subtracted normalized correlation; larger is better."""
    a = a - np.mean(a)
    b = b - np.mean(b)
    denominator = np.sqrt(np.sum(a ** 2)) * np.sqrt(np.sum(b ** 2))
    if denominator == 0:
        return -np.inf  # Constant images cannot provide a useful match.
    return np.sum(a * b) / denominator


def shift_image(image, offset):
    """Apply (dy, dx): positive dy moves down; positive dx moves right."""
    return np.roll(image, shift=offset, axis=(0, 1))


def align_single(moving, reference, radius=15, center=(0, 0), metric="l2"):
    """Return the best total (dy, dx) to apply to moving, near center."""
    score_function = {"l2": l2_score, "ncc": ncc_score}[metric]
    center_y, center_x = center
    height, width = reference.shape

    # Ignore 10% borders plus enough space for every candidate shift.
    row_margin = int(height * 0.1) + abs(center_y) + radius
    col_margin = int(width * 0.1) + abs(center_x) + radius
    if 2 * row_margin >= height or 2 * col_margin >= width:
        raise ValueError("Search window leaves no interior pixels to compare")
    interior = (slice(row_margin, height - row_margin),
                slice(col_margin, width - col_margin))
    reference_crop = reference[interior]

    best_score = np.inf
    best_offset = None
    for dy in range(center_y - radius, center_y + radius + 1):
        for dx in range(center_x - radius, center_x + radius + 1):
            shifted = shift_image(moving, (dy, dx))
            score = score_function(shifted[interior], reference_crop)
            if metric == "ncc":
                score = -score
            if score < best_score:
                best_score = score
                best_offset = (dy, dx)
    if best_offset is None:
        raise ValueError("No valid alignment score; check for constant images")
    return best_offset


def align_pyramid(moving, reference, metric="l2"):
    """Return a full-resolution (dy, dx) using coarse-to-fine alignment."""
    if max(reference.shape) <= 400:
        return align_single(moving, reference, metric=metric)

    small_moving = rescale(moving, 0.5, anti_aliasing=True)
    small_reference = rescale(reference, 0.5, anti_aliasing=True)
    dy, dx = align_pyramid(small_moving, small_reference, metric=metric)

    return align_single(moving, reference, radius=2,
                        center=(2 * dy, 2 * dx), metric=metric)


def colorize(path, method="unaligned", metric="l2"):
    """Return an RGB image and the applied green/red offsets in (dy, dx)."""
    blue, green, red = load_channels(path)
    if method == "unaligned":
        green_offset = red_offset = (0, 0)
    else:
        align = {"single": align_single, "pyramid": align_pyramid}[method]
        green_offset = align(green, blue, metric=metric)
        red_offset = align(red, blue, metric=metric)
    rgb = np.dstack([shift_image(red, red_offset),
                     shift_image(green, green_offset), blue])
    return rgb, {"green": green_offset, "red": red_offset}


if __name__ == "__main__":
    filename = "cathedral.jpg"
    method = "single"  # Use "pyramid" for TIFFs, "unaligned" for a baseline.
    metric = "l2"  # Later try "ncc".

    rgb, offsets = colorize(DATA_DIR / filename, method, metric)
    for channel, (dy, dx) in offsets.items():
        print(f"{channel} displacement (x, y): ({dx}, {dy})")

    output_dir = ROOT / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{Path(filename).stem}_{method}_{metric}.jpg"
    skio.imsave(output_path, sk.img_as_ubyte(np.clip(rgb, 0, 1)))
    print(f"Saved {method} result: {output_path}")
