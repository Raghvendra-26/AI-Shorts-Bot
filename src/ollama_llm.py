# src/ollama_llm.py
import subprocess
import time
import logging
import re

# -------------------------------------------------
# CONFIG
# -------------------------------------------------

OLLAMA_PATH = r"C:\Users\rsr26\AppData\Local\Programs\Ollama\ollama.exe"

# GPU-first (primary model)
GPU_MODEL = "llama3.1:8b"

# CPU-safe fallback (lighter, stable)
CPU_MODEL = "llama3.2:3b"

# Retry config
OLLAMA_RETRIES = 2
RETRY_DELAY_SEC = 2

# Minimum acceptable output length (Shorts-safe)
MIN_WORDS = 90

logger = logging.getLogger(__name__)


# -------------------------------------------------
# INTERNAL HELPERS
# -------------------------------------------------

SYSTEM_INSTRUCTION = """
You are generating spoken narration for short-form video.
Follow these rules strictly:
- Spoken dialogue only
- Do NOT mention scripts, writing, or videos
- Do NOT explain what you are doing
- No headings, lists, emojis, or formatting
- Natural conversational tone
"""

TRAILING_GARBAGE_PATTERNS = [
    r"^sure[,!\- ]*",
    r"^here('?s| is) .*",
    r"as requested",
    r"let me know",
]


def _clean_llm_output(text: str) -> str:
    """
    Light cleanup to prevent downstream wipes.
    DOES NOT rewrite content.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    cleaned = []

    for line in lines:
        lowered = line.lower()
        if any(re.search(p, lowered) for p in TRAILING_GARBAGE_PATTERNS):
            continue
        cleaned.append(line)

    return " ".join(cleaned).strip()


# -------------------------------------------------
# INTERNAL RUNNER
# -------------------------------------------------

def _run_ollama(model: str, prompt: str) -> str:
    """
    Runs ollama once with the given model.
    Raises RuntimeError on failure.
    """

    full_prompt = SYSTEM_INSTRUCTION.strip() + "\n\n" + prompt.strip()

    result = subprocess.run(
        [OLLAMA_PATH, "run", model],
        input=full_prompt,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="ignore"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    output = _clean_llm_output(result.stdout.strip())

    if not output:
        raise RuntimeError("LLM returned empty response")

    if len(output.split()) < MIN_WORDS:
        raise RuntimeError("LLM returned weak or incomplete response")

    return output


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------

def generate_short_script(prompt: str) -> str:
    """
    GPU-first script generation with CPU fallback.
    Returns clean spoken text or raises a clear error.
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
    # 2️⃣ CPU FALLBACK
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
