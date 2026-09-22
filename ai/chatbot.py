# PATH: GovScheme/ai/chatbot.py
"""
Chatbot orchestrator (spec sections 27, 36-41).

Architecture implemented here (RAG-style, spec section 41):
    User Question -> classify_intent() -> Retrieval (DB / eligibility
    engine / recommendation service) -> response_generator (grounded text)
    -> optional ChatModelService polish -> Response

The chatbot NEVER invents scheme facts, eligibility outcomes, application
numbers, or status. It always calls the same eligibility engine and the
same recommendation service used by the rest of the app (spec section 39).
"""
import re

from ai.intent_classifier import classify_intent
from ai.chat_model_service import get_chat_model_service
from ai.recommendation_model import get_recommendations, get_all_eligibility_results
from ai.response_generator import (render_recommendations, render_eligibility,
                                    render_scheme_details, not_found_message,
                                    missing_profile_message)
from models.scheme_model import get_all_schemes, search_schemes


def _find_scheme_in_message(message: str):
    text = message.lower()
    for scheme in get_all_schemes():
        name = scheme["scheme_name"].lower()
        # crude but effective for a fixed catalogue of 20 schemes
        if name in text or any(word in text for word in name.split() if len(word) > 4):
            return scheme
    return None


def handle_message(message: str, user_row: dict = None, language: str = "English") -> dict:
    """
    Returns {"reply": str, "intent": str}.
    user_row may be None for an anonymous/logged-out visitor - in that
    case eligibility/recommendation intents ask the user to log in.
    """
    intent = classify_intent(message)
    chat_model = get_chat_model_service()
    reply = None

    if intent in ("RECOMMENDATIONS", "WHY_RECOMMENDED"):
        if user_row is None:
            reply = "Please log in so I can check your profile against scheme criteria."
        else:
            recs = get_recommendations(user_row, top_k=5)
            reply = render_recommendations(recs, language)

    elif intent == "ELIGIBILITY":
        scheme = _find_scheme_in_message(message)
        if user_row is None:
            reply = "Please log in so I can check your eligibility against your profile."
        elif scheme is None:
            reply = "Which scheme would you like me to check? For example: 'Am I eligible for PM-KISAN?'"
        else:
            results = get_all_eligibility_results(user_row)
            match = next((r for s, r in results if s["scheme_id"] == scheme["scheme_id"]), None)
            reply = render_eligibility(scheme["scheme_name"], match, language) if match else not_found_message(language)

    elif intent == "SCHEME_DETAILS" or intent == "BENEFITS" or intent == "DOCUMENTS":
        scheme = _find_scheme_in_message(message)
        reply = render_scheme_details(scheme, language) if scheme else not_found_message(language)

    elif intent in ("FARMER_SCHEMES", "STUDENT_SCHEMES", "SENIOR_CITIZEN_SCHEMES",
                     "DISABILITY_SCHEMES", "WOMEN_SCHEMES", "HOUSING", "HEALTH", "EDUCATION"):
        keyword_map = {
            "FARMER_SCHEMES": "farmer", "STUDENT_SCHEMES": "student",
            "SENIOR_CITIZEN_SCHEMES": "senior", "DISABILITY_SCHEMES": "disab",
            "WOMEN_SCHEMES": "widow", "HOUSING": "housing", "HEALTH": "health",
            "EDUCATION": "education",
        }
        results = search_schemes(keyword=keyword_map[intent])
        if results:
            names = "\n".join(f"- {s['scheme_name']} ({s['category']})" for s in results[:10])
            reply = f"Schemes that may match:\n{names}"
        else:
            reply = "I couldn't find matching schemes in the SmartGov AI database for that category."

    elif intent == "SCHEME_SEARCH" or intent == "CATEGORY_SEARCH" or intent == "STATE_SEARCH":
        # naive keyword extraction: use content words after common stop phrases
        cleaned = re.sub(r"(find|search|look for|schemes?|in|for)", " ", message.lower())
        keyword = cleaned.strip()
        results = search_schemes(keyword=keyword) if keyword else get_all_schemes()
        if results:
            names = "\n".join(f"- {s['scheme_name']} ({s['category']})" for s in results[:10])
            reply = f"Here's what I found:\n{names}"
        else:
            reply = "I couldn't find any matching schemes in the SmartGov AI database."

    elif intent == "APPLICATION_STATUS":
        reply = "Please open the 'Applications' page to see the live status of your applications."

    elif intent == "APPLICATION_PROCESS":
        reply = ("To apply: open a scheme's details page and click 'Apply Now'. "
                 "SmartGov AI will create an application record and (in demo mode) "
                 "simulate the repetitive application steps. This is not a substitute "
                 "for the official government application where required.")

    elif intent == "SAVED_SCHEMES":
        reply = "Please open the 'Saved Schemes' page to see everything you've bookmarked."

    elif intent == "NEW_SCHEMES":
        reply = "Please check the Notifications page for newly discovered or updated schemes."

    else:
        reply = ("I can help with scheme eligibility, recommendations, scheme details, "
                 "documents required, and application status. Try asking things like "
                 "'What schemes do you recommend for me?' or 'Am I eligible for PM-KISAN?'")

    reply = chat_model.polish_response(reply, message, language)
    return {"reply": reply, "intent": intent}
