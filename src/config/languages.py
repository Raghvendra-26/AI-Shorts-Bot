from dataclasses import dataclass
import random


@dataclass(frozen=True)
class LanguageConfig:
    code: str
    name: str
    voices: list[str]


LANGUAGES = {
    "en": LanguageConfig(
        code="en",
        name="English",
        voices=[
            "en-US-GuyNeural",
            "en-US-DavisNeural",
            "en-GB-RyanNeural",
            "en-IN-PrabhatNeural",
        ],
    ),
    "hi": LanguageConfig(
        code="hi",
        name="Hindi",
        voices=[
            "hi-IN-MadhurNeural",
            "hi-IN-SwaraNeural",
        ],
    ),
}


def get_random_voice(lang: str) -> str:
    """
    Returns a random voice for the given language.
    Defaults to English if lang is unknown.
    """
    config = LANGUAGES.get(lang, LANGUAGES["en"])
    return random.choice(config.voices)
