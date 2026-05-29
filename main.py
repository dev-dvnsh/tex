import pytesseract
import argparse
from PIL import Image

try:
    parser = argparse.ArgumentParser(prog="tex", description="Extracts text from image")

    parser.add_argument("-i", "--image", help="Takes path to an image file")
    parser.add_argument("-l", "--lang", help="Takes language of text", default="eng")

    args = parser.parse_args()
    text = pytesseract.image_to_string(args.image, args.lang)
    if text == "":
        print(f"No text found in {args.image}")
    else:
        print(text)


except Exception as e:
    print(e)
