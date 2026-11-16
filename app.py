import json
from flask import Flask, request, jsonify, render_template

import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- ধাপ ১: NLTK এর stopwords ডাউনলোড (প্রথমবার একবার) ----------
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

app = Flask(__name__)

tokenizer = RegexpTokenizer(r"[a-z0-9]+")   # শুধু শব্দ ও সংখ্যা রাখে
stemmer = PorterStemmer()                   # shipping, shipped -> ship
stop_words = set(stopwords.words("english"))  # is, the, a, how ... বাদ দেওয়ার জন্য


# ---------- ধাপ ২: টেক্সট প্রিপ্রসেসিং ----------
def preprocess(text):
    text = text.lower()                       # ছোট হাতের অক্ষর
    tokens = tokenizer.tokenize(text)         # টোকেনাইজ + চিহ্ন (?, !) বাদ
    tokens = [stemmer.stem(t) for t in tokens if t not in stop_words]
    return " ".join(tokens)


# ---------- ধাপ ৩: FAQ লোড ও TF-IDF ভেক্টর তৈরি ----------
with open("faqs.json", encoding="utf-8") as f:
    faqs = json.load(f)

processed_questions = [preprocess(item["question"]) for item in faqs]
vectorizer = TfidfVectorizer()
faq_vectors = vectorizer.fit_transform(processed_questions)

GREETINGS = {"hi", "hello", "hey", "hola", "salam", "assalamualaikum"}
THANKS = {"thanks", "thank", "thankyou", "bye", "goodbye"}
THRESHOLD = 0.25   # এর কম মিল হলে বট বলবে "বুঝতে পারিনি"


# ---------- ধাপ ৪: সবচেয়ে মিল থাকা উত্তর বের করা ----------
def get_answer(user_message):
    words = set(user_message.lower().replace("!", " ").replace(".", " ").split())

    if words & GREETINGS:
        return "Hello! 👋 I am Riya assistant. Ask me about orders, delivery, payment or returns.", None, 1.0
    if words & THANKS:
        return "You're welcome! 😊 Have a great day!", None, 1.0

    cleaned = preprocess(user_message)
    if not cleaned:
        return "Please ask a question about our shop.", None, 0.0

    user_vector = vectorizer.transform([cleaned])
    scores = cosine_similarity(user_vector, faq_vectors)[0]
    best = int(scores.argmax())
    best_score = float(scores[best])

    if best_score < THRESHOLD:
        return ("Sorry, I could not understand that. 😕 Try asking about delivery, "
                "payment, return or refund. Or email support@Riya.com"), None, best_score

    return faqs[best]["answer"], faqs[best]["question"], best_score


# ---------- Flask রুট ----------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    message = request.get_json().get("message", "").strip()
    answer, matched, score = get_answer(message)
    return jsonify({"answer": answer, "matched": matched, "score": round(score, 2)})


if __name__ == "__main__":
    app.run(debug=True)