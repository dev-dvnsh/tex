import pytesseract
import argparse
from PIL import Image
from preprocessor import preprocess
from pathlib import Path
import sys
import glob
from colorama import Fore, Style, init

try:
    parser = argparse.ArgumentParser(
        prog="tex", description="Extracts text from image files"
    )

    # commands are here
    parser.add_argument("-i", "--image", help="Takes path to an image file")
    parser.add_argument("-f", "--folder", help="batch the folder ")
    parser.add_argument("-l", "--lang", help="Takes language of text", default="eng")
    parser.add_argument("-o", "--output", help="Takes the output path")
    parser.add_argument(
        "--preprocess", action="store_true", help="Clears image before conversion"
    )
    parser.add_argument(
        "--print", action="store_true", help="Prints the text while saving to file"
    )
    parser.add_argument(
        "path", nargs="?", help="Lets user type path like ./foldername or ."
    )

    # arguments are taken here
    args = parser.parse_args()

    if args.image and (args.folder or args.path):
        print(
            "Either use -i or -f (only one) or else just pass the path to folder no need for i or f"
        )
    elif args.image:
        if args.preprocess:
            image = preprocess(args.image)  # returns a PIL Image
        else:
            image = Image.open(args.image)  # load normally
        text = pytesseract.image_to_string(image, args.lang)
        if text.strip() == "":
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

    elif args.folder or args.path:
        # if args.folder == args.path:
        #     path = args.folder

        path = args.folder
        files = list(Path(path).glob("*.png"))
        success = 0
        for pos, item in enumerate(files, start=1):
            try:
                print(f"[{pos}/{len(files)}] Processing: {item}")
                if args.preprocess:
                    image = preprocess(item)  # returns a PIL Image
                else:
                    image = Image.open(item)  # load normally
                text = pytesseract.image_to_string(image, args.lang)
                if text.strip() == "":
                    print(f"No text found in {item}")
                    continue

                success += 1
                if args.print:
                    print(text)

                if args.output:

                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"Text saved to {args.output}")

                else:
                    parent = item.parent
                    name = item.stem
                    newPath = parent / f"{name}_output.txt"
                    with open(newPath, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(f"Text saved to {newPath}")
            except Exception as e:
                print(f"Error processing {item}: {e}")
                continue
        print(f"{success}/{len(files)} images processed")


except Exception as e:
    print(e)
