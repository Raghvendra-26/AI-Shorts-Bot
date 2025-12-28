# src/ollama_llm.py
import subprocess
import os
import time

OLLAMA_PATH = r"C:\Users\rsr26\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_MODEL = "llama3.1:8b"

# Hard safety limits
OLLAMA_TIMEOUT = 120  # seconds
OLLAMA_RETRIES = 2


def generate_short_script(topic: str) -> str:
    if not topic or not topic.strip():
        raise RuntimeError("Empty topic passed to LLM")

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
- End with ONE short CTA

OUTPUT:
Return ONLY the spoken words.
NOTHING ELSE.
""".strip()

    # 🔒 FORCE CPU (prevents CUDA crash)
    env = os.environ.copy()
    env["OLLAMA_NO_CUDA"] = "1"

    last_error = None

    for attempt in range(1, OLLAMA_RETRIES + 1):
        try:
            result = subprocess.run(
                [OLLAMA_PATH, "run", OLLAMA_MODEL],
                input=prompt,
                text=True,
                capture_output=True,
                encoding="utf-8",
                errors="ignore",
                timeout=OLLAMA_TIMEOUT,
                env=env,
            )

            if result.returncode != 0:
                raise RuntimeError(result.stderr.strip() or "Ollama failed")

            output = result.stdout.strip()

            if not output or len(output.split()) < 30:
                raise RuntimeError("LLM returned empty or weak response")

            return output

        except subprocess.TimeoutExpired:
            last_error = "Ollama timed out"
        except Exception as e:
            last_error = str(e)

        print(f"⚠️ Ollama attempt {attempt} failed: {last_error}")
        time.sleep(2)

    raise RuntimeError(f"Ollama failed after {OLLAMA_RETRIES} attempts: {last_error}")
