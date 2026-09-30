"""Show Parts 1.2/1.3 and save their figures for the webpage."""

from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from convolutions import finite_difference_edges, derivative_of_gaussian_edges


root = Path(__file__).parent
assets = root / "assets"
assets.mkdir(exist_ok=True)
with Image.open(root / "inputs/cameraman.png") as photo:
    image = np.asarray(photo.convert("L"), dtype=float) / 255

# Change these values to experiment. The HTML captions are edited manually.
raw_threshold = 0.21
smooth_threshold = 0.08
kernel_size = 9
sigma = 1.5

gx, gy, raw_magnitude, raw_edges = finite_difference_edges(image, raw_threshold)
blurred, magnitude, edges, dog_x, dog_y, dog_magnitude = derivative_of_gaussian_edges(
    image, smooth_threshold, kernel_size, sigma
)
g = cv2.getGaussianKernel(kernel_size, sigma)
gaussian = g @ g.T

# Verify the two methods before converting anything to display images.
same_magnitude = np.allclose(
    magnitude[1:-1, 1:-1], dog_magnitude[1:-1, 1:-1], rtol=0, atol=1e-12
)
print(f"Gradient magnitudes match (excluding border): {same_magnitude}")
assert same_magnitude


def show(ax, values, title, vmin=0, vmax=1):
    ax.imshow(values, cmap="gray", vmin=vmin, vmax=vmax, interpolation="nearest")
    ax.set_title(title)
    ax.axis("off")


def save(fig, filename):
    fig.tight_layout()
    fig.savefig(assets / filename, dpi=120)


# Part 1.2: the four required outputs.
fig, axes = plt.subplots(2, 2, figsize=(9, 9))
show(axes[0, 0], gx, "Horizontal derivative (Gx)", -0.25, 0.25)
show(axes[0, 1], gy, "Vertical derivative (Gy)", -0.25, 0.25)
show(axes[1, 0], raw_magnitude, "Gradient magnitude", vmax=0.4)
show(axes[1, 1], raw_edges, f"Edges: threshold = {raw_threshold}")
save(fig, "part12_results.png")

# Part 1.3: compare ordinary differences with blur-then-differentiate.
fig, axes = plt.subplots(3, 2, figsize=(9, 12))
show(axes[0, 0], image, "Original cameraman")
show(axes[0, 1], blurred, f"Gaussian blur: {kernel_size}x{kernel_size}, sigma = {sigma}")
show(axes[1, 0], raw_magnitude, "Without smoothing: magnitude", vmax=0.4)
show(axes[1, 1], magnitude, "With smoothing: magnitude", vmax=0.4)
show(axes[2, 0], raw_edges, f"Without smoothing: threshold = {raw_threshold}")
show(axes[2, 1], edges, f"With smoothing: threshold = {smooth_threshold}")
save(fig, "part13_smoothing.png")

# Display the small filters, not filtered images of the cameraman.
fig, axes = plt.subplots(1, 3, figsize=(10, 3.5))
limit = max(np.abs(dog_x).max(), np.abs(dog_y).max())
show(axes[0], gaussian, "Gaussian kernel", vmax=gaussian.max())
show(axes[1], dog_x, "DoG x kernel", -limit, limit)
show(axes[2], dog_y, "DoG y kernel", -limit, limit)
save(fig, "part13_filters.png")

# Keep the same intensity scale so the two routes can be compared visually.
fig, axes = plt.subplots(1, 2, figsize=(9, 4.5))
show(axes[0], magnitude, "Blur then differentiate: magnitude", vmax=0.4)
show(axes[1], dog_magnitude, "Combined DoG filters: magnitude", vmax=0.4)
save(fig, "part13_comparison.png")

print("Saved four figures in proj2/assets. Close the plot windows when finished.")
plt.show()
