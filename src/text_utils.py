import re


# ---------------- TTS SANITIZATION ---------------- #

def sanitize_for_tts(text: str) -> str:
    """
    Minimal, SAFE cleaning for TTS.
    Never returns empty unless input is empty.
    """
    if not text or not text.strip():
        return ""

    text = text.replace("\n", " ")
    text = text.replace("“", "").replace("”", "")
    text = text.replace("’", "'")

    # collapse multiple spaces
    text = " ".join(text.split())

    return text.strip()


# ---------------- LLM CLEANUP ---------------- #

def clean_llm_script(text: str) -> str:
    """
    Removes obvious instruction / narrator leakage from LLM output.
    This runs BEFORE deeper spoken sanitization.
    """
    if not text:
        return ""

    patterns = [
        r"^here'?s.*script",
        r"^here is.*script",
        r"^write a.*script",
        r"^this video",
        r"^in this video",
        r"^youtube shorts",
        r"^30[-–]?45 second",
        r"^spoken script",
    ]

    lines = text.strip().splitlines()
    cleaned = []

    for line in lines:
        lower = line.lower().strip()
        if any(re.search(p, lower) for p in patterns):
            continue
        cleaned.append(line)

    return " ".join(cleaned).strip()


# ---------------- SPOKEN SCRIPT SANITIZER (CRITICAL) ---------------- #

def sanitize_spoken_script(script: str) -> str:
    """
    Final safety layer.
    Ensures the script sounds like natural speech, not a list or explanation.
    """
    if not script:
        return ""

    lines = script.splitlines()
    cleaned = []

    for line in lines:
        line = line.strip()

        # 🚫 Drop meta / explanation phrases
        if re.search(
            r"(here are|rewritten|sentences|points|following|example|script)",
            line,
            re.I,
        ):
            continue

        # 🚫 Drop pure numbering lines (e.g. "1", "2", "3")
        if re.fullmatch(r"\d+", line):
            continue

        # 🚫 Remove numbered prefixes like "1. ", "2) ", "3 - "
        line = re.sub(r"^\d+\s*[\.\)\-:]\s*", "", line)

        # 🚫 Remove accidental list-style starts
        line = re.sub(r"^(first|second|third|next|finally)\s+", "", line, flags=re.I)

        if line:
            cleaned.append(line)

    # Rejoin into natural spoken paragraph
    final = " ".join(cleaned)
    final = re.sub(r"\s+", " ", final).strip()

    return final
