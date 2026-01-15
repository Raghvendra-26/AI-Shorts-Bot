import re
from src.ollama_llm import generate_short_script
from src.utils.logger import logger
from yt_analytics.prompt_context import build_prompt_with_insights


HOOK_KEYWORDS = {
    "why", "secret", "truth", "mistake",
    "nobody", "never", "stop", "this",
    "you", "they", "real", "hidden"
}

EMOTION_WORDS = {
    "secret", "mistake", "truth", "dangerous", "destroy",
    "powerful", "addicted", "obsessed", "insane", "monster",
    "hidden", "nobody", "never", "stop", "ruining", "changed"
}

QUESTION_WORDS = {"why", "how", "what"}

# ---------------- BASIC UTILS ---------------- #

def split_sentences(text: str):
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

# ---------------- META LANGUAGE ---------------- #

META_PATTERNS = [
    r"^here('?s| is) (a )?(short|spoken)? ?script",
    r"^as requested",
    r"^sure[,!\- ]*",
    r"^this (short|script|video) (will|is going to)",
]

def contains_meta_language(script: str) -> bool:
    lines = script.strip().splitlines()
    for line in lines[:2]:  # only check first 2 lines
        lowered = line.lower()
        if any(re.search(p, lowered) for p in META_PATTERNS):
            return True
    return False

def remove_meta_language(script: str) -> str:
    lines = script.strip().splitlines()
    cleaned = []
    for line in lines:
        lowered = line.lower()
        if any(re.search(p, lowered) for p in META_PATTERNS):
            continue
        cleaned.append(line)
    return " ".join(cleaned).strip()

# ---------------- SCORING ---------------- #

def score_script(script: str) -> dict:
    sentences = split_sentences(script)
    words = script.split()

    word_count = len(words)
    avg_sentence_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    hook = extract_hook(script)
    hook_score = score_hook(hook)

    score = 0

    # 🎯 Ideal word range: 130–145
    if 130 <= word_count <= 145:
        score += 40
    else:
        score += max(0, 40 - abs(word_count - 138) * 0.8)

    # Sentence brevity
    score += max(20 - avg_sentence_len, 0) * 2

    # Hook quality
    score += hook_score

    return {
        "total": round(score, 2),
        "word_count": word_count,
        "avg_sentence_len": round(avg_sentence_len, 2),
        "hook_score": hook_score
    }

# ---------------- SCRIPT GENERATION ---------------- #

def generate_multiple_scripts(prompt: str, n=2):
    """Generate fewer scripts to avoid CUDA crashes"""

    # 🔹 Analytics-aware prompt enrichment (SAFE)
    enriched_prompt = build_prompt_with_insights(prompt)

    scripts = []
    for _ in range(n):
        try:
            s = generate_short_script(enriched_prompt)
            if s:
                scripts.append(s)
        except Exception as e:
            logger.warning(f"⚠️ Script generation failed: {e}")
    return scripts


def select_best_script(scripts: list):
    scored = []

    for s in scripts:
        if not s:
            continue

        if contains_meta_language(s):
            s = remove_meta_language(s)

        if len(s.split()) < 60:
            continue

        scored.append((score_script(s), s))

    if not scored:
        logger.warning("⚠️ All scripts weak — falling back to best raw script")
        return max(scripts, key=lambda x: len(x.split()) if x else 0)

    scored.sort(key=lambda x: x[0]["total"], reverse=True)

    best_score, best_script = scored[0]
    logger.info(f"🏆 Selected script score: {best_score}")
    return best_script

# ---------------- HOOK HANDLING ---------------- #

def extract_hook(script: str) -> str:
    return split_sentences(script)[0] if script else ""

def replace_hook(script: str, new_hook: str) -> str:
    sentences = split_sentences(script)
    sentences[0] = new_hook
    return ". ".join(sentences) + "."

def score_hook(hook: str) -> int:
    if not hook:
        return 0

    words = hook.lower().split()
    score = 0

    # 1️⃣ Brevity
    if len(words) <= 8:
        score += 30
    elif len(words) <= 12:
        score += 15

    # 2️⃣ Curiosity gap
    if "?" in hook:
        score += 20
    if any(w in QUESTION_WORDS for w in words):
        score += 15

    # 3️⃣ Direct address
    if any(w in {"you", "your"} for w in words):
        score += 15

    # 4️⃣ Emotional words
    score += min(sum(1 for w in words if w in EMOTION_WORDS) * 5, 20)

    # 5️⃣ Specificity
    if re.search(r"\d", hook):
        score += 10

    return min(score, 100)

def regenerate_hook(script: str, topic: str, max_attempts=3):
    original_script = script

    try:
        hook = extract_hook(script)

        for i in range(max_attempts):
            if score_hook(hook) >= 80:
                return script

            logger.info(f"🔁 Improving hook (attempt {i+1})")

            prompt = f"""
Rewrite ONLY the first sentence to be a viral hook.

Topic:
{topic}

Rules:
- Max 10 words
- Spoken dialogue
- Curiosity driven
- No emojis
- Return ONLY the hook
"""

            new_hook = generate_short_script(prompt).strip()

            if not new_hook or len(new_hook.split()) < 3:
                continue

            script = replace_hook(script, new_hook)
            hook = new_hook

        return script

    except Exception as e:
        logger.warning(f"⚠️ Hook regeneration failed: {e}")
        return original_script

# ---------------- SENTENCE REWRITE ---------------- #

def rewrite_long_sentences(script: str, max_words=10):
    sentences = split_sentences(script)
    long_sentences = [s for s in sentences if len(s.split()) > max_words]

    if not long_sentences:
        return script

    prompt = f"""
Rewrite each sentence to be at most {max_words} words.
Same meaning. Spoken dialogue.

Return rewritten sentences line by line.

Sentences:
""" + "\n".join(long_sentences)

    try:
        rewritten = generate_short_script(prompt).splitlines()
        mapping = dict(zip(long_sentences, rewritten))
    except Exception as e:
        logger.warning(f"⚠️ Sentence rewrite skipped: {e}")
        return script

    improved = [mapping.get(s, s) for s in sentences]
    return ". ".join(improved) + "."
