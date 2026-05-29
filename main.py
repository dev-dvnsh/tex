import pytesseract
import argparse
from PIL import Image
from preprocessor import preprocess
from pathlib import Path
import sys

try:
    parser = argparse.ArgumentParser(prog="tex", description="Extracts text from image")

    parser.add_argument("-i", "--image", help="Takes path to an image file")
    parser.add_argument("-l", "--lang", help="Takes language of text", default="eng")
    parser.add_argument(
        "--preprocess", action="store_true", help="Clears image before conversion"
    )
    parser.add_argument("-o", "--output", help="Takes the output path")
    parser.add_argument("--print", action="store_true")

    args = parser.parse_args()

    if args.preprocess:
        image = preprocess(args.image)  # returns a PIL Image
    else:
        image = Image.open(args.image)  # load normally
    text = pytesseract.image_to_string(image, args.lang)
    if text == "":
        print(f"No text found in {args.image}")
        sys.exit(0)

    if args.print:
        print(text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved to {args.output}")

    else:
        path = args.image
        parent = Path(path).parent
        newPath = parent / "output.txt"
        with open(newPath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved to {newPath}")


except Exception as e:
    print(e)
