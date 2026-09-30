from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from convolutions import finite_difference_edges


with Image.open(Path(__file__).parent / "inputs/cameraman.png") as photo:
    image = np.asarray(photo.convert("L"), dtype=float) / 255

# Change these values and rerun to compare thresholds.
thresholds = [0.15, 0.18, 0.21, 0.24]

fig, axes = plt.subplots(2, 3, figsize=(12, 8))
axes = axes.ravel()
axes[0].imshow(image, cmap="gray", vmin=0, vmax=1)
axes[0].set_title("Original")

for ax, threshold in zip(axes[2:], thresholds):
    gx, gy, magnitude, edges = finite_difference_edges(image, threshold)
    ax.imshow(edges, cmap="gray", vmin=0, vmax=1)
    ax.set_title(f"Threshold = {threshold}")

axes[1].imshow(magnitude, cmap="gray", vmin=0)
axes[1].set_title("Gradient magnitude")
for ax in axes:
    ax.axis("off")

plt.tight_layout()
plt.show()
