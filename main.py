import pytesseract
import argparse
from PIL import Image
from preprocessor import preprocess
from pathlib import Path
import sys
from colorama import Fore, Style, init, Back
from time import perf_counter

try:
    init()
    parser = argparse.ArgumentParser(
        prog="tex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extracts text from image files",
    )

    # commands are here
    parser.epilog = """ 
For Single image file: "tex -i path/to/image.png -o output.txt --print"
For Batch images/folder: "tex -f path/to/folder/" or "tex path/to/folder/"
    """

    parser.add_argument("-v", "--version", action="version", version="v1.0.0")
    parser.add_argument("-i", "--image", help="Takes path to an image file")
    parser.add_argument("-f", "--folder", help="batch the folder ")
    parser.add_argument("-l", "--lang", help="Takes language of text", default="eng")
    parser.add_argument("-o", "--output", help="Takes the output path")
    parser.add_argument("--verbose", action="store_true", help="Gives verbose output")
    parser.add_argument(
        "--preprocess", action="store_true", help="Clears image before conversion"
    )
    parser.add_argument(
        "--print", action="store_true", help="Prints the text while saving to file"
    )
    parser.add_argument(
        "path", nargs="?", help="Lets user type path like ./foldername or ."
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Search subfolders recursively"
    )

    # arguments are taken here
    args = parser.parse_args()

    if args.image and (args.folder or args.path):
        print(
            Fore.YELLOW
            + "Either use -i or -f (only one) or else just pass the path to folder no need for i or f"
        )

    elif args.folder and args.path:
        print(Fore.YELLOW + "Don't use -f and a path together, pick one")

    elif args.image:
        start = perf_counter()
        if args.preprocess:
            image = preprocess(args.image)  # returns a PIL Image
        else:
            image = Image.open(args.image)  # load normally
        text = pytesseract.image_to_string(image, args.lang)
        if text.strip() == "":
            print(Fore.RED + f"No text found in {args.image}")
            sys.exit(0)

        if args.print:
            print(Style.RESET_ALL + text)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
            print(Fore.GREEN + f"Text saved to {args.output}")

        else:
            path = args.image
            parent = Path(path).parent
            newPath = parent / f"{Path(args.image).stem}_output.txt"
            with open(newPath, "w", encoding="utf-8") as f:
                f.write(text)
            print(Fore.GREEN + f"Text saved to {newPath}")
        end = perf_counter()

        if args.verbose:
            print(Style.RESET_ALL + f"Your image path: {args.image}")
            print(f"Your image size: {image.size}")
            print(f"Language selected: {args.lang}")
            print(f"Processing: {'yes' if args.preprocess else 'no'}")
            print(f"Time taken: {end-start:.2f}s")

    else:
        if args.folder:
            path = args.folder

        elif args.path:
            path = args.path

        else:
            path = "."

        extensions = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff", "*.webp"]
        files = []
        if args.recursive:
            for single_extention in extensions:
                files.extend(Path(path).rglob(single_extention))
        else:
            for single_extention in extensions:
                files.extend(Path(path).glob(single_extention))
        success = 0
        for pos, item in enumerate(files, start=1):
            try:
                start = perf_counter()

                print(
                    Back.GREEN
                    + Fore.BLACK
                    + f"[{pos}/{len(files)}]"
                    + f"Processing: {item}"
                    + Style.RESET_ALL
                )
                if args.preprocess:
                    image = preprocess(item)  # returns a PIL Image
                else:
                    image = Image.open(item)  # load normally
                text = pytesseract.image_to_string(image, args.lang)
                if text.strip() == "":
                    print(Fore.YELLOW + f"No text found in {item}")
                    continue

                success += 1
                if args.print:
                    print(Style.RESET_ALL + text)

                if args.output:

                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(Fore.GREEN + f"Text saved to {args.output}")

                else:
                    parent = item.parent
                    name = item.stem
                    newPath = parent / f"{name}_output.txt"
                    with open(newPath, "w", encoding="utf-8") as f:
                        f.write(text)
                    print(Fore.GREEN + f"Text saved to {newPath}")
                end = perf_counter()
                if args.verbose:
                    print(Style.RESET_ALL + f"Your image path: {item}")
                    print(f"Your image size: {image.size}")
                    print(f"Language selected: {args.lang}")
                    print(f"Processing: {'yes' if args.preprocess else 'no'}")
                    print(f"Time taken: {end-start:.2f}s")

            except Exception as e:
                print(Fore.RED + f"Error processing {item}: {e}")
                continue
        print(Fore.GREEN + f"{success}/{len(files)} images processed")


except Exception as e:
    print(e)
