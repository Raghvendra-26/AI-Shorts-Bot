from src.text_utils import sanitize_for_captions, write_captions

raw = """That's why short videos feel addictive!
Swipe. Reward. Repeat.
Subscribe for more."""
safe = sanitize_for_captions(raw)

write_captions(safe)
print(safe)
