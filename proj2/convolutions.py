import numpy as np


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
