import numpy as np

def gaussian_2d(xy, A, mu_x, mu_y, sigma_x, sigma_y):
    x, y = xy
    return A * np.exp(-((x - mu_x) ** 2) / (2 * sigma_x ** 2) - ((y - mu_y) ** 2) / (2 * sigma_y ** 2))