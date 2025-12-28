import re
from src.ollama_llm import generate_short_script

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

QUESTION_WORDS = {"why","how","what"}

# ---------------- BASIC UTILS ---------------- #

def split_sentences(text: str):
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]

# ---------------- SCORING ---------------- #

def score_script(script: str) -> dict:
    sentences = split_sentences(script)
    words = script.split()

    word_count = len(words)
    avg_sentence_len = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)

    hook = extract_hook(script)
    hook_score = score_hook(hook)


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
    if not hook:
        return 0

    words = hook.lower().split()
    score = 0

    # 1️⃣ Brevity (hooks must be tight)
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

    # 4️⃣ Emotional / power words
    score += min(
        sum(1 for w in words if w in EMOTION_WORDS) * 5,
        20
    )

    # 5️⃣ Specificity (numbers, years)
    if re.search(r"\d", hook):
        score += 10

    return min(score, 100)

def regenerate_hook(script: str, topic: str, max_attempts=1):
    hook = extract_hook(script)

    # 🔒 Accept good hooks — no LLM calls
    if score_hook(hook) >= 70:
        return script

    for i in range(max_attempts):
        print(f"🔁 Improving hook (attempt {i+1})")

        prompt = f"""
Rewrite ONLY the first line for virality.

Topic:
{topic}

Rules:
- Max 10 words
- Spoken dialogue
- Curiosity driven
- NO emojis
- Return ONLY the hook
"""

        try:
            new_hook = generate_short_script(prompt).strip()
            if not new_hook or len(new_hook.split()) < 3:
                raise ValueError("Weak hook")

            script = replace_hook(script, new_hook)
            return script  # ✅ STOP after first success

        except Exception as e:
            print(f"⚠️ Hook regeneration failed: {e}")
            return script  # 🔥 FAIL-SAFE

    return script


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
