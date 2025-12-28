import re
from src.ollama_llm import generate_short_script

HOOK_KEYWORDS = {
    "why", "secret", "truth", "mistake",
    "nobody", "never", "stop", "this",
    "you", "they", "real", "hidden"
}

# ---------------- BASIC UTILS ---------------- #

def split_sentences(text: str):
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

# ---------------- SCORING ---------------- #

def score_script(script: str) -> dict:
    sentences = split_sentences(script)
    words = script.split()

    word_count = len(words)
    avg_sentence_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    hook_words = words[:10]
    hook_score = sum(1 for w in hook_words if w.lower() in HOOK_KEYWORDS) * 10
    hook_score = min(hook_score, 50)

    score = 0
    score += min(word_count / 120 * 40, 40)
    score += max(20 - avg_sentence_len, 0) * 2
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
    scripts = []
    for _ in range(n):
        try:
            s = generate_short_script(prompt)
            if s:
                scripts.append(s)
        except Exception as e:
            print(f"⚠️ Script generation failed: {e}")
    return scripts

def select_best_script(scripts: list):
    scored = [(score_script(s), s) for s in scripts if s.strip()]
    scored.sort(key=lambda x: x[0]["total"], reverse=True)

    best_score, best_script = scored[0]
    print(f"🏆 Selected script score: {best_score}")
    return best_script

# ---------------- HOOK HANDLING ---------------- #

def extract_hook(script: str) -> str:
    return split_sentences(script)[0]

def replace_hook(script: str, new_hook: str) -> str:
    sentences = split_sentences(script)
    sentences[0] = new_hook
    return ". ".join(sentences) + "."

def score_hook(hook: str) -> int:
    words = hook.lower().split()
    score = 0
    if len(words) <= 10:
        score += 40
    if any(w in HOOK_KEYWORDS for w in words):
        score += 60
    return score

def regenerate_hook(script: str, topic: str):
    """Single-attempt hook regeneration (FAIL-SAFE)"""
    hook = extract_hook(script)

    if score_hook(hook) >= 80:
        return script

    prompt = f"""
Rewrite ONLY the first line for virality.

Topic:
{topic}

Rules:
- Max 10 words
- Spoken dialogue
- Curiosity driven
- Return ONLY the hook
"""

    try:
        new_hook = generate_short_script(prompt).strip()
        if new_hook and len(new_hook.split()) >= 3:
            return replace_hook(script, new_hook)
    except Exception as e:
        print(f"⚠️ Hook regeneration skipped: {e}")

    return script  # SAFE FALLBACK

# ---------------- SENTENCE REWRITE (BATCH) ---------------- #

def rewrite_long_sentences(script: str, max_words=10):
    sentences = split_sentences(script)
    long_sentences = [s for s in sentences if len(s.split()) > max_words]

    if not long_sentences:
        return script

    prompt = f"""
Rewrite each sentence to be max {max_words} words.
Same meaning. Spoken dialogue.

Return rewritten sentences line by line.

Sentences:
""" + "\n".join(long_sentences)

    try:
        rewritten = generate_short_script(prompt).splitlines()
        mapping = dict(zip(long_sentences, rewritten))
    except Exception as e:
        print(f"⚠️ Sentence rewrite skipped: {e}")
        return script

    improved = [mapping.get(s, s) for s in sentences]
    return ". ".join(improved) + "."
