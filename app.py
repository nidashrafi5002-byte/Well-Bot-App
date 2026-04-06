import streamlit as st
from groq import Groq
import os
import json
import random
from dotenv import load_dotenv
from fpdf import FPDF
import datetime
from streamlit.components.v1 import html as st_html

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

HISTORY_FILE = "chat_history.json"
PROFILE_FILE = "user_profile.json"

LANGUAGES = {
    "English": ("English", "en-US"),
    "Hindi": ("Hindi", "hi-IN"),
    "Kannada": ("Kannada", "kn-IN"),
    "Tamil": ("Tamil", "ta-IN"),
    "Telugu": ("Telugu", "te-IN"),
    "Malayalam": ("Malayalam", "ml-IN"),
    "Bengali": ("Bengali", "bn-IN"),
    "Japanese": ("Japanese", "ja-JP"),
    "Korean": ("Korean", "ko-KR"),
    "Spanish": ("Spanish", "es-ES"),
    "French": ("French", "fr-FR"),
    "Arabic": ("Arabic", "ar-SA"),
    "Chinese": ("Chinese", "zh-CN"),
    "German": ("German", "de-DE"),
}

HEALTH_TIPS = [
    "Drink at least 8 glasses of water daily to stay hydrated.",
    "Aim for 7-9 hours of sleep every night for optimal health.",
    "Take a 10-minute walk after meals to aid digestion.",
    "Eat more fruits and vegetables — aim for 5 servings a day.",
    "Limit screen time before bed to improve sleep quality.",
    "Practice deep breathing for 5 minutes to reduce stress.",
    "Wash your hands regularly to prevent infections.",
    "Stretch for 5 minutes every hour if you sit for long periods.",
    "Avoid skipping breakfast — it fuels your brain and body.",
    "Limit sugary drinks and opt for water or herbal tea.",
    "Regular exercise (30 min/day) reduces risk of chronic disease.",
    "Maintain a consistent meal schedule to regulate metabolism.",
    "Spend time outdoors daily for natural Vitamin D.",
    "Avoid smoking and limit alcohol for a healthier life.",
    "Regular health checkups help catch issues early.",
]

def get_system_msg(language, profile=None):
    lang_name = language[0] if isinstance(language, tuple) else language
    profile_context = ""
    if profile and profile.get("name"):
        profile_context = (
            f" The user's name is {profile['name']}."
            f" Age: {profile.get('age', 'unknown')}."
            f" Blood group: {profile.get('blood_group', 'unknown')}."
            f" Known conditions: {profile.get('conditions', 'none')}."
            " Use this info to personalize your responses."
        )
    return {
        "role": "system",
        "content": f"You are WellBot, a friendly health assistant.{profile_context} Always respond in {lang_name}. Give general health guidance only. Always remind users to consult a doctor for medical advice."
    }

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_session(messages):
    history = load_history()
    chat_only = [m for m in messages if m["role"] != "system"]
    if not chat_only:
        return
    session = {
        "id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "date": datetime.datetime.now().strftime("%B %d, %Y at %H:%M"),
        "preview": chat_only[0]["content"][:55] + "...",
        "messages": messages
    }
    history.insert(0, session)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f)

def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f)

def clean_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")

def get_font():
    font_path = "DejaVuSans.ttf"
    if not os.path.exists(font_path):
        import urllib.request
        urllib.request.urlretrieve(
            "https://github.com/dejavu-fonts/dejavu-fonts/raw/refs/heads/master/ttf/DejaVuSans.ttf",
            font_path
        )
    return font_path

