from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

from filters import hybrid_image, fourier_magnitude

root = Path(__file__).parent
starter = root / "cs180_proj2_hybrid_starter_code"

assets = root / "assets"
assets.mkdir(exist_ok=True)


def load_image(path):
    with Image.open(path) as photo:
        return np.asarray(ImageOps.exif_transpose(photo).convert("L"), dtype=float) / 255


def align_image(image, eyes):
    first, second = np.asarray(eyes, dtype=np.float32)
    direction = second - first
    third = first + np.array([-direction[1], direction[0]], dtype=np.float32)
    source = np.array([first, second, third], dtype=np.float32)
    target = np.array([[110, 160], [210, 160], [110, 260]], dtype=np.float32)
    transform = cv2.getAffineTransform(source, target)
    return cv2.warpAffine(image, transform, (320, 400), borderMode=cv2.BORDER_REFLECT)


def align_pair(first, second, points):
    return align_image(first, points[:2]), align_image(second, points[2:])


def show(ax, image, title, vmin=0, vmax=1):
    ax.imshow(image, cmap="gray", vmin=vmin, vmax=vmax)
    ax.set_title(title)
    ax.axis("off")


def save(fig, filename):
    fig.tight_layout()
    fig.savefig(assets / filename, dpi=140)


pairs = [
    ("derek_nutmeg", "Derek", "Nutmeg",
     starter / "DerekPicture.jpg", starter / "nutmeg.jpg",
     [(298, 345), (440, 331), (605, 292), (752, 368)], 10, 3),
    ("aaron_samoyed", "Aaron", "Samoyed",
     root / "inputs/self_portrait.jpg", root / "inputs/samoyed.jpg",
     [(596, 282), (693, 285), (299, 346), (403, 335)], 10, 3),
    ("portraits", "Far-camera portrait", "Close-camera portrait",
     root.parent / "proj0/assets/selfie_far_zoom.jpeg",
     root.parent / "proj0/assets/selfie_close.jpeg",
     [(543, 824), (887, 835), (406, 673), (797, 674)], 10, 3),
]


def main():
    for name, low_name, high_name, low_path, high_path, points, sigma_low, sigma_high in pairs:
        original_low, original_high = load_image(low_path), load_image(high_path)
        aligned_low, aligned_high = align_pair(original_low, original_high, points)
        low, high, hybrid = hybrid_image(aligned_low, aligned_high, sigma_low, sigma_high)
        display = np.clip(hybrid, 0, 1)
        Image.fromarray(np.rint(display * 255).astype(np.uint8)).save(assets / f"part22_{name}.png")

        fig, axes = plt.subplots(1, 3, figsize=(10, 4))
        show(axes[0], original_low, low_name + " (low source)")
        show(axes[1], original_high, high_name + " (high source)")
        show(axes[2], display, "Hybrid")
        save(fig, f"part22_{name}_inputs.png")

        if name == "derek_nutmeg":
            fig, axes = plt.subplots(2, 3, figsize=(10, 8))
            show(axes[0, 0], aligned_low, "Aligned Derek")
            show(axes[0, 1], aligned_high, "Aligned Nutmeg")
            show(axes[0, 2], display, "Hybrid")
            show(axes[1, 0], low, f"Low-pass: sigma = {sigma_low}")
            show(axes[1, 1], high, f"High-pass: sigma = {sigma_high}", -0.25, 0.25)
            show(axes[1, 2], cv2.resize(display, (40, 50), interpolation=cv2.INTER_AREA),
                 "Reduced to 40 x 50 pixels")
            save(fig, "part22_process.png")

            images = [aligned_low, aligned_high, low, high, hybrid]
            titles = ["Aligned Derek", "Aligned Nutmeg", "Low-pass Derek", "High-pass Nutmeg", "Hybrid"]
            spectra = [fourier_magnitude(im) for im in images]
            fig, axes = plt.subplots(1, 5, figsize=(14, 3.5))
            maximum = max(spectrum.max() for spectrum in spectra)
            for ax, spectrum, title in zip(axes, spectra, titles):
                show(ax, spectrum, title, 0, maximum)
            save(fig, "part22_fourier.png")
        print(f"{name}: sigma_low={sigma_low}, sigma_high={sigma_high}", flush=True)
    plt.show()


if __name__ == "__main__":
    main()
