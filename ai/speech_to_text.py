# PATH: GovScheme/ai/speech_to_text.py
"""
SpeechToTextService abstraction (spec section 33).

No provider is wired in by default. This keeps the core project runnable
without any paid API and without ever faking a transcription. To add a
real provider (e.g. Azure Speech, Google Cloud Speech, Whisper API):
    1. Implement a subclass with a working `transcribe()`.
    2. Register it in `get_stt_service()` below.
    3. Set STT_PROVIDER / STT_API_KEY in .env.
Never hardcode API keys in this file - always read from Config.
"""
from config import Config


class SpeechToTextService:
    def is_available(self) -> bool:
        raise NotImplementedError

    def transcribe(self, audio_bytes: bytes, language: str) -> str:
        """Returns transcribed text, or raises SpeechToTextError."""
        raise NotImplementedError


class SpeechToTextError(Exception):
    pass


class UnavailableSTTService(SpeechToTextService):
    """Used whenever no STT provider is configured. Text chat still works;
    the UI must show: "Sorry, I couldn't understand the audio. Please try
    again or type your question." per spec section 44."""

    def is_available(self) -> bool:
        return False

    def transcribe(self, audio_bytes: bytes, language: str) -> str:
        raise SpeechToTextError(
            "No speech-to-text provider is configured (STT_PROVIDER is empty in .env). "
            "Use text chat instead, or configure a provider."
        )


def get_stt_service() -> SpeechToTextService:
    provider = Config.STT_PROVIDER
    if not provider or not Config.STT_API_KEY:
        return UnavailableSTTService()
    # Example wiring point for a real provider:
    # if provider == "azure_speech":
    #     from ai.providers.azure_stt import AzureSTTService
    #     return AzureSTTService(api_key=Config.STT_API_KEY)
    return UnavailableSTTService()
