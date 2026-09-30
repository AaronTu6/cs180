from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

from filters import blur_image, sharpen_image


root = Path(__file__).parent
assets = root / "assets"
assets.mkdir(exist_ok=True)
kernel_size = 9
sigma = 1.5
amounts = [0.5, 1.5, 3.0]


def load_image(filename):
    with Image.open(root / "inputs" / filename) as photo:
        photo = ImageOps.exif_transpose(photo).convert("RGB")
        photo.thumbnail((600, 600), Image.Resampling.LANCZOS)
        return np.asarray(photo, dtype=float) / 255


def show(ax, image, title):
    ax.imshow(np.clip(image, 0, 1))
    ax.set_title(title)
    ax.axis("off")


def sharpening_comparison(image, name):
    blurred = blur_image(image, kernel_size, sigma)
    detail = image - blurred
    sharpened = [sharpen_image(image, alpha, kernel_size, sigma) for alpha in amounts]

    fig, axes = plt.subplots(2, 3, figsize=(10, 8))
    show(axes[0, 0], image, "Input")
    show(axes[0, 1], blurred, "Gaussian low-pass")
    show(axes[0, 2], 0.5 + 3 * detail, "High frequencies (3x, gray = zero)")
    for ax, alpha, result in zip(axes[1], amounts, sharpened):
        show(ax, result, f"Sharpened: alpha = {alpha}")
    fig.tight_layout()
    fig.savefig(assets / f"part21_{name}.png", dpi=140)
    return sharpened[1]


taj = load_image("taj.jpg")
samoyed = load_image("samoyed.jpg")
samoyed_blurry = blur_image(samoyed, kernel_size=13, sigma=2.0)
Image.fromarray(np.rint(samoyed_blurry * 255).astype(np.uint8)).save(
    root / "inputs/samoyed_blurry.png"
)

sharpening_comparison(taj, "taj")
samoyed_recovered = sharpening_comparison(samoyed_blurry, "samoyed")

fig, axes = plt.subplots(1, 3, figsize=(10, 5))
show(axes[0], samoyed, "Original before added blur")
show(axes[1], samoyed_blurry, "Blurred: sigma = 2")
show(axes[2], samoyed_recovered, "Resharpened: alpha = 1.5")
fig.tight_layout()
fig.savefig(assets / "part21_recovery.png", dpi=140)

print("Saved Part 2.1 figures and inputs/samoyed_blurry.png.")
plt.show()
