#!/usr/bin/env python3
# ============================================================
#  argus_uploader.py  –  Run this on the Raspberry Pi
#  It watches a folder for new meteor images and uploads
#  them to the live Render site automatically.
#
#  Install on Pi:  pip install requests watchdog
#  Run:            python argus_uploader.py
# ============================================================

import os
import time
import requests
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── CONFIG – only thing you need to change ─────────────────
RENDER_URL   = "https://argus.onrender.com"   # Your Render URL
WATCH_FOLDER = "/home/pi/argus_images"        # Folder Pi saves images to
# ───────────────────────────────────────────────────────────

UPLOAD_ENDPOINT = f"{RENDER_URL}/api/upload"
SUPPORTED_TYPES = ('.jpg', '.jpeg', '.png')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)


def upload_image(filepath, cnn_confidence=0.0, is_meteor=False, sdr_confirmed=False):
    filename = os.path.basename(filepath)
    try:
        with open(filepath, 'rb') as f:
            response = requests.post(
                UPLOAD_ENDPOINT,
                files={'image': (filename, f, 'image/jpeg')},
                data={
                    'cnn_confidence': cnn_confidence,
                    'is_meteor':      str(is_meteor).lower(),
                    'sdr_confirmed':  str(sdr_confirmed).lower(),
                },
                timeout=30
            )
        if response.status_code == 201:
            log.info(f"✅ Uploaded: {filename}")
            return True
        else:
            log.error(f"❌ Failed to upload {filename}: {response.status_code} {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        log.error(f"❌ Could not connect to {RENDER_URL} — is it online?")
        return False
    except requests.exceptions.Timeout:
        log.error(f"❌ Upload timed out for {filename}")
        return False
    except Exception as e:
        log.error(f"❌ Unexpected error uploading {filename}: {e}")
        return False


def parse_metadata_from_filename(filename):
    cnn_confidence = 0.0
    is_meteor      = False
    if 'meteor' in filename.lower():
        is_meteor = True
        parts = filename.split('_')
        for part in parts:
            try:
                val = float(part)
                if 0.0 <= val <= 1.0:
                    cnn_confidence = val
                    break
            except ValueError:
                continue
    return cnn_confidence, is_meteor


class ImageUploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        _, ext = os.path.splitext(filepath)
        if ext.lower() not in SUPPORTED_TYPES:
            return
        time.sleep(1)
        log.info(f"📷 New image detected: {os.path.basename(filepath)}")
        cnn_confidence, is_meteor = parse_metadata_from_filename(filepath)
        upload_image(filepath, cnn_confidence=cnn_confidence, is_meteor=is_meteor)


def upload_existing_images():
    if not os.path.exists(WATCH_FOLDER):
        log.warning(f"Watch folder not found: {WATCH_FOLDER} — creating it")
        os.makedirs(WATCH_FOLDER, exist_ok=True)
        return
    existing = [
        f for f in os.listdir(WATCH_FOLDER)
        if os.path.splitext(f)[1].lower() in SUPPORTED_TYPES
    ]
    if existing:
        log.info(f"Found {len(existing)} existing image(s) — uploading...")
        for filename in existing:
            filepath = os.path.join(WATCH_FOLDER, filename)
            cnn_confidence, is_meteor = parse_metadata_from_filename(filename)
            upload_image(filepath, cnn_confidence=cnn_confidence, is_meteor=is_meteor)
            time.sleep(0.5)
    else:
        log.info("No existing images to upload.")


def main():
    log.info(f"🚀 ARGUS Uploader starting...")
    log.info(f"   Render URL:   {RENDER_URL}")
    log.info(f"   Watch folder: {WATCH_FOLDER}")
    upload_existing_images()
    handler  = ImageUploadHandler()
    observer = Observer()
    observer.schedule(handler, WATCH_FOLDER, recursive=False)
    observer.start()
    log.info(f"👀 Watching for new images in {WATCH_FOLDER}...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("Stopping uploader...")
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
