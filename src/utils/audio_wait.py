import os
import time

def wait_for_audio_file(path, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            return
        time.sleep(0.1)
    raise RuntimeError(f"Audio file not ready: {path}")