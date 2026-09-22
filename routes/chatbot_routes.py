# PATH: GovScheme/routes/chatbot_routes.py
from flask import Blueprint, request, jsonify, session, render_template

from models.user_model import get_user_by_id
from models.db import execute, query
from ai.chatbot import handle_message
from ai.language_service import get_supported_text_languages, voice_support_for
from ai.speech_to_text import get_stt_service, SpeechToTextError
from ai.text_to_speech import get_tts_service, TextToSpeechError
from config import Config

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/chatbot")
def chatbot_widget():
    return render_template("chatbot/chatbot.html", languages=get_supported_text_languages())


def _get_or_create_session(user_id, language):
    existing = query("SELECT * FROM chat_sessions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                      (user_id,)) if user_id else []
    if existing:
        return existing[0]["session_id"]
    return execute("INSERT INTO chat_sessions (user_id, language) VALUES (?, ?)", (user_id, language))


@chatbot_bp.route("/api/chat/message", methods=["POST"])
def chat_message():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    language = data.get("language", "English")
    if not message:
        return jsonify({"error": "Empty message"}), 400

    user_id = session.get("user_id")
    user_row = get_user_by_id(user_id) if user_id else None

    session_id = _get_or_create_session(user_id, language)
    execute("""INSERT INTO chat_messages (session_id, sender, message, language)
               VALUES (?, 'user', ?, ?)""", (session_id, message, language))

    result = handle_message(message, user_row, language)

    execute("""INSERT INTO chat_messages (session_id, sender, message, language, intent)
               VALUES (?, 'bot', ?, ?, ?)""",
            (session_id, result["reply"], language, result["intent"]))

    return jsonify({"reply": result["reply"], "intent": result["intent"]})


@chatbot_bp.route("/api/chat/languages")
def chat_languages():
    return jsonify({
        "text_languages": get_supported_text_languages(),
        "voice_supported": {
            lang: voice_support_for(lang, Config.STT_PROVIDER)
            for lang in get_supported_text_languages()
        },
    })


@chatbot_bp.route("/api/chat/voice-input", methods=["POST"])
def voice_input():
    """Accepts multipart audio, returns transcribed text (or a clear
    fallback message if no STT provider is configured - spec section 44)."""
    language = request.form.get("language", "English")
    audio_file = request.files.get("audio")
    if audio_file is None:
        return jsonify({"error": "No audio provided"}), 400

    stt = get_stt_service()
    if not stt.is_available():
        return jsonify({
            "error": "unavailable",
            "message": "Voice input isn't configured in this deployment. "
                       "Please continue using text chat.",
        }), 503

    try:
        text = stt.transcribe(audio_file.read(), language)
        return jsonify({"text": text})
    except SpeechToTextError as exc:
        return jsonify({
            "error": "transcription_failed",
            "message": "Sorry, I couldn't understand the audio. Please try again or type your question.",
            "detail": str(exc),
        }), 502


@chatbot_bp.route("/api/chat/voice-output", methods=["POST"])
def voice_output():
    """Returns audio bytes for a given text/language, or 503 with a clear
    fallback message so the UI keeps showing text (spec section 44)."""
    data = request.get_json(force=True) or {}
    text = data.get("text", "")
    language = data.get("language", "English")

    tts = get_tts_service()
    if not tts.is_available_for(language):
        return jsonify({
            "error": "unavailable",
            "message": f"Voice output isn't configured for {language} in this deployment. "
                       f"The text response above is still accurate.",
        }), 503

    try:
        audio_bytes = tts.synthesize(text, language)
        return audio_bytes, 200, {"Content-Type": "audio/mpeg"}
    except TextToSpeechError as exc:
        return jsonify({"error": "synthesis_failed", "detail": str(exc)}), 502
