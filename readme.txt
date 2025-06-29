This is a small program — some might even say a crappy program (as it's mostly about plugging one API into another, and I mostly got ChatGPT and copilot to write it for me) — that runs in a folder and ocrs files as you save them to the folder, moving them to subfolders afterwards. You should run it with uv, which run.bat will conveniently do for you (this is a batch script that is also a valid shell script, so it works cross-platform). Check out uv run ocrer.py --help for various options. As of 2025-06-29 it reads:

uv run ocrer.py --help
usage: ocrer.py [-h] [--tesseract-path TESSERACT_PATH] [--watch-folder WATCH_FOLDER] [--truncate-name | --no-truncate-name]

OCR file renamer

options:
  -h, --help            show this help message and exit
  --tesseract-path TESSERACT_PATH
                        Path to the Tesseract executable (defaults to just calling `tesseract` on your system, so if that's in your PATH you're probably fine.)
  --watch-folder WATCH_FOLDER
                        Folder to watch for new images (default: 'ocr-me' in this folder)
  --truncate-name, --no-truncate-name
                        Truncate output filename to avoid OS errors (default: true)
