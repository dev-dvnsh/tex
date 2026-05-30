# getx — Image-to-Text CLI Tool (Go Build Roadmap)

> Each task is a standalone building block. Complete them in order — every task depends on the previous one. **Platform:** Arch Linux | **Language:** Go | **Tool name:** `getx`

---

## Task 1 — Set Up Your Project Environment

### What This Task Does

Installs system dependencies, creates the project directory, initializes a Go module, and verifies everything works together.

### Prerequisite

- Arch Linux with `pacman` available
- Internet connection

### What to Learn and Understand

**Why Go instead of Python?** Go compiles to a single static binary with no runtime or dependencies. No virtual environments, no `pip install`, no "works on my machine." One `go build` and you ship a file that runs on every Linux system — no Python, no venv, nothing else needed.

**How does Go handle dependencies?** Go uses a module system (`go.mod` + `go.sum`). When you run `go get`, Go downloads the source code of the dependency, pins its version in `go.mod`, and compiles it directly into your binary. There's no separate install step — `go build` fetches and compiles everything in one command.

**What is CGo and why does it matter?** CGo lets Go programs call C libraries. `gosseract` uses CGo to link against `libtesseract`. This means: (1) you need `tesseract` and its C headers installed at build time, (2) the resulting binary is dynamically linked to `libtesseract.so`, so it still needs Tesseract on the target system. Go's usual "static binary" promise only applies to pure Go code — CGo breaks that.

**Can I avoid CGo?** There's `gosseract` (CGo) and `tesseract.rs`-style bindings — not much avoids CGo for Tesseract. Some projects shell out to the `tesseract` binary instead (like pytesseract does), but that's slower and fragile. For this project, CGo is acceptable. It means `getx` needs Tesseract installed at runtime, same as the Python version.

### What to Do

1. Install Go:

   ```bash
   sudo pacman -S go
   ```

2. Install Tesseract (still needed as runtime dependency):

   ```bash
   sudo pacman -S tesseract tesseract-data-eng
   ```

   For other languages e.g. Hindi:

   ```bash
   sudo pacman -S tesseract-data-hin
   ```

3. Install Tesseract C headers (needed by gosseract at compile time):

   ```bash
   sudo pacman -S tesseract
   ```

4. Create project directory:

   ```bash
   mkdir getx && cd getx
   ```

5. Initialize Go module:

   ```bash
   go mod init github.com/yourname/getx
   ```

6. Install gosseract:

   ```bash
   go get github.com/otiai10/gosseract/v2
   ```

7. Verify the build works (empty main is fine):

   ```bash
   cat > main.go << 'EOF'
   package main

   func main() {}
   EOF
   go build -o getx .
   ```

8. Verify `libtesseract` is linkable:

   ```bash
   ldconfig -p | grep tesseract
   ```

   You should see `libtesseract.so` listed.

> ⚠️ **CGo note:** If you get linker errors during `go build` later, install `base-devel` (`sudo pacman -S base-devel`) for the C compiler toolchain.

---

## Task 2 — CLI Arguments and Image Loading

### What This Task Does

Creates `main.go` — the entry point of `getx`. Learns how to accept command-line arguments using Go's `flag` package and load an image file, confirming the pipeline works before adding OCR.

### Prerequisite

- Task 1 complete
- A test image (`.jpg` or `.png`) somewhere on your system

### What to Learn and Understand

**How does Go receive command-line arguments?** Go stores raw arguments in `os.Args` (a `[]string`), but the `flag` package parses them declaratively. You define flags with `flag.String()`, `flag.Int()`, `flag.Bool()` etc., then call `flag.Parse()`. Unlike Python's argparse, Go's `flag` package doesn't support `-i` and `--image` interchangeably — you pick one convention. We'll use `--image` with long-form flags.

**How does Go load images?** Go's standard library includes `image/jpeg`, `image/png`, `image/gif`, and `image/png` decoders. You register them with blank imports (`import _ "image/png"`), then `image.Decode()` automatically picks the right decoder based on the file header. The result is an `image.Image` interface — you can query `.Bounds()`, `.ColorModel()`, etc.

**What is deferred execution?** `defer file.Close()` tells Go to run `file.Close()` when the surrounding function returns — whether it returns normally or panics. This is Go's idiomatic way to ensure resources are cleaned up. You open a file, immediately defer close, then do your work without worrying about forgetting to close.

### What to Do

