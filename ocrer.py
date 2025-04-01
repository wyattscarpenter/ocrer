#!/usr/bin/env python3
# Largely generated by chatgpt.

# This script metadata is cool! Try uv run ocrer.py to run the script appropriately using these dependencies.
# /// script
# dependencies = [
#   "watchdog",
#   "pillow",
#   "pytesseract",
# ]
# ///

import os
import sys
import time
import re
import pytesseract
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)

debug = False #True

def dprint(*args, **kwargs):
  if debug:
    eprint(*args, **kwargs)

def parse_arguments():
    parser = argparse.ArgumentParser(description="OCR file renamer")
    parser.add_argument("--tesseract-path", type=str, help="Path to the Tesseract executable (defaults to just calling `tesseract` on your system, so if that's in your PATH you're probably fine.)")
    parser.add_argument("--watch-folder", type=str, default="ocr-me", help="Folder to watch for new images (default: 'ocr-me' in this folder)")
    return parser.parse_args()

class OCRRenameHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        time.sleep(1)  # Give some time for the file to be fully written # It's crazy that this was the automatically-generated code lmao.
        self.process(event.src_path)

    def process(self, file_path):
        try:
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image).strip()

            if not extracted_text:
                print(f"No text found in {file_path}, skipping rename.")
                return

            # This logic is largely taken from Wyatt S Carpenter's tessname.py, and the code could be shared using imports (but that seems like a hassle).
            dprint("raw:", extracted_text)
            extracted_text = re.sub(r"\|", "I", extracted_text) #for some reason it often gets these wrong
            extracted_text = extracted_text.lower()
            dprint("lowered:", extracted_text)
            extracted_text = re.sub(r"[^\w\s-]", "", extracted_text)
            dprint("sub out non-word:", extracted_text)
            extracted_text = re.sub(r"\s+", " ", extracted_text).strip()
            dprint("sub out spaces:", extracted_text)
            if not extracted_text:
                print(f"No recognizable text found in {file_path} after filtering, skipping rename.")
                return
            ext = os.path.splitext(file_path)[1] #this is "split ext(ention)", not "split text", btw.
            extracted_text = extracted_text[0:255-len(ext)-1] #limit name to make operating system happy #the -1 is for good luck! or, possibly, the trailing nul that other systems (file explorer, perhaps) occasionally must slap on there. Anyway, you get weird "too long" errors on windows and this makes those happen less often.
            new_file_path = os.path.join(os.path.dirname(file_path), f"{extracted_text}{ext}")

            os.rename(file_path, new_file_path)
            print(f"Renamed {file_path} -> {new_file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    args = parse_arguments()

    if args.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = args.tesseract_path

    WATCH_FOLDER = args.watch_folder

    event_handler = OCRRenameHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    print(f"Watching folder: {WATCH_FOLDER}")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
