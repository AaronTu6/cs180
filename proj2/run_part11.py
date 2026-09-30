"""Run with: python proj2/run_part11.py (requires NumPy, SciPy, Pillow)."""

from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image, ImageOps
from scipy.signal import convolve2d

from convolutions import convolve_four_loops, convolve_two_loops

ROOT = Path(__file__).resolve().parent


def scipy_same(image, kernel):
    return convolve2d(image, kernel, mode="same", boundary="fill", fillvalue=0)


def save_image(path, values):
    pixels = np.rint(np.clip(values, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(pixels).save(path)


def main():
    with Image.open(ROOT / "inputs/self_portrait.jpg") as photo:
        image = np.asarray(ImageOps.exif_transpose(photo).convert("L"), dtype=float) / 255
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    save_image(assets / "grayscale.png", image)

    filters = {
        "box": np.ones((9, 9)) / 81,
        "dx": np.array([[1, 0, -1]]),
        "dy": np.array([[1], [0], [-1]]),
    }
    methods = {
        "four": convolve_four_loops,
        "two": convolve_two_loops,
        "scipy": scipy_same,
    }

    print("Filter  Method  Median seconds  Max error vs SciPy", flush=True)
    for name, kernel in filters.items():
        reference = scipy_same(image, kernel)
        for method_name, method in methods.items():
            times = []
            for _ in range(3):
                start = perf_counter()
                output = method(image, kernel)
                times.append(perf_counter() - start)
                np.testing.assert_allclose(output, reference, rtol=0, atol=1e-12)

            error = np.max(np.abs(output - reference))
            print(f"{name:6}  {method_name:6}  {np.median(times):.6f}        {error:.2e}", flush=True)

            # Save our two-loop results; all methods agree within 1e-12.
            if method_name == "two":
                # Derivatives: map [-0.25, 0.25] to [0, 1], with zero at gray.
                display = output if name == "box" else 0.5 + output / 0.5
                save_image(assets / f"{name}_two.png", display)


if __name__ == "__main__":
    main()
