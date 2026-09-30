import numpy as np
from scipy.signal import convolve2d


def convolve_four_loops(image, kernel):
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    height, width = image.shape
    kernel_height, kernel_width = kernel.shape

    flipped = np.flip(kernel, axis=(0, 1))
    pad_y = kernel_height // 2
    pad_x = kernel_width // 2

    padded = np.pad(image, ((pad_y, pad_y), (pad_x, pad_x)), mode="constant",
        constant_values=0,
    )
    output = np.zeros((height, width), dtype=float)
    for y in range(height):
        for x in range(width):
            total = 0
            for kernel_y in range(kernel_height):
                for kernel_x in range(kernel_width):
                    total += (padded[y + kernel_y, x + kernel_x] * flipped[kernel_y, kernel_x])
            output[y, x] = total
    return output

def convolve_two_loops(image, kernel):
    image = np.asarray(image, dtype=float)
    kernel = np.asarray(kernel, dtype=float)
    height, width = image.shape
    kernel_height, kernel_width = kernel.shape

    flipped = np.flip(kernel, axis=(0, 1))
    pad_y = kernel_height // 2
    pad_x = kernel_width // 2

    padded = np.pad(image, ((pad_y, pad_y), (pad_x, pad_x)), mode="constant",
        constant_values=0,
    )
    output = np.zeros((height, width), dtype=float)
    for y in range(height):
        for x in range(width):
            output[y, x] = np.sum(padded[y : y + kernel_height, x : x + kernel_width] * flipped)
    return output


def finite_difference_edges(image, threshold):
    "0.21 threshold seems good for part 1.2"
    image = np.asarray(image, dtype=float)
    height, width = image.shape
    dx = np.array([[1, 0, -1]], dtype=float)
    dy = np.array([[1], [0], [-1]], dtype=float)

    gx = convolve2d(image, dx, mode="same", boundary="fill", fillvalue=0)
    gy = convolve2d(image, dy, mode="same", boundary="fill", fillvalue=0)

    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    edges = magnitude > threshold

    return gx, gy, magnitude, edges


def derivative_of_gaussian_edges(image, threshold, kernel_size=9, sigma=1.5):
    import cv2

    image = np.asarray(image, dtype=float)
    dx = np.array([[1, 0, -1]], dtype=float)
    dy = np.array([[1], [0], [-1]], dtype=float)

    g = cv2.getGaussianKernel(kernel_size, sigma)
    gaussian = g @ g.T

    blurred = convolve2d(image, gaussian, mode="same", boundary="fill", fillvalue=0)
    gx, gy, magnitude, edges = finite_difference_edges(blurred, threshold)


    dog_x = convolve2d(gaussian, dx, mode="full", boundary="fill", fillvalue=0)
    dog_y = convolve2d(gaussian, dy, mode="full", boundary="fill", fillvalue=0)

    dog_gx = convolve2d(image, dog_x, mode="same", boundary="fill", fillvalue=0)
    dog_gy = convolve2d(image, dog_y, mode="same", boundary="fill", fillvalue=0)
    dog_magnitude = np.sqrt(dog_gx ** 2 + dog_gy ** 2)

    same_x = np.allclose(gx[1:-1, 1:-1], dog_gx[1:-1, 1:-1], rtol=0, atol=1e-12)
    same_y = np.allclose(gy[1:-1, 1:-1], dog_gy[1:-1, 1:-1], rtol=0, atol=1e-12)
    print(f"Blur then differentiate vs DoG (excluding border): x matches = {same_x}")
    print(f"Blur then differentiate vs DoG (excluding border): y matches = {same_y}")

    return blurred, magnitude, edges, dog_x, dog_y, dog_magnitude
