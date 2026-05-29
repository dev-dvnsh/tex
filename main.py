import pytesseract
import argparse
from PIL import Image
from preprocessor import preprocess

try:
    parser = argparse.ArgumentParser(prog="tex", description="Extracts text from image")

    parser.add_argument("-i", "--image", help="Takes path to an image file")
    parser.add_argument("-l", "--lang", help="Takes language of text", default="eng")
    parser.add_argument("--preprocess", action="store_true")

    args = parser.parse_args()

    if args.preprocess:
        image = preprocess(args.image)  # returns a PIL Image
    else:
        image = Image.open(args.image)  # load normally
    text = pytesseract.image_to_string(image, args.lang)
    if text == "":
        print(f"No text found in {args.image}")
    else:
        print(text)


except Exception as e:
    print(e)
