# src/ollama_llm.py
import subprocess
import time
import logging

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

OLLAMA_PATH = r"C:\Users\rsr26\AppData\Local\Programs\Ollama\ollama.exe"

# GPU-first (your current model)
GPU_MODEL = "llama3.1:8b"

# CPU-safe fallback (lighter, stable)
CPU_MODEL = "llama3.2:3b"

# Retry config
OLLAMA_RETRIES = 2
RETRY_DELAY_SEC = 2

# Minimum acceptable output length (safety)
MIN_WORDS = 40

logger = logging.getLogger(__name__)


# -------------------------------------------------
# INTERNAL RUNNER
# -------------------------------------------------

def _run_ollama(model: str, prompt: str) -> str:
    """
    Runs ollama once with the given model.
    Raises RuntimeError on failure.
    """
    result = subprocess.run(
        [OLLAMA_PATH, "run", model],
        input=prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    output = result.stdout.strip()

    if not output or len(output.split()) < MIN_WORDS:
        raise RuntimeError("LLM returned empty or weak response")

    return output


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def generate_short_script(prompt: str) -> str:
    """
    GPU-first script generation with CPU fallback.
    Guaranteed to return non-empty text or raise a clear error.
    """

    last_error = None

    # -------------------------------
    # 1️⃣ TRY GPU MODEL
    # -------------------------------
    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            logger.info(f"🧠 Ollama GPU attempt {attempt}")
            return _run_ollama(GPU_MODEL, prompt)
        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ GPU attempt {attempt} failed: {e}")
            time.sleep(RETRY_DELAY_SEC)

    logger.warning("🔥 GPU model failed, falling back to CPU model")

    # -------------------------------
    # 2️⃣ CPU FALLBACK (SAFE MODE)
    # -------------------------------
    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            logger.info(f"🧠 Ollama CPU attempt {attempt}")
            return _run_ollama(CPU_MODEL, prompt)
        except Exception as e:
            last_error = str(e)
            logger.warning(f"⚠️ CPU attempt {attempt} failed: {e}")
            time.sleep(RETRY_DELAY_SEC)

    # -------------------------------
    # ❌ TOTAL FAILURE
    # -------------------------------
    raise RuntimeError(
        f"Ollama failed after GPU + CPU attempts. Last error: {last_error}"
    )
