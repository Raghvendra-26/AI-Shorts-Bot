import re

def sanitize_for_tts(text: str) -> str:
    """
    Minimal, SAFE cleaning for TTS.
    Never returns empty unless input is empty.
    """
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.replace("“", "").replace("”", "")
    text = text.replace("’", "'")

    # collapse spaces
    text = " ".join(text.split())

    return text.strip()


def clean_llm_script(text: str) -> str:
    # Remove common instruction leakage
    patterns = [
        r"^here'?s.*script.*?:",
        r"^write a.*script.*?:",
        r"^this video.*?:",
    ]

    lines = text.strip().splitlines()
    cleaned = []

    for line in lines:
        lower = line.lower()
        if any(re.match(p, lower) for p in patterns):
            continue
        cleaned.append(line)

    return " ".join(cleaned).strip()
