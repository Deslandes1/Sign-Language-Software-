import streamlit as st
import base64
import tempfile
import os
from gtts import gTTS
from deep_translator import GoogleTranslator

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

# ---------- Language mapping ----------
LANG_CODES = {
    "English": "en",
    "French": "fr",
    "Spanish": "es",
    "Haitian Creole": "ht"
}

# ---------- Translation helper ----------
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
    except:
        return text

# ---------- Text-to-speech helper (removes speaker names from audio) ----------
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

# ---------- Generate 20 chapters with Gesner & Junior conversations ----------
def generate_chapter(ch_num):
    # Three different conversation topics per chapter (vary slightly by chapter number)
    topics = [
        f"Greetings and Introductions – Part {ch_num}",
        f"Daily Routine – Day {ch_num}",
        f"Hobbies and Interests – Variation {ch_num}"
    ]
    conversations = []
    for t_idx, topic in enumerate(topics):
        # Create a realistic dialogue between Gesner and Junior (visible names but removed from audio)
        lines_with_names = [
            f"Gesner: Hello Junior! How are you today? (Chapter {ch_num}, {topic})",
            f"Junior: Hi Gesner! I'm doing great, thank you. And you?",
            f"Gesner: I'm fine too. Did you practice sign language yesterday?",
            f"Junior: Yes, I learned many new signs. Would you like to see?",
            f"Gesner: Of course! That would be wonderful.",
            f"Junior: Let's start with the sign for 'hello' – wave your hand.",
            f"Gesner: Oh, I see. What about 'thank you'?",
            f"Junior: You touch your chin with your fingertips and move forward.",
            f"Gesner: That's beautiful. I will practice more.",
            f"Junior: Me too. See you tomorrow!"
        ]
        # For audio, remove the "Name: " prefix (keep only the spoken words)
        spoken_lines = [line.split(": ", 1)[1] if ": " in line else line for line in lines_with_names]
        full_spoken_text = " ".join(spoken_lines)
        conversations.append({
            "title": f"Conversation {t_idx+1}: {topic}",
            "lines_with_names": lines_with_names,   # for display
            "spoken_text": full_spoken_text         # for audio (no names)
        })
    
    # Vocabulary (same across chapters for consistency)
    vocab = [
        {"word": "hello", "sign_desc": "👋 Wave hand near temple"},
        {"word": "thank you", "sign_desc": "🤟 Touch chin and move forward"},
        {"word": "practice", "sign_desc": "🖐️ Repeated hand motion"},
        {"word": "learn", "sign_desc": "📖 Take from hand to forehead"},
        {"word": "beautiful", "sign_desc": "👐 Open hands circling face"}
    ]
    grammar = "Sign language uses hand shapes, facial expressions, and body movements. Word order is often Subject-Object-Verb."
    quiz = [
        {"question": "What is the sign for 'hello'?", "options": ["👋 Wave", "✌️ Peace", "👍 Thumbs up"], "answer": "👋 Wave"},
        {"question": "Which body part is used for 'thank you'?", "options": ["Chin", "Forehead", "Chest"], "answer": "Chin"},
        {"question": "True or False: Sign language is the same worldwide.", "options": ["True", "False"], "answer": "False"}
    ]
    return {
        "title": f"Chapter {ch_num}: Gesner & Junior Sign Conversation",
        "conversations": conversations,
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
            st.session_state.translations = {}
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

    st.markdown("# 🤟 Sign Language Book Software")
    st.markdown("### Built by **Gesner Deslandes**")
    st.markdown("---")

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
    st.markdown("## 💬 Gesner & Junior Live Conversations")
    for idx, conv in enumerate(ch_data["conversations"]):
        with st.expander(f"🗣️ {translate_text(conv['title'], st.session_state.language)}"):
            # Display conversation lines with names
            for line in conv["lines_with_names"]:
                st.markdown(f"- {translate_text(line, st.session_state.language)}")
            # Audio button – plays only the spoken words (names removed)
            if st.button(f"🔊 Play Conversation {idx+1} (Audio – no names)", key=f"conv_audio_{st.session_state.chapter}_{idx}"):
                spoken_text_translated = translate_text(conv["spoken_text"], st.session_state.language)
                audio_html = text_to_speech(spoken_text_translated, st.session_state.language)
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
