import cv2
import numpy as np
from math import sqrt, sin, cos, atan2, exp, radians


def extract_mean_rgb(image_path):
    """
    Extract mean RGB from cleaned ROI image.
    Ignores extreme pixel values (outliers).
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    pixels = img.reshape(-1, 3).astype(np.float32)

    lower = np.percentile(pixels, 5, axis=0)
    upper = np.percentile(pixels, 95, axis=0)

    mask = np.all((pixels >= lower) & (pixels <= upper), axis=1)
    filtered_pixels = pixels[mask]

    return filtered_pixels.mean(axis=0)


def rgb_to_lab(rgb):
    rgb_norm = np.array([[rgb / 255.0]], dtype=np.float32)
    lab = cv2.cvtColor(rgb_norm, cv2.COLOR_RGB2LAB)
    return lab[0][0]


# -------------------------------------------------
# ΔE 2000 (Industry Standard)
# -------------------------------------------------
def delta_e_2000(lab1, lab2):
    L1, a1, b1 = lab1.astype(float)
    L2, a2, b2 = lab2.astype(float)

    avg_L = (L1 + L2) / 2
    C1 = sqrt(a1**2 + b1**2)
    C2 = sqrt(a2**2 + b2**2)
    avg_C = (C1 + C2) / 2

    G = 0.5 * (1 - sqrt((avg_C**7) / (avg_C**7 + 25**7)))
    a1p = (1 + G) * a1
    a2p = (1 + G) * a2

    C1p = sqrt(a1p**2 + b1**2)
    C2p = sqrt(a2p**2 + b2**2)

    h1p = atan2(b1, a1p) % (2 * np.pi)
    h2p = atan2(b2, a2p) % (2 * np.pi)

    dLp = L2 - L1
    dCp = C2p - C1p

    dhp = h2p - h1p
    if abs(dhp) > np.pi:
        dhp -= 2 * np.pi * np.sign(dhp)

    dHp = 2 * sqrt(C1p * C2p) * sin(dhp / 2)

    avg_Lp = (L1 + L2) / 2
    avg_Cp = (C1p + C2p) / 2

    if abs(h1p - h2p) > np.pi:
        avg_hp = (h1p + h2p + 2 * np.pi) / 2
    else:
        avg_hp = (h1p + h2p) / 2

    T = (
        1
        - 0.17 * cos(avg_hp - radians(30))
        + 0.24 * cos(2 * avg_hp)
        + 0.32 * cos(3 * avg_hp + radians(6))
        - 0.20 * cos(4 * avg_hp - radians(63))
    )

    d_ro = 30 * exp(-((avg_hp - radians(275)) / radians(25)) ** 2)
    R_C = sqrt((avg_Cp**7) / (avg_Cp**7 + 25**7))
    S_L = 1 + (0.015 * (avg_Lp - 50) ** 2) / sqrt(20 + (avg_Lp - 50) ** 2)
    S_C = 1 + 0.045 * avg_Cp
    S_H = 1 + 0.015 * avg_Cp * T
    R_T = -sin(2 * d_ro) * R_C

    dE = sqrt(
        (dLp / S_L) ** 2 +
        (dCp / S_C) ** 2 +
        (dHp / S_H) ** 2 +
        R_T * (dCp / S_C) * (dHp / S_H)
    )

    return dE
