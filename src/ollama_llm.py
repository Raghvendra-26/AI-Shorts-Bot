# src/ollama_llm.py
import subprocess

OLLAMA_PATH = r"C:\Users\rsr26\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_MODEL = "llama3.1:8b"


def generate_short_script(topic: str) -> str:
    prompt = f"""
You are a professional YouTube Shorts scriptwriter.

TASK:
Write ONLY the spoken dialogue for a viral YouTube Shorts video.

TOPIC:
{topic}

STRICT RULES (VERY IMPORTANT):
- DO NOT say phrases like:
  "here's a script"
  "this video"
  "in this short"
  "30–45 seconds"
  "youtube shorts"
- DO NOT introduce the script
- DO NOT explain anything
- DO NOT use headings
- DO NOT use timestamps
- DO NOT use markdown
- DO NOT use emojis

STYLE:
- Spoken dialogue ONLY
- Conversational
- Short punchy sentences
- Strong hook in first line
- End with a CTA (like, comment, subscribe)

OUTPUT:
Return ONLY the spoken words.
NOTHING ELSE.
"""

    result = subprocess.run(
        [OLLAMA_PATH, "run", OLLAMA_MODEL],
        input=prompt,
        text=True,
        capture_output=True,
	encoding="utf-8",
	errors="ignore"
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    return result.stdout.strip()
