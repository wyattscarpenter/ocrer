#!/usr/bin/env python3
# Largely generated by GPT.

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
import select
if sys.platform.startswith('win'):
    import msvcrt

def eprint(*args, **kwargs) -> None:
  print(*args, file=sys.stderr, **kwargs)

debug = False #True

def dprint(*args, **kwargs) -> None:
  if debug:
    eprint(*args, **kwargs)

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OCR file renamer")
    parser.add_argument("--tesseract-path", type=str, help="Path to the Tesseract executable (defaults to just calling `tesseract` on your system, so if that's in your PATH you're probably fine.)")
    parser.add_argument("--watch-folder", type=str, default="ocr-me", help="Folder to watch for new images (default: 'ocr-me' in this folder)")
    parser.add_argument("--truncate-name", action=argparse.BooleanOptionalAction, default=True, help="Truncate output filename to avoid OS errors (default: true)")
    return parser.parse_args()

class OCRRenameHandler(FileSystemEventHandler):
    def on_created(self, event) -> None:
        if event.is_directory:
            return

        time.sleep(1)  # Give some time for the file to be fully written # It's crazy that this was the automatically-generated code lmao.
        self.process(event.src_path)

    def process(self, file_path) -> None:
        try:
            # Create necessary directories if they don't exist
            base_dir = os.path.dirname(file_path)
            success_dir = os.path.join(base_dir, "has-been-ocr'd")
            failure_dir = os.path.join(base_dir, "ocr-failure")
            
            os.makedirs(success_dir, exist_ok=True)
            os.makedirs(failure_dir, exist_ok=True)

            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image).strip()

            if not extracted_text:
                print(f"No text found in {file_path}, moving to ocr-failure.")
                os.rename(file_path, os.path.join(failure_dir, os.path.basename(file_path)))
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
                print(f"No recognizable text found in {file_path} after filtering, moving to ocr-failure.")
                os.rename(file_path, os.path.join(failure_dir, os.path.basename(file_path)))
                return
            
            ext = os.path.splitext(file_path)[1] #this is "split ext(ension)", not "split text", btw.
            if args.truncate_name:
                extracted_text = extracted_text[0:255-len(ext)-1] #limit name to make operating system happy #the -1 is for good luck! or, possibly, the trailing nul that other systems (file explorer, perhaps) occasionally must slap on there. Anyway, you get weird "too long" errors on windows and this makes those happen less often.
            new_file_name = f"{extracted_text}{ext}"
            new_file_path = os.path.join(success_dir, new_file_name)

            os.rename(file_path, new_file_path)
            print(f"Successfully processed {file_path} -> {new_file_name}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    args = parse_arguments()

    if args.tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = args.tesseract_path

    WATCH_FOLDER = args.watch_folder

    event_handler = OCRRenameHandler()
    print(f"Processing any pre-existing files in {WATCH_FOLDER}...")
    for filename in os.listdir(WATCH_FOLDER):
        file_path = os.path.join(WATCH_FOLDER, filename)
        if os.path.isfile(file_path):
            event_handler.process(file_path)

    # Set up the observer for new files
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    print(f"Watching folder: {WATCH_FOLDER}")
    print("Type 'q' to quit, 'e' to open the folder in the file browser.")
    try:
        while True:
            if sys.platform.startswith('win'):
                import msvcrt
                start_time = time.time()
                while True:
                    if msvcrt.kbhit():
                        ch = msvcrt.getwch()
                        if ch.lower() == 'q':
                            print("Quitting...")
                            exit()
                        elif ch.lower() == 'e':
                            print(f"Opening {WATCH_FOLDER} in file explorer...")
                            os.startfile(WATCH_FOLDER)
                        elif ch == '\r' or ch == '\n':
                            break
                    if time.time() - start_time > 10:
                        break
                    time.sleep(0.1)
            else:
                rlist, _, _ = select.select([sys.stdin], [], [], 10)
                if rlist:
                    user_input = sys.stdin.readline().strip().lower()
                    if user_input == 'q':
                        print("Quitting...")
                        exit()
                    elif user_input == 'e':
                        print(f"Opening {WATCH_FOLDER} in file browser...")
                        import subprocess
                        subprocess.Popen(['xdg-open', WATCH_FOLDER])
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
