import cv2
import pytesseract as pyt
from skimage.metrics import structural_similarity as ssim
import re


# Global Variables
CONFIG = r'--oem 3 --psm 6'


def compare_images(image1, image2):

    _, thresh_image1 = cv2.threshold(image1, 200, 255, cv2.THRESH_BINARY)
    _, thresh_image2 = cv2.threshold(image2, 200, 255, cv2.THRESH_BINARY)

    if thresh_image1.shape != thresh_image2.shape:
        thresh_image2 = cv2.resize(thresh_image2, (thresh_image1.shape[1], thresh_image1.shape[0]))

    score, _ = ssim(thresh_image1, thresh_image2, full=True)

    return score


def extract_numbers(img, sep=False):
    """Extracts numbers from image"""
    if sep:
        return list(map(int, re.findall('\d+', pyt.image_to_string(img, config=CONFIG))))
    return int(''.join(re.findall('\d+', pyt.image_to_string(img, config=CONFIG))))