# tex

A command line tool that extracts text from images using Tesseract OCR. Supports single images, batch processing entire folders, and recursive subfolder scanning. Output is saved as a .txt file alongside the original image by default.

Built with Python, Pillow, and pytesseract.

---

## Requirements

- Python 3.8+
- Tesseract OCR

On Arch Linux:

```
sudo pacman -S tesseract tesseract-data-eng
```

For other languages, for example Hindi:

```
sudo pacman -S tesseract-data-hin
```

Python dependencies:

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Flags

| Flag         | Short | Description                                |
| ------------ | ----- | ------------------------------------------ |
| --image      | -i    | Takes path to an image file                |
| --folder     | -f    | Batch process a folder of images           |
| --lang       | -l    | Takes language of text (default: eng)      |
| --output     | -o    | Takes the output path                      |
| --recursive  | -r    | Search subfolders recursively              |
| --preprocess |       | Clears image before conversion             |
| --print      |       | Prints the text while saving to file       |
| --verbose    |       | Gives verbose output                       |
| --version    | -v    | Show version                               |
| path         |       | Lets user type path like ./foldername or . |

---

## Usage

Single image, output saved next to the image automatically:

```
tex -i photo.png
```

Single image with custom output path:

```
tex -i photo.png -o result.txt
```

Print to terminal and save:

```
tex -i photo.png --print
```

Batch process a folder:

```
tex -f ./images/
```

Run in current directory:

```
tex .
tex
```

Batch with recursive subfolder search:

```
tex -f ./images/ -r
```

Specify language:

```
tex -i photo.png -l hin
tex -f ./images/ -l hin
```

Show processing info:

```
tex -i photo.png --verbose
```

---

## Output

By default, each image gets its own .txt file saved in the same folder:

```
photo.png -> photo_output.txt
scan.jpg  -> scan_output.txt
```

Use `-o` to specify a custom output path for single image mode.

---

## Supported Formats

png, jpg, jpeg, bmp, tiff, webp

---

## License

MIT
