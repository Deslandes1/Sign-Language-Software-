import streamlit as st
import base64
import tempfile
import os
from gtts import gTTS
from deep_translator import GoogleTranslator
import random

st.set_page_config(
    page_title="Sign Language Book – Gesner Deslandes",
    page_icon="🤟",
    layout="wide"
)

# ---------- Custom CSS ----------
st.markdown(
    """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .spinning-globe {
        animation: spin 4s linear infinite;
        font-size: 50px;
        text-align: center;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa, #e9ecef);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d4e0e9, #c0cfdf);
    }
    h1, h2, h3, p, div, span, label {
        color: #1e2a3a !important;
    }
    .stButton button {
        background-color: #4a90e2 !important;
        color: white !important;
        border-radius: 30px !important;
    }
    .chapter-box {
        background: white;
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .conversation {
        background: #f0f4f8;
        border-left: 5px solid #4a90e2;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 15px;
    }
    .vocab-word {
        background: #fff3e0;
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.5rem;
        border-radius: 50px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Session state ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "language" not in st.session_state:
    st.session_state.language = "en"
if "chapter" not in st.session_state:
    st.session_state.chapter = 1
if "translations" not in st.session_state:
    st.session_state.translations = {}
if "audio_cache" not in st.session_state:
    st.session_state.audio_cache = {}

# ---------- Language mapping for deep_translator ----------
LANG_CODES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "Haitian Creole": "ht"
}

# ---------- Translation helper (cached) ----------
def translate_text(text, target_lang):
    if target_lang == "en":
        return text
    cache_key = f"{text}_{target_lang}"
    if cache_key in st.session_state.translations:
        return st.session_state.translations[cache_key]
    try:
        translated = GoogleTranslator(source='en', target=target_lang).translate(text)
        st.session_state.translations[cache_key] = translated
        return translated
    except Exception as e:
        st.warning(f"Translation error: {e}")
        return text

# ---------- Text-to-speech helper (cached) ----------
def text_to_speech(text, lang_code):
    if not text:
        return ""
    cache_key = f"{text}_{lang_code}"
    if cache_key in st.session_state.audio_cache:
        return st.session_state.audio_cache[cache_key]
    try:
        tts = gTTS(text=text, lang=lang_code)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            with open(f.name, "rb") as audio_file:
                audio_bytes = audio_file.read()
            os.unlink(f.name)
        b64 = base64.b64encode(audio_bytes).decode()
        html = f'<audio controls src="data:audio/mp3;base64,{b64}" style="width:100%; margin-top:0.5rem;"></audio>'
        st.session_state.audio_cache[cache_key] = html
        return html
    except Exception as e:
        return f"<p>Audio error: {e}</p>"

# ---------- Generate content for 20 chapters (master in English) ----------
def generate_chapter(ch_num):
    # Each chapter has dynamic content based on chapter number
    base_greeting = f"Chapter {ch_num}: Everyday Signs"
    convs = []
    for i in range(1, 4):
        convs.append({
            "title": f"Conversation {i}: Meeting someone",
            "lines": [
                f"Person A: Hello! What is your name? (Chapter {ch_num})",
                "Person B: My name is Alex. Nice to meet you.",
                "Person A: Nice to meet you too. How are you?",
                "Person B: I am fine, thank you."
            ]
        })
    vocab = [
        {"word": "hello", "sign_desc": "👋 Wave hand near temple"},
        {"word": "name", "sign_desc": "✋ Tap fingers on chin"},
        {"word": "nice", "sign_desc": "👍 Thumbs up with smile"},
        {"word": "meet", "sign_desc": "🤝 Bring index fingers together"},
        {"word": "fine", "sign_desc": "👌 OK sign near chest"}
    ]
    grammar = "In sign language, word order is often Subject-Object-Verb. Facial expressions convey tone."
    quiz = [
        {"question": "What is the sign for 'hello'?", "options": ["👋 Wave", "✌️ Peace sign", "👍 Thumbs up"], "answer": "👋 Wave"},
        {"question": "True or False: Sign language is universal.", "options": ["True", "False"], "answer": "False"},
        {"question": "Which hand shape means 'name'?", "options": ["✋ Tap chin", "👌 OK sign", "✊ Fist"], "answer": "✋ Tap chin"}
    ]
    return {
        "title": base_greeting,
        "conversations": convs,
        "vocabulary": vocab,
        "grammar": grammar,
        "quiz": quiz
    }

# ---------- Login page ----------
def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div class="spinning-globe">🌍</div>', unsafe_allow_html=True)
        st.title("🤟 Sign Language Book")
        st.markdown("### Learn Sign Language with AI Audio")
        st.markdown("Built by **Gesner Deslandes**")
        st.markdown("---")
        password = st.text_input("Enter password", type="password")
        if st.button("Unlock Book"):
            if password == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password. Try again.")

# ---------- Main app ----------
def main_app():
    with st.sidebar:
        st.markdown('<div class="spinning-globe">🌐</div>', unsafe_allow_html=True)
        st.markdown("### GlobalInternet.py")
        st.markdown("**Gesner Deslandes** – Software Engineer")
        st.markdown("[🌍 Website](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
        st.markdown("📧 deslandes78@gmail.com")
        st.markdown("📞 (509) 4738-5663")
        st.markdown("---")
        lang_display = st.selectbox("🌐 Language", list(LANG_CODES.keys()), index=0)
        new_lang = LANG_CODES[lang_display]
        if new_lang != st.session_state.language:
            st.session_state.language = new_lang
            st.session_state.translations = {}  # clear cache
            st.rerun()
        st.markdown("---")
        chapter_num = st.selectbox("📖 Select Chapter", list(range(1, 21)), index=st.session_state.chapter-1)
        st.session_state.chapter = chapter_num
        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.translations = {}
            st.session_state.audio_cache = {}
            st.rerun()

    # Main page header
    st.markdown("# 🤟 Sign Language Book Software")
    st.markdown("### Built by **Gesner Deslandes**")
    st.markdown("---")

    # Load current chapter content
    ch_data = generate_chapter(st.session_state.chapter)
    ch_title = translate_text(ch_data["title"], st.session_state.language)

    col1, col2 = st.columns([4,1])
    with col1:
        st.subheader(ch_title)
    with col2:
        if st.button(f"🔊 Read {st.session_state.chapter}"):
            audio_html = text_to_speech(ch_title, st.session_state.language)
            st.markdown(audio_html, unsafe_allow_html=True)

    st.markdown("---")

    # ---------- Conversations ----------
    st.markdown("## 💬 Conversations")
    for idx, conv in enumerate(ch_data["conversations"]):
        with st.expander(f"🗣️ {translate_text(conv['title'], st.session_state.language)}"):
            for line in conv["lines"]:
                st.markdown(f"- {translate_text(line, st.session_state.language)}")
            full_text = " ".join(conv["lines"])
            full_text_translated = translate_text(full_text, st.session_state.language)
            if st.button(f"🔊 Play Conversation {idx+1}", key=f"conv_audio_{st.session_state.chapter}_{idx}"):
                audio_html = text_to_speech(full_text_translated, st.session_state.language)
                st.markdown(audio_html, unsafe_allow_html=True)

    # ---------- Vocabulary ----------
    st.markdown("## 📖 Vocabulary & Signs")
    vocab_cols = st.columns(3)
    for i, word_item in enumerate(ch_data["vocabulary"]):
        with vocab_cols[i % 3]:
            word = translate_text(word_item["word"], st.session_state.language)
            sign_desc = translate_text(word_item["sign_desc"], st.session_state.language)
            st.markdown(f'<div class="vocab-word">✋ {word}</div>', unsafe_allow_html=True)
            st.markdown(f"*Sign:* {sign_desc}")
            if st.button(f"🔊 Say '{word}'", key=f"vocab_audio_{st.session_state.chapter}_{i}"):
                audio_html = text_to_speech(word, st.session_state.language)
                st.markdown(audio_html, unsafe_allow_html=True)

    # ---------- Grammar ----------
    st.markdown("## 📚 Grammar")
    grammar_text = translate_text(ch_data["grammar"], st.session_state.language)
    st.info(grammar_text)
    if st.button("🔊 Read Grammar", key="grammar_audio"):
        audio_html = text_to_speech(grammar_text, st.session_state.language)
        st.markdown(audio_html, unsafe_allow_html=True)

    # ---------- Quiz ----------
    st.markdown("## ✅ Quiz – Test Yourself")
    quiz = ch_data["quiz"]
    score = 0
    for q_idx, q in enumerate(quiz):
        question = translate_text(q["question"], st.session_state.language)
        options = [translate_text(opt, st.session_state.language) for opt in q["options"]]
        answer = translate_text(q["answer"], st.session_state.language)
        user_answer = st.radio(question, options, key=f"quiz_{st.session_state.chapter}_{q_idx}")
        if user_answer == answer:
            score += 1
            st.success("✔️ Correct!")
        else:
            st.error(f"❌ Wrong. Correct answer: {answer}")
    st.markdown(f"**Your score: {score}/{len(quiz)}**")

    st.markdown("---")
    st.markdown("<footer>© 2025 Gesner Deslandes – GlobalInternet.py – All rights reserved</footer>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    login()
else:
    main_app()
