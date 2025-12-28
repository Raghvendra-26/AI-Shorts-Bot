# src/idea_generator.py

from src.ollama_llm import generate_short_script

def generate_idea(niche: str) -> str:
    prompt = f"""
Generate ONE viral YouTube Shorts IDEA for this niche:

{niche}

STRICT RULES:
- EXACTLY ONE LINE
- 6 to 10 words only
- Curiosity driven
- NO punctuation
- NO emojis
- NO CTA
- NO explanation
- NOT a script

Examples:
Bad: I tried Ronaldo's diet for 24 hours and this happened
Good: Footballers secretly eat junk food before matches

Return ONLY the idea text.
"""

    idea = generate_short_script(prompt)

    # HARD SAFETY
    idea = idea.split("\n")[0]
    idea = idea.strip()

    return idea
