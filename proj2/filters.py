import cv2
import numpy as np
from scipy.signal import convolve2d


def gaussian_kernel(kernel_size=9, sigma=1.5):
    g = cv2.getGaussianKernel(kernel_size, sigma)
    return g @ g.T


def apply_filter(image, kernel):
    image = np.asarray(image, dtype=float)

    if image.ndim == 2:
        return convolve2d(image, kernel, mode="same", boundary="symm")

    output = np.zeros_like(image)
    for channel in range(image.shape[2]):
        output[:, :, channel] = convolve2d(
            image[:, :, channel], kernel, mode="same", boundary="symm"
        )
    return output


def blur_image(image, kernel_size=9, sigma=1.5):
    gaussian = gaussian_kernel(kernel_size, sigma)
    return apply_filter(image, gaussian)


def sharpen_image(image, alpha=1.0, kernel_size=9, sigma=1.5):
    gaussian = gaussian_kernel(kernel_size, sigma)
    identity = np.zeros_like(gaussian)
    identity[kernel_size // 2, kernel_size // 2] = 1

    sharpen_kernel = (1 + alpha) * identity - alpha * gaussian
    return apply_filter(image, sharpen_kernel)


def hybrid_image(low_image, high_image, sigma_low=10, sigma_high=3):
    low_size = 2 * int(np.ceil(3 * sigma_low)) + 1
    high_size = 2 * int(np.ceil(3 * sigma_high)) + 1
    low = blur_image(low_image, low_size, sigma_low)
    high = high_image - blur_image(high_image, high_size, sigma_high)
    return low, high, low + high


def fourier_magnitude(image):
    return np.log1p(np.abs(np.fft.fftshift(np.fft.fft2(image))))
