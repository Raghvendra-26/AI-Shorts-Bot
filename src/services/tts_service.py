from src.config.languages import get_random_voice
from src.tts_edge import text_to_speech
from src.text_utils import sanitize_for_tts


def speak(text: str, lang: str) -> str:
    voice = get_random_voice(lang)
    return text_to_speech(
        sanitize_for_tts(text),
        voice=voice
    )