def generate_pdf(messages, profile=None):
    from fpdf.enums import XPos, YPos
    pdf = FPDF()
    pdf.set_margins(15, 15, 15)
    pdf.add_page()

    font_path = get_font()
    pdf.add_font("DejaVu", "", font_path)
    pdf.add_font("DejaVu", "B", font_path)
    fn = "DejaVu"

    pdf.set_fill_color(0, 102, 204)
    pdf.rect(0, 0, 210, 28, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(fn, "B", 18)
    pdf.set_y(5)
    pdf.cell(0, 10, "WellBot - Health Assessment Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font(fn, "", 9)
    pdf.cell(0, 6, f"Generated on {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.ln(8)
    pdf.set_text_color(0, 0, 0)

    if profile and profile.get("name"):
        pdf.set_font(fn, "B", 11)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 8, "Patient Information", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(0, 102, 204)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)
        pdf.set_font(fn, "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Name: {profile.get('name','-')}   Age: {profile.get('age','-')}   Blood Group: {profile.get('blood_group','-')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, f"Known Conditions: {profile.get('conditions','None')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    pdf.set_fill_color(255, 243, 205)
    pdf.set_draw_color(255, 193, 7)
    pdf.set_font(fn, "B", 9)
    pdf.set_text_color(133, 100, 4)
    pdf.multi_cell(0, 7, "DISCLAIMER: This report contains general health guidance only. It is not a substitute for professional medical advice. Please consult a qualified healthcare provider.", border=1, fill=True)
    pdf.ln(5)

    pdf.set_font(fn, "B", 13)
    pdf.set_text_color(0, 102, 204)
    pdf.cell(0, 8, "Reported Symptoms", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(0, 102, 204)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    pdf.set_font(fn, "", 10)
    pdf.set_text_color(0, 0, 0)
    for msg in messages:
        if msg["role"] == "user":
            pdf.set_fill_color(240, 248, 255)
            pdf.multi_cell(0, 7, f"- {msg['content']}", fill=True)
            pdf.ln(1)

    pdf.ln(3)
    pdf.set_font(fn, "B", 13)
    pdf.set_text_color(0, 153, 76)
    pdf.cell(0, 8, "Health Guidance & Recommendations", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(0, 153, 76)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(3)
    pdf.set_font(fn, "", 10)
    pdf.set_text_color(0, 0, 0)
    for msg in messages:
        if msg["role"] == "assistant":
            pdf.set_fill_color(240, 255, 245)
            pdf.multi_cell(0, 7, msg["content"], fill=True)
            pdf.ln(3)

    pdf.set_y(-18)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.set_font(fn, "", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, "Generated by WellBot - For informational purposes only.", align="C")
    return bytes(pdf.output())

# ── Page config ──
st.set_page_config(page_title="WellBot", layout="wide", page_icon="💊")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background: linear-gradient(135deg, #0a0a1a, #1a1040, #0d1b2a); min-height: 100vh; }

    /* Animated background particles feel */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: radial-gradient(ellipse at 20% 50%, rgba(102,126,234,0.08) 0%, transparent 60%),
                    radial-gradient(ellipse at 80% 20%, rgba(56,239,125,0.06) 0%, transparent 50%);
        pointer-events: none; z-index: 0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(10,10,30,0.85) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(102,126,234,0.2);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: rgba(255,255,255,0.04);
        border-radius: 18px;
        padding: 14px 18px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.07);
        backdrop-filter: blur(10px);
        transition: all 0.2s ease;
        animation: fadeIn 0.4s ease;
    }
    [data-testid="stChatMessage"]:hover {
        border-color: rgba(102,126,234,0.3);
        background: rgba(255,255,255,0.06);
    }
    @keyframes fadeIn { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform: translateY(0); } }

    /* Chat input */
    [data-testid="stChatInput"] textarea {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(102,126,234,0.3) !important;
        border-radius: 16px !important;
        color: white !important;
        font-size: 15px !important;
        transition: border 0.3s ease !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: rgba(102,126,234,0.8) !important;
        box-shadow: 0 0 20px rgba(102,126,234,0.15) !important;
    }

    /* All buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        width: 100%;
        letter-spacing: 0.3px;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(102,126,234,0.45);
        background: linear-gradient(135deg, #7b8ff5, #8a5cb8);
    }
    .stButton > button:active { transform: translateY(0px); }

    /* Download button */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #11998e, #38ef7d) !important;
        color: #0a2a1a !important;
        border: none; border-radius: 12px;
        font-weight: 600; width: 100%;
    }
    [data-testid="stDownloadButton"] > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 25px rgba(56,239,125,0.35);
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(102,126,234,0.1);
        border: 1px solid rgba(102,126,234,0.2);
        text-align: left; border-radius: 10px;
        font-size: 12px; margin-bottom: 4px;
        font-weight: 400;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(102,126,234,0.25);
        box-shadow: none; transform: none;
        border-color: rgba(102,126,234,0.5);
    }

    /* Title */
    h1 {
        background: linear-gradient(135deg, #a78bfa, #38ef7d, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-weight: 800 !important; font-size: 2.4rem !important;
        letter-spacing: -0.5px;
    }
    h3, h4 { color: #c9d1d9 !important; }
    p, .stMarkdown { color: #b0bec5 !important; }

    .stInfo {
        background: rgba(102,126,234,0.1) !important;
        border: 1px solid rgba(102,126,234,0.25) !important;
        border-radius: 12px; color: #c9d1d9 !important;
    }

    /* Custom cards */
    .disclaimer {
        background: linear-gradient(135deg, rgba(255,193,7,0.08), rgba(255,152,0,0.05));
        border-left: 3px solid #ffc107;
        border-radius: 12px; padding: 12px 18px;
        color: #ffd54f !important; font-size: 13px; margin-bottom: 20px;
    }
    .tip-box {
        background: linear-gradient(135deg, rgba(56,239,125,0.08), rgba(17,153,142,0.05));
        border-left: 3px solid #38ef7d;
        border-radius: 12px; padding: 12px 16px;
        color: #a8f0c6 !important; font-size: 13px;
        line-height: 1.6; margin-bottom: 8px;
    }
    .profile-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.12), rgba(118,75,162,0.08));
        border-radius: 12px; padding: 12px 16px;
        border: 1px solid rgba(102,126,234,0.25); margin-bottom: 8px;
        font-size: 13px;
    }
    .sug-btn-wrap { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }
    .welcome-box {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(56,239,125,0.05));
        border: 1px solid rgba(102,126,234,0.2);
        border-radius: 20px; padding: 30px;
        text-align: center; margin-bottom: 24px;
        animation: fadeIn 0.6s ease;
    }
    .welcome-box h2 { color: #e0e0e0 !important; font-size: 1.5rem; margin-bottom: 6px; }
    .welcome-box p { color: #90a4ae !important; font-size: 14px; }
    .stat-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px; padding: 16px;
        text-align: center;
    }
    .stat-card .num { font-size: 1.8rem; font-weight: 700; background: linear-gradient(135deg,#667eea,#38ef7d); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .stat-card .label { font-size: 12px; color: #78909c !important; margin-top: 4px; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(102,126,234,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──
profile = load_profile()

with st.sidebar:
    st.markdown("## 💊 WellBot")
    st.markdown("---")

    # Health Tip
    if "tip_index" not in st.session_state:
        st.session_state.tip_index = random.randint(0, len(HEALTH_TIPS) - 1)
    st.markdown("### 💡 Health Tip of the Day")
    st.markdown(f'<div class="tip-box">{HEALTH_TIPS[st.session_state.tip_index]}</div>', unsafe_allow_html=True)
    if st.button("New Tip"):
        st.session_state.tip_index = random.randint(0, len(HEALTH_TIPS) - 1)
        st.rerun()

    st.markdown("---")

    # User Profile
    st.markdown("### 👤 User Profile")
    with st.expander("Edit Profile", expanded=not bool(profile.get("name"))):
        name = st.text_input("Name", value=profile.get("name", ""))
        age = st.text_input("Age", value=profile.get("age", ""))
        blood_group = st.selectbox("Blood Group", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                                   index=["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].index(profile.get("blood_group", "")) if profile.get("blood_group") else 0)
        conditions = st.text_input("Known Conditions", value=profile.get("conditions", ""), placeholder="e.g. diabetes, asthma")
        if st.button("Save Profile"):
            profile = {"name": name, "age": age, "blood_group": blood_group, "conditions": conditions}
            save_profile(profile)
            st.success("Saved!")
            st.rerun()

    if profile.get("name"):
        st.markdown(f'<div class="profile-box">👤 {profile["name"]} | {profile.get("age","?")} yrs | {profile.get("blood_group","?")}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Language
    st.markdown("### 🌐 Language")
    selected_lang_key = st.selectbox("Choose language", list(LANGUAGES.keys()), key="language")
    selected_lang, lang_locale = LANGUAGES[selected_lang_key]

    st.markdown("---")

    # Chat History
    st.markdown("### 🕐 Chat History")
    if st.button("🗑️ Clear All History"):
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()
    st.markdown("")
    history = load_history()
    if not history:
        st.info("No past sessions yet.")
    for session in history:
        if st.button(f"📅 {session['date']}\n{session['preview']}", key=session["id"]):
            st.session_state.messages = session["messages"]
            st.session_state.viewing_history = True
            st.rerun()

# ── Main ──
st.title("💊 WellBot")

greeting_name = f", {profile['name']}" if profile.get("name") else ""
st.markdown(f"""
<div class="welcome-box">
    <div style="font-size:3rem; margin-bottom:8px;">💊</div>
    <h2>Welcome to WellBot{greeting_name}</h2>
    <p>Your AI-powered health assistant. Describe your symptoms and get instant guidance.</p>
</div>
""", unsafe_allow_html=True)

SYSTEM_MSG = get_system_msg(selected_lang, profile)
if "messages" not in st.session_state:
    st.session_state.messages = [SYSTEM_MSG]
if "viewing_history" not in st.session_state:
    st.session_state.viewing_history = False
if "suggested_input" not in st.session_state:
    st.session_state.suggested_input = ""

history_count = len(load_history())
chat_count = len([m for m in st.session_state.messages if m["role"] == "user"])
sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f'<div class="stat-card"><div class="num">{history_count}</div><div class="label">Past Sessions</div></div>', unsafe_allow_html=True)
with sc2:
    st.markdown(f'<div class="stat-card"><div class="num">{chat_count}</div><div class="label">Messages Today</div></div>', unsafe_allow_html=True)
with sc3:
    st.markdown('<div class="stat-card"><div class="num">14</div><div class="label">Languages</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="disclaimer">This bot gives general health guidance only. Always consult a doctor for medical advice.</div>', unsafe_allow_html=True)

chat_only = [m for m in st.session_state.messages if m["role"] != "system"]
if not chat_only and not st.session_state.viewing_history:
    st.markdown("#### 🩹 Common Symptoms — tap to ask:")
    suggestions = [
        ("🌡️", "I have a fever"), ("🤕", "I have a headache"), ("🤢", "I feel nauseous"),
        ("😮", "I have a sore throat"), ("😵", "I feel dizzy"), ("💔", "I have chest pain"),
        ("😴", "I can't sleep"), ("🦴", "I have back pain"), ("😓", "I feel very tired"), ("🤧", "I have a cold"),
    ]
    cols = st.columns(5)
    for i, (icon, s) in enumerate(suggestions):
        if cols[i % 5].button(f"{icon} {s}", key=f"sug_{i}"):
            st.session_state.suggested_input = s
            st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

if not st.session_state.viewing_history:
    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    # Mic button using streamlit component
    vc, tc = st.columns([1, 11])
    with vc:
        mic_clicked = st.button("🎤")
    with tc:
        st.markdown("<span style='color:#c9d1d9; font-size:13px;'>Click 🎤 then speak, or type below</span>", unsafe_allow_html=True)

    if mic_clicked:
        st_html("""
        <script>
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) { alert('Speech recognition not supported. Use Chrome.'); }
        else {
            const r = new SR();
            r.lang = 'en-US';
            r.interimResults = false;
            r.onresult = (e) => {
                const t = e.results[0][0].transcript;
                // Write to a hidden input Streamlit can read via query param trick
                window.parent.location.href = window.parent.location.href.split('?')[0] + '?voice=' + encodeURIComponent(t);
            };
            r.start();
        }
        </script>
        """, height=0)

    # Pick up voice input from query params
    params = st.query_params
    if "voice" in params and params["voice"]:
        st.session_state.voice_text = params["voice"]
        st.query_params.clear()

    voice_input = st.session_state.voice_text
    if voice_input:
        st.info(f"Voice input: {voice_input}")

    user_input = st.chat_input("Describe your symptoms...")
    if not user_input and st.session_state.suggested_input:
        user_input = st.session_state.suggested_input
    if not user_input and voice_input:
        user_input = voice_input
    if st.session_state.suggested_input:
        st.session_state.suggested_input = ""
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.spinner("Analyzing..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[get_system_msg(selected_lang, profile)] + [m for m in st.session_state.messages if m["role"] != "system"]            )
        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})
        with st.chat_message("assistant"):
            st.markdown(reply)
        # TTS - speak reply
        clean = reply.replace("'", "\\'").replace("\n", " ").replace('"', '\\"')[:500]
        st_html(f"""
        <button onclick="speakText()" style="
            background: linear-gradient(135deg,#667eea,#764ba2);
            color:white; border:none; border-radius:8px;
            padding:6px 14px; cursor:pointer; font-size:13px; margin-top:4px;">
            🔊 Read Aloud
        </button>
        <script>
        function speakText() {{
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance('{clean}');
            u.lang = '{lang_locale}'; u.rate = 0.95;
            window.speechSynthesis.speak(u);
        }}
        </script>
        """, height=50)
else:
    st.info("Viewing a past session. Start a new chat to continue.")

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🧹 Clear Chat"):
        save_session(st.session_state.messages)
        st.session_state.messages = [SYSTEM_MSG]
        st.session_state.viewing_history = False
        st.rerun()
with col2:
    if st.button("✨ New Chat"):
        save_session(st.session_state.messages)
        st.session_state.messages = [SYSTEM_MSG]
        st.session_state.viewing_history = False
        st.rerun()

final_chat = [m for m in st.session_state.messages if m["role"] != "system"]
if final_chat:
    try:
        pdf_data = generate_pdf(st.session_state.messages, profile)
        st.download_button(
            label="📄 Download Report",
            data=pdf_data,
            file_name=f"wellbot_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        import traceback
        st.error(traceback.format_exc())