1. Delete the placeholder `main.go` from Task 1 and create a proper one:

   Create `main.go` with the following structure:
   - Package `main`
   - Imports: `flag`, `fmt`, `image`, `os`, `_ "image/jpeg"`, `_ "image/png"`
   - `main()` function
   - Use `flag.String("image", "", "Path to image file")`
   - Call `flag.Parse()`
   - Validate `--image` is provided (check empty string)
   - Open file with `os.Open()`, defer close
   - Decode with `image.Decode()`
   - Print bounds (width x height), color model

2. Error handling:
   - `os.Open()` error → print "Could not open file: <reason>" and `os.Exit(1)`
   - `image.Decode()` error → print "Could not decode image: <reason>" and `os.Exit(1)`
   - No `--image` given → print "Usage: getx --image <file>" and `os.Exit(1)`

3. Build and test:

   ```bash
   go build -o getx .
   ./getx --image photo.jpg
   ```

4. Verify the output shows width x height and color model.

---

## Task 3 — Extract Text From an Image (Core OCR)

### What This Task Does

Adds the actual OCR — passes the loaded image through Tesseract via gosseract and prints the extracted text. This is the core feature of `getx`.

### Prerequisite

- Task 2 complete (image loading + CLI argument working)

### What to Learn and Understand

**How does gosseract work?** gosseract is a Go binding around the C API of libtesseract (libtesseract's C API is exposed via `tesseract.h`). Unlike pytesseract (which shells out to the `tesseract` binary), gosseract calls into libtesseract directly as a shared library. This means: (1) it's faster — no subprocess overhead, (2) it needs `libtesseract.so` at both compile and runtime, (3) you must install Tesseract's development headers (`tesseract` on Arch) at build time.

**How does gosseract's API work?** You create a client with `gosseract.NewClient()`, configure it with methods like `.SetLanguage()`, `.SetImage()`, `.SetPageSegMode()`, then call `.Text()` to run OCR. The client holds internal state, so you should `.Close()` it when done. The typical pattern is: NewClient → configure → Text → Close (or defer Close).

**What is Page Segmentation Mode (PSM)?** Same concept as the Python version. gosseract exposes `tesseract.PageSegMode` constants: `PSM_AUTO` (3, full page), `PSM_SINGLE_BLOCK` (6), `PSM_SINGLE_LINE` (7), `PSM_SINGLE_WORD` (8), `PSM_RAW_LINE` (13). For general images, `PSM_AUTO` is best. We'll stick with the default for now.

### What to Do

1. Import gosseract: `"github.com/otiai10/gosseract/v2"`

2. After image loading, create a gosseract client:

   ```go
   client := gosseract.NewClient()
   defer client.Close()
   ```

3. Set the image path and language:

   ```go
   client.SetImage(imagePath)
   client.SetLanguage("eng")
   ```

4. Call `client.Text()` to get the extracted text.

5. Trim whitespace from the result. If empty, print "No text found in image."

6. Otherwise print the extracted text.

7. Add `--lang` flag (default `"eng"`).

8. Build and test:

   ```bash
   go build -o getx .
   ./getx --image photo.jpg
   ./getx --image photo.jpg --lang hin
   ```

---

## Task 4 — Preprocess the Image to Improve Accuracy

### What This Task Does

Adds optional image preprocessing using pure Go — converting to grayscale and applying Otsu's threshold — so Tesseract gets cleaner input. No OpenCV, no CGo dependencies.

### Prerequisite

- Task 3 complete (basic OCR working end-to-end)

### What to Learn and Understand

**Why pure Go instead of gocv?** gocv (Go bindings for OpenCV) pulls in a massive C dependency chain — cross-compilation becomes painful, binary size balloons, and you need OpenCV installed on every build machine. Since we only need grayscale + thresholding (about 50 lines of pixel math), pure Go is simpler, keeps the binary statically linkable, and makes cross-compilation trivial.

**How does grayscale conversion work in code?** An RGB pixel has three values (R, G, B). A grayscale pixel has one value (luminance). The standard formula is: `gray = 0.299*R + 0.587*G + 0.114*B` — these weights match human perception (we're most sensitive to green). You iterate over every pixel, apply the formula, and produce a new grayscale image.

**How does Go's image package represent pixels?** Go's `image.Image` interface returns colors via `img.At(x, y)`. But for performance, concrete types like `image.RGBA` let you access the pixel buffer directly via `img.Pix[y*img.Stride + x*4 + channel]`. For grayscale output, you use `image.Gray` which stores one byte per pixel.

**How does Otsu's thresholding work?** Otsu's method automatically finds the optimal threshold to separate foreground (text) from background:
1. Compute a histogram of all pixel intensities (0–255)
2. For every possible threshold value (0–255), calculate:
   - Weight of background pixels (below threshold)
   - Weight of foreground pixels (above threshold)
   - Variance between the two groups
3. Pick the threshold that maximizes between-class variance
4. Apply it: pixels below threshold → black (0), above → white (255)

The math looks intimidating but is ~20 lines of Go.

### What to Do

1. Create `preproc/preprocess.go`:

   ```
   getx/
   ├── main.go
   ├── preproc/
   │   └── preprocess.go
   ├── go.mod
   └── go.sum
   ```

2. In `preproc/preprocess.go`, create a `Preprocess(imagePath string) (*image.Gray, error)` function:
   - Open and decode the image
   - Convert to grayscale using luminance formula
   - Compute histogram of grayscale values
   - Calculate Otsu threshold
   - Apply binary threshold (black/white)
   - Return the processed `*image.Gray`

3. In `main.go`, add `--preprocess` boolean flag.

4. If `--preprocess` is passed, call `preproc.Preprocess()` and save to a temp file, then pass temp file path to gosseract.

   (gosseract works with file paths by default. For in-memory processing, you'd save the processed image to a temp file or use SetImageFromBytes.)

5. Build and test:

   ```bash
   go build -o getx .
   ./getx --image blurry.jpg
   ./getx --image blurry.jpg --preprocess
   ```

---

## Task 5 — Save Output to a Text File

### What This Task Does

Adds the ability to write extracted text to a `.txt` file, with smart auto-generated filenames when no output path is specified.

### Prerequisite

- Task 4 complete (full OCR pipeline with optional preprocessing)

### What to Learn and Understand

**How does Go handle file paths?** Go's `path/filepath` package is equivalent to Python's `pathlib`. Key functions: `filepath.Dir(path)` → parent directory, `filepath.Base(path)` → filename with extension, strings before the last dot via custom logic (Go has no built-in "stem" — you use `strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))`), `filepath.Join(dir, name)` → safe path concatenation.

**How does Go write to a file?** `os.WriteFile(path, []byte(content), 0644)` writes a byte slice to a file in one call — creates if missing, truncates if exists, sets permissions. For more control, use `os.Create()` which returns a `*File` you can write to with `f.WriteString()` or `f.Write()`.

**What does auto-generating filenames look like in practice?** If input is `/home/user/photos/receipt.jpg`, then `filepath.Dir(path)` = `/home/user/photos`, stem = `receipt`, output = `/home/user/photos/receipt_output.txt`.

### What to Do

1. Add `--output` / `-o` flag (optional, empty string default).

2. Add `--print` flag (`bool`, default `false`).

3. After OCR, if `--print` is true, print the text to stdout.

4. If `--output` is set, write to that path. Otherwise auto-generate:
   - Extract directory: `filepath.Dir(imagePath)`
   - Extract stem: trim extension from `filepath.Base(imagePath)`
   - Combine: `filepath.Join(dir, stem + "_output.txt")`

5. Write with `os.WriteFile(outputPath, []byte(text), 0644)`.

6. Print success message: `fmt.Printf("Text saved to %s\n", outputPath)`.

7. Build and test:

   ```bash
   go build -o getx .
   ./getx --image photo.jpg -o result.txt
   ./getx --image photo.jpg               # auto-generates
   ./getx --image photo.jpg --print       # prints AND saves
   ```

---

## Task 6 — Smart Input: Batch Processing + Current Directory Default

### What This Task Does

Upgrades `getx` to work like familiar Unix tools — you can point it at a directory, pass `.` for the current directory, or run it with no arguments and it scans wherever you are. Each image gets its own `.txt` output file.

### Prerequisite

- Task 5 complete (single image + file output working)

### What to Learn and Understand

**How does Go handle directory walking?** `os.ReadDir(path)` reads a directory and returns `[]os.DirEntry`. Each entry has `.Name()`, `.IsDir()`, `.Type()`. For recursive walking, `filepath.WalkDir()` traverses subdirectories. To match file extensions, use `strings.HasSuffix(entry.Name(), ".jpg")` or `filepath.Ext()`.

**How do you scan for multiple extensions?** Iterate over a list of extensions (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`) and collect matching files. You'll build a combined list of candidate files before processing.

**How does Go handle variable argument modes?** Use the zero-value pattern: check if `--image` was provided (non-empty), check if a positional arg was provided (`flag.NArg() > 0`), fall back to current directory. The `flag` package treats non-flag args as `flag.Args()` — so `getx .` means `.` is available at `flag.Arg(0)`.

### What to Do

1. Add a subcommand or positional argument for path. Since Go's `flag` package handles positional args with `flag.Args()`, use that:
   - `getx` → batch current directory
   - `getx .` → batch current directory  
   - `getx ./folder` → batch that folder
   - `getx --image photo.jpg` → single file (existing behavior)

2. Write the priority logic:
   - `--image` given → single file mode
   - `flag.NArg() > 0` → batch that directory path
   - nothing given → batch `"."` (current directory)

3. In batch mode:
   - Read the directory with `os.ReadDir(path)`
   - Filter files by extension
   - Loop over images, run full OCR pipeline per file
   - Wrap each iteration in error handling so one bad file doesn't stop the batch
   - Track success/fail counts

4. Print progress: `fmt.Printf("[%d/%d] Processing: %s\n", current, total, filename)`

5. Print summary at end.

6. Build and test:

   ```bash
   cd ~/photos && ./getx          # scans current folder
   ./getx .                       # same
   ./getx ./subfolder             # scans subfolder
   ./getx --image single.jpg      # single file still works
   ```

---

## Task 7 — Polish the CLI: Colors, Help Text & Verbose Mode

### What This Task Does

Final UX pass — colored terminal output, proper `--help` with examples, `--version`, and `--verbose` mode. Makes `getx` feel like a polished tool.

### Prerequisite

- Task 6 complete (full batch + smart input working)

### What to Learn and Understand

**How does terminal color work in Go?** Same ANSI escape codes as any language: `\033[32m` = green, `\033[31m` = red, `\033[33m` = yellow, `\033[0m` = reset. Go doesn't need colorama (colorama exists because Windows terminals don't support ANSI natively — modern Windows Terminal does, and on Linux it's universal). Just define color constants and use `fmt.Printf()`.

**How does Go's `flag` package handle help text?** `flag.PrintDefaults()` prints auto-generated help, but it's ugly. A better approach: write a custom `Usage` function using `fmt.Fprintf(os.Stderr, ...)` and register it with `flag.Usage = myUsageFunc`. This lets you format help text with examples, grouping, and any style you want.

**How do you implement `--version` in Go?** Go has no built-in version flag. Common patterns:
- Define a `version` variable: `var version = "1.0.0"`
- In `init()` or `main()`, check a `--version` flag and print + exit
- For production: use `-ldflags` to inject version at build time: `go build -ldflags="-X main.version=1.0.0"`

**How do you time operations in Go?** `time.Now()` returns the current time. Call it before the operation, call `time.Since(start)` after. For finer precision, use `time.Now().UnixNano()` or the `time` package's monotonic clock.

### What to Do

1. Add color constants at package level:
   ```go
   const (
     colorGreen  = "\033[32m"
     colorRed    = "\033[31m"
     colorYellow = "\033[33m"
     colorReset  = "\033[0m"
   )
   ```

2. Create a custom `Usage` function for `--help` that shows:
   - Description of what `getx` does
   - All flags with their descriptions
   - 3–4 usage examples at the bottom

3. Register it: `flag.Usage = myUsage`

4. Add `--version` flag — if set, print `"getx v1.0.0"` and exit.

5. Add `--verbose` flag — when set, print:
   - Resolved input path
   - Image dimensions
   - Language
   - Whether preprocessing ran
   - Time taken per image

6. Wrap all output in color: green for success, red for errors, yellow for warnings.

7. Build and test:

   ```bash
   go build -o getx .
   ./getx --help      # should look clean and complete
   ./getx --version   # should print version
   ./getx -i photo.jpg --verbose
   ```

---

## Task 8 — Cross-Compile & Distribute

### What This Task Does

Compiles `getx` into a single binary and cross-compiles for other platforms. After this task, you have a distributable binary ready to share on GitHub releases.

### Prerequisite

- Task 7 complete (fully polished tool)

### What to Learn and Understand

**How does Go cross-compilation work?** Go makes cross-compilation trivial — set `GOOS` (target operating system) and `GOARCH` (target architecture) environment variables, then `go build`. No cross-compiler toolchain needed, no special build flags. Examples:
- `GOOS=linux GOARCH=amd64` — Linux x86_64
- `GOOS=linux GOARCH=arm64` — Linux ARM (Raspberry Pi, Apple Silicon)
- `GOOS=darwin GOARCH=amd64` — macOS Intel
- `GOOS=darwin GOARCH=arm64` — macOS Apple Silicon
- `GOOS=windows GOARCH=amd64` — Windows x86_64

**Does CGo affect cross-compilation?** Yes — CGo cross-compilation requires a cross-compiler toolchain for the target platform, which is painful to set up. Since `gosseract` uses CGo, cross-compilation for non-Linux targets will be difficult. Solutions:
- **Best approach:** Cross-compile for Linux targets (amd64, arm64) only — these share the same C ABI and can link against the same libtesseract API.
- **Alternative:** Write a fallback mode that shells out to the `tesseract` binary (pure Go, no CGo), which works cross-platform but needs Tesseract installed on the target.

In practice, since Tesseract is a runtime dependency anyway, Linux-only distribution is acceptable for now.

**What's the best distribution method?** GitHub Releases with attached binaries, plus `go install` for Go users who have the toolchain:
```bash
go install github.com/yourname/getx@latest
```

### What to Do

1. Build for current platform:

   ```bash
   go build -ldflags="-s -w" -o getx .
   ```

   The `-ldflags="-s -w"` strips debug info and reduces binary size.

2. Cross-compile for Linux amd64 and arm64:

   ```bash
   GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o getx-linux-amd64 .
   GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o getx-linux-arm64 .
   ```

3. Verify binary size and test:

   ```bash
   ls -lh getx*
   ./getx-linux-amd64 --version
   ```

4. Install to `~/.local/bin`:

   ```bash
   cp getx ~/.local/bin/getx
   chmod +x ~/.local/bin/getx
   ```

5. Ensure `~/.local/bin` is in PATH. Add to `~/.zshrc` if missing:

   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

6. Run from anywhere:

   ```bash
   cd /tmp && getx -i ~/photo.jpg
   getx .
   ```

> ⚠️ **CGo note:** Since we used `gosseract` (CGo), these binaries need `libtesseract.so` on the target system. Users must `sudo pacman -S tesseract` or equivalent. For a truly static binary, you'd need a pure Go Tesseract implementation or shell out to the `tesseract` binary.

### Bonus: Pure Go fallback for truly static binaries

If you want a fully static binary with zero runtime dependencies:
1. Remove gosseract dependency
2. Instead of linking libtesseract, call the `tesseract` binary via `os/exec`
3. Feed the image via stdin: `tesseract stdin stdout -l eng`
4. This makes `go build` produce a fully static binary, but requires `tesseract` on PATH at runtime

---

## Final Project Structure

```
getx/
├── main.go              # CLI entry point
├── preproc/
│   └── preprocess.go    # Image preprocessing (pure Go)
├── go.mod               # Go module definition
├── go.sum               # Go module checksums
├── roadmap-go.md        # This file
└── getx                 # Compiled binary (generated, not committed)
```

## Quick Reference — All CLI Flags

| Flag           | Type    | Description                              |
| -------------- | ------- | ---------------------------------------- |
| `--image`      | string  | Single image file                        |
| `--output`     | string  | Output `.txt` path (optional)            |
| `--lang`       | string  | Tesseract language code (default: `eng`) |
| `--preprocess` | bool    | Enable preprocessing (grayscale + Otsu)  |
| `--print`      | bool    | Print to terminal even when saving       |
| `--verbose`    | bool    | Show path, size, lang, timing            |
| `--version`    | bool    | Print `getx v1.0.0`                      |
| `path`         | arg     | Positional: `getx .` or `getx ./folder`  |

## Arch Linux Cheat Sheet

```bash
# Install Go and Tesseract (once)
sudo pacman -S go tesseract tesseract-data-eng

# Create and initialize module (once)
go mod init github.com/yourname/getx
go get github.com/otiai10/gosseract/v2

# Build during development
go build -o getx .

# Run
./getx --image photo.jpg
./getx --image photo.jpg --preprocess --verbose
./getx .                                    # batch current directory

# Install globally
cp getx ~/.local/bin/getx && chmod +x ~/.local/bin/getx

# Run from anywhere
getx -i photo.jpg
getx .

# Cross-compile for release
GOOS=linux GOARCH=amd64 go build -ldflags="-s -w" -o getx-linux-amd64 .
GOOS=linux GOARCH=arm64 go build -ldflags="-s -w" -o getx-linux-arm64 .
```
