import argparse
from PIL import Image

try:
    parser = argparse.ArgumentParser(prog="tex", description="Extracts text from image")

    parser.add_argument("-i", "--image")

    args = parser.parse_args()
    imgData = Image.open(args.image)
    print(imgData.size, imgData.format, imgData.mode)

except Exception as e:
    print(e)
