from PIL import Image


def preprocess(imagePath):
    clr_img = Image.open(imagePath)

    grayScale = clr_img.convert("L")
    thresh = grayScale.point(lambda x: 255 if x > 128 else 0)
    return thresh
