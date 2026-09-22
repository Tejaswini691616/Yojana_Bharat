# PATH: GovScheme/ai/text_to_speech.py
"""
TextToSpeechService abstraction (spec section 34). Mirrors
ai/speech_to_text.py: no provider wired in by default, never fakes audio,
and the app must fall back to showing text only (spec section 44) when
unavailable or when the response language has no configured voice.
"""
from config import Config


class TextToSpeechError(Exception):
    pass


class TextToSpeechService:
    def is_available_for(self, language: str) -> bool:
        raise NotImplementedError

    def synthesize(self, text: str, language: str) -> bytes:
        """Returns audio bytes, or raises TextToSpeechError."""
        raise NotImplementedError


class UnavailableTTSService(TextToSpeechService):
    def is_available_for(self, language: str) -> bool:
        return False

    def synthesize(self, text: str, language: str) -> bytes:
        raise TextToSpeechError(
            "No text-to-speech provider is configured (TTS_PROVIDER is empty in .env). "
            "The text response is still shown; audio playback is unavailable."
        )


def get_tts_service() -> TextToSpeechService:
    provider = Config.TTS_PROVIDER
    if not provider or not Config.TTS_API_KEY:
        return UnavailableTTSService()
    # Example wiring point:
    # if provider == "azure_speech":
    #     from ai.providers.azure_tts import AzureTTSService
    #     return AzureTTSService(api_key=Config.TTS_API_KEY)
    return UnavailableTTSService()
