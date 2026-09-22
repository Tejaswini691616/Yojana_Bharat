# PATH: GovScheme/ai/response_generator.py
"""
Builds chatbot response TEXT from real data (scheme DB, eligibility engine,
recommendation service). Never invents scheme facts (spec section 40/47).

Multilingual note (honesty, spec section 28/29): the underlying scheme
dataset (names, descriptions, criteria) is only available in English in
the source Excel workbook. We translate the surrounding UI phrases
("Here are your recommended schemes:", "Why recommended:", etc.) into the
selected language using the PHRASES dictionary below. Scheme names and
data fields stay in English with a one-line note, rather than silently
mistranslating factual government-scheme content with no verified
translation source. This is a deliberate, disclosed limitation - not a bug.
"""

PHRASES = {
    "English": {
        "recommended_header": "Here are your top recommended schemes:",
        "why_recommended": "Why recommended:",
        "no_recommendations": "I couldn't find any schemes you're potentially eligible for right now based on your profile.",
        "eligible_yes": "Based on the configured prototype criteria, you appear potentially eligible for {scheme}.",
        "eligible_no": "Based on the configured prototype criteria, you do not currently appear eligible for {scheme}.",
        "not_found": "I couldn't find that scheme in the SmartGov AI database.",
        "disclaimer": "This is a prototype assessment, not an official government decision. Please verify with the official source before applying.",
        "missing_profile": "I need a bit more profile information to answer that. Please complete your profile.",
        "data_note": "(Scheme details are shown in English as sourced from the official dataset.)",
    },
    "Hindi": {
        "recommended_header": "आपके लिए अनुशंसित योजनाएं:",
        "why_recommended": "अनुशंसा का कारण:",
        "no_recommendations": "आपकी प्रोफ़ाइल के आधार पर फिलहाल कोई योजना नहीं मिली जिसके लिए आप संभावित रूप से पात्र हों।",
        "eligible_yes": "कॉन्फ़िगर किए गए प्रोटोटाइप मानदंडों के अनुसार, आप {scheme} के लिए संभावित रूप से पात्र प्रतीत होते हैं।",
        "eligible_no": "कॉन्फ़िगर किए गए प्रोटोटाइप मानदंडों के अनुसार, आप वर्तमान में {scheme} के लिए पात्र नहीं दिखते।",
        "not_found": "यह योजना SmartGov AI डेटाबेस में नहीं मिली।",
        "disclaimer": "यह एक प्रोटोटाइप मूल्यांकन है, आधिकारिक सरकारी निर्णय नहीं। कृपया आवेदन करने से पहले आधिकारिक स्रोत से पुष्टि करें।",
        "missing_profile": "इसका उत्तर देने के लिए मुझे थोड़ी और प्रोफ़ाइल जानकारी चाहिए। कृपया अपनी प्रोफ़ाइल पूरी करें।",
        "data_note": "(योजना विवरण आधिकारिक डेटासेट के अनुसार अंग्रेज़ी में दिखाए गए हैं।)",
    },
}

FALLBACK_NOTE = "(This language's chat interface phrases are not yet fully translated in this prototype; showing English text.)"


def _phrases(language: str) -> dict:
    return PHRASES.get(language, PHRASES["English"])


def render_recommendations(recommendations: list, language: str = "English") -> str:
    p = _phrases(language)
    if not recommendations:
        return p["no_recommendations"]

    lines = [p["recommended_header"], ""]
    for i, rec in enumerate(recommendations, start=1):
        scheme = rec["scheme"]
        result = rec["result"]
        lines.append(f"{i}. {scheme['scheme_name']} (Model Relevance Score: {rec['relevance_score']}%)")
        if result.matched:
            lines.append(f"   {p['why_recommended']}")
            for m in result.matched:
                lines.append(f"   ✓ {m}")
        lines.append("")
    lines.append(p["disclaimer"])
    if language != "English":
        lines.append(p["data_note"])
    return "\n".join(lines)


def render_eligibility(scheme_name: str, result, language: str = "English") -> str:
    p = _phrases(language)
    lines = []
    if result.is_eligible:
        lines.append(p["eligible_yes"].format(scheme=scheme_name))
    else:
        lines.append(p["eligible_no"].format(scheme=scheme_name))
    lines.append("")
    lines.append(result.explanation_text())
    lines.append("")
    lines.append(p["disclaimer"])
    return "\n".join(lines)


def render_scheme_details(scheme: dict, language: str = "English") -> str:
    p = _phrases(language)
    lines = [
        f"**{scheme['scheme_name']}**",
        f"Category: {scheme.get('category') or 'N/A'}",
        f"Eligibility criteria: {scheme.get('eligibility') or 'Not specified in dataset.'}",
        f"Official link: {scheme.get('official_link') or 'Official link not available in current dataset.'}",
        "",
        p["disclaimer"],
    ]
    if language != "English":
        lines.append(p["data_note"])
    return "\n".join(lines)


def not_found_message(language: str = "English") -> str:
    return _phrases(language)["not_found"]


def missing_profile_message(language: str = "English") -> str:
    return _phrases(language)["missing_profile"]
