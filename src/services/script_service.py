from src.config.prompts import SCRIPT_BODY_PROMPTS
from src.script_quality import (
    generate_multiple_scripts,
    select_best_script,
    regenerate_hook,
    rewrite_long_sentences
)
from src.text_utils import clean_llm_script, sanitize_spoken_script
from src.config.comment_bait import COMMENT_BAIT

import random


def generate_script(idea: str, lang: str) -> str:
    prompt = SCRIPT_BODY_PROMPTS[lang].format(idea=idea)

    scripts = generate_multiple_scripts(prompt, n=2)
    script = select_best_script(scripts)

    script = regenerate_hook(script, idea)
    script = rewrite_long_sentences(script)

    cleaned = sanitize_spoken_script(clean_llm_script(script))
    final_script = cleaned if cleaned.strip() else script

    # ---------------- COMMENT-BAIT INJECTION ---------------- #
    bait = random.choice(COMMENT_BAIT.get(lang, COMMENT_BAIT["en"]))
    final_script = final_script.rstrip(". ") + ". " + bait

    return final_script
