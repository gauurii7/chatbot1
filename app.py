from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from difflib import get_close_matches
from deep_translator import GoogleTranslator

app = Flask(__name__)
CORS(app)

# ───────────────────────────────
# Load FAQ data
faq_data = pd.read_csv("faq.csv")
faq_data["Question"] = faq_data["Question"].str.lower()

# ───────────────────────────────
def translate_to_english(text, src_lang):
    """Translate user input from selected language to English."""
    try:
        if src_lang == "en":
            return text
        return GoogleTranslator(source=src_lang, target="en").translate(text)
    except Exception:
        return text

def translate_from_english(text, target_lang):
    """Translate English answer to user-selected language."""
    try:
        if target_lang == "en":
            return text
        return GoogleTranslator(source="en", target=target_lang).translate(text)
    except Exception:
        return text

# ───────────────────────────────
def find_answer(user_question):
    user_question = user_question.lower().strip()

    # Direct substring match
    for _, row in faq_data.iterrows():
        q = row["Question"].lower()
        if q in user_question or user_question in q:
            return row["Answer"]

    # Fuzzy match
    possible_questions = faq_data["Question"].tolist()
    closest = get_close_matches(user_question, possible_questions, n=1, cutoff=0.4)
    if closest:
        match = closest[0]
        return faq_data.loc[faq_data["Question"] == match, "Answer"].values[0]

    # Fallback
    return "Sorry, I couldn’t find an answer. Please contact parking support at contact number :0209776075 will contact you shortly  "

# ───────────────────────────────
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message", "")
    user_lang = data.get("language", "en")

    translated_text = translate_to_english(user_message, user_lang)
    answer_en = find_answer(translated_text)
    reply_translated = translate_from_english(answer_en, user_lang)

    return jsonify({
        "reply": reply_translated,
        "language": user_lang
    })

# ───────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return "🚗 Parking Chatbot API (Manual language selection: English, Hindi, Marathi)"

# ───────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
