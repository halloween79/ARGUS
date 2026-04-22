#!/usr/bin/env python3
# ============================================================
#  start_argus.py  –  Run this ONE script to launch everything
#  Usage:  python start_argus.py
#  Stop:   Ctrl+C
# ============================================================

import subprocess
import sys
import os
import time
import signal
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
log = logging.getLogger(__name__)

RENDER_URL   = "https://argus.onrender.com"
WATCH_FOLDER = "/home/pi/argus_images"

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
processes = []

def shutdown(signum=None, frame=None):
    log.info("\n🛑 Shutting down ARGUS...")
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    log.info("✅ All processes stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT,  shutdown)
signal.signal(signal.SIGTERM, shutdown)

def main():
    log.info("🚀 Starting ARGUS system...")
    log.info(f"   Render URL:   {RENDER_URL}")
    log.info(f"   Watch folder: {WATCH_FOLDER}")

    flask_script = os.path.join(BASE_DIR, "run.py")
    if not os.path.exists(flask_script):
        log.error("❌ Could not find run.py — make sure start_argus.py is in the same folder")
        sys.exit(1)

    log.info("🌐 Starting Flask site (localhost:5000)...")
    flask_proc = subprocess.Popen([sys.executable, flask_script], cwd=BASE_DIR)
    processes.append(flask_proc)
    time.sleep(2)

    if flask_proc.poll() is not None:
        log.error("❌ Flask failed to start.")
        shutdown()

    log.info("✅ Flask site running at http://localhost:5000")

    uploader_script = os.path.join(BASE_DIR, "argus_uploader.py")
    if not os.path.exists(uploader_script):
        log.error("❌ Could not find argus_uploader.py")
        shutdown()

    log.info("☁️  Starting Render uploader...")
    uploader_proc = subprocess.Popen(
        [sys.executable, uploader_script],
        cwd=BASE_DIR,
        env={**os.environ, "RENDER_URL": RENDER_URL, "WATCH_FOLDER": WATCH_FOLDER}
    )
    processes.append(uploader_proc)
    time.sleep(2)

    if uploader_proc.poll() is not None:
        log.error("❌ Uploader failed to start.")
        shutdown()

    log.info("✅ Uploader running — images will sync to Render automatically")
    log.info("=" * 50)
    log.info("  ARGUS is fully running!")
    log.info("  Local site:  http://localhost:5000")
    log.info(f"  Live site:   {RENDER_URL}")
    log.info("  Press Ctrl+C to stop everything")
    log.info("=" * 50)

    while True:
        time.sleep(5)
        if flask_proc.poll() is not None:
            log.warning("⚠️  Flask crashed — restarting...")
            flask_proc = subprocess.Popen([sys.executable, flask_script], cwd=BASE_DIR)
            processes[0] = flask_proc
            time.sleep(2)
        if uploader_proc.poll() is not None:
            log.warning("⚠️  Uploader crashed — restarting...")
            uploader_proc = subprocess.Popen(
                [sys.executable, uploader_script],
                cwd=BASE_DIR,
                env={**os.environ, "RENDER_URL": RENDER_URL, "WATCH_FOLDER": WATCH_FOLDER}
            )
            processes[1] = uploader_proc
            time.sleep(2)

if __name__ == '__main__':
    main()
