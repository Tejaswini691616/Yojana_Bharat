# PATH: GovScheme/ai/language_service.py
"""
Language configuration for the chatbot.

IMPORTANT (spec section 28): we do NOT claim STT/TTS support for a
language unless a configured provider actually supports it. Text chat
uses hand-written response templates per language (see
ai/response_generator.py), which is honest and always works offline.
Voice (STT/TTS) support is reported separately via voice_support_for()
and depends entirely on what STT_PROVIDER/TTS_PROVIDER is configured in
.env - if none is configured, voice is disabled and the UI must say so,
while text chat keeps working in all listed languages.
"""

SUPPORTED_TEXT_LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Punjabi": "pa",
    "Odia": "or",
    "Assamese": "as",
}

# Providers and their ACTUALLY verified language codes go here. This dict is
# intentionally empty by default (no provider configured) so the app never
# fakes voice support. Fill this in only after confirming your chosen
# STT/TTS provider's documented language coverage.
PROVIDER_VOICE_LANGUAGES = {
    # "azure_speech": {"English": "en-US", "Hindi": "hi-IN", ...},
}


def get_supported_text_languages():
    return list(SUPPORTED_TEXT_LANGUAGES.keys())


def is_text_language_supported(language: str) -> bool:
    return language in SUPPORTED_TEXT_LANGUAGES


def voice_support_for(language: str, provider: str) -> bool:
    """Returns True only if `provider` has a verified language code for
    `language`. With no provider configured, always returns False."""
    if not provider:
        return False
    codes = PROVIDER_VOICE_LANGUAGES.get(provider, {})
    return language in codes


def detect_language_hint(text: str) -> str:
    """Very small heuristic script-range detector for auto-detect UX.
    This is NOT a substitute for manual language selection (spec 31)."""
    ranges = {
        "Hindi": (0x0900, 0x097F), "Bengali": (0x0980, 0x09FF),
        "Tamil": (0x0B80, 0x0BFF), "Telugu": (0x0C00, 0x0C7F),
        "Gujarati": (0x0A80, 0x0AFF), "Kannada": (0x0C80, 0x0CFF),
        "Malayalam": (0x0D00, 0x0D7F), "Punjabi": (0x0A00, 0x0A7F),
        "Odia": (0x0B00, 0x0B7F), "Assamese": (0x0980, 0x09FF),
    }
    for lang, (lo, hi) in ranges.items():
        if any(lo <= ord(ch) <= hi for ch in text):
            return lang
    return "English"
