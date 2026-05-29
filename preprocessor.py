import cv2
from PIL import Image


def preprocess(imagePath):
    img = cv2.imread(str(imagePath))

    if img is None:
        raise FileNotFoundError(f"OpenCV could not read image: {imagePath}")
    grayScale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(grayScale, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    pil = Image.fromarray(thresh)
    return pil
