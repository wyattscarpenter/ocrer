This is a small program — some might even say a crappy program (as it's mostly about plugging one API into another, and I mostly got ChatGPT and copilot to write it for me, although sadly a lot of manual massaging (and downright coding) was still involved) — that watches a folder and ocrs files as you save them to the folder, moving them to subfolders afterwards. You should run it with uv, like uv run ocrer.py whatever_folder. By the time you're reading this, you can probably just uvx or pipx it. Check out uv run ocrer.py --help for various options. As of 2025-07-14 it reads:

usage: ocrer.py [-h] [--tesseract-path TESSERACT_PATH]
                [--truncate-name | --no-truncate-name] [--update-readme]
                watch_folder [watch_folder ...]

OCR file renamer

positional arguments:
  watch_folder          Folder(s) to watch for new images

options:
  -h, --help            show this help message and exit
  --tesseract-path TESSERACT_PATH
                        Path to the Tesseract executable (defaults to just
                        calling `tesseract` on your system, so if that's in
                        your PATH you're probably fine.)
  --truncate-name, --no-truncate-name
                        Truncate output filename to avoid OS errors (default:
                        true)

developer functionality:
  --update-readme       Update the readme file with the latest help output.
