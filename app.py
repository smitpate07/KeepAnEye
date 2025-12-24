import streamlit as st
import time
import threading
from datetime import datetime
import re

from keepaneye.api_call import ApiCall
from keepaneye.save_to_db import SaveToDB
from keepaneye.price_monitor import PriceMonitor
from keepaneye.notify_user import NotifyUser
from keepaneye.tracking_manager import TrackingManager


# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="KeepAnyEye - Price Tracker",
    page_icon="👀",
    layout="centered"
)

# ================= GLOBAL CSS =================
st.markdown("""
<style>

/* ======================================================
   🔒 ABSOLUTE NO-SCROLL — EDGE / STREAMLIT SAFE
   ====================================================== */

* {
    box-sizing: border-box;
}

/* 🔑 TOPMOST STREAMLIT ROOT (CRITICAL FIX) */
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
    height: calc(100svh - 6px) !important;
    max-height: calc(100svh - 6px) !important;
    overflow: hidden !important;
}

/* MAIN WRAPPER */
.main {
    height: 100% !important;
    overflow: hidden !important;
}

/* CONTENT CONTAINER */
.main .block-container {
    height: 100% !important;
    max-height: 100% !important;
    padding: 0.35rem 1rem !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden !important;
}

/* ===== BACKGROUND ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #9fd3ff 0%, #c8f1f4 100%);
}

/* ===== HIDE STREAMLIT UI ===== */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
footer,
header,
#MainMenu {
    display: none !important;
}

/* ======================================================
   🎉 ANIMATED EMOJIS
   ====================================================== */

.emoji-hero {
    text-align: center;
    font-size: clamp(2.1rem, 4vw, 3rem);
    line-height: 1;
    margin: 0.15rem 0;
}

.blink {
    display: inline-block;
    animation: blink 4s infinite;
}
@keyframes blink {
    0%, 95%, 100% { transform: scaleY(1); }
    96%, 98% { transform: scaleY(0.1); }
}

.pulse {
    display: inline-block;
    animation: pulse 1.6s infinite;
}
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.12); }
    100% { transform: scale(1); }
}

.float {
    display: inline-block;
    animation: float 2.4s ease-in-out infinite;
}
@keyframes float {
    0% { transform: translateY(0); }
    50% { transform: translateY(-6px); }
    100% { transform: translateY(0); }
}

/* ======================================================
   🏷️ TITLE
   ====================================================== */

.subtitle {
    text-align: center;
    font-size: clamp(1.6rem, 3.4vw, 2.4rem);
    font-weight: 900;
    color: white;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

/* ======================================================
   🧾 FORM
   ====================================================== */

[data-testid="stForm"] {
    background: white !important;
    padding: 0.45rem !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12) !important;
}

.stTextInput input {
    border-radius: 10px;
    padding: 0.45rem;
}

/* BUTTON */
.stButton > button {
    width: 100%;
    border-radius: 25px;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    font-weight: 600;
}

/* MESSAGES */
.success-msg {
    background: #d4edda;
    padding: 0.4rem;
    border-left: 4px solid #28a745;
    border-radius: 8px;
    font-size: 0.85rem;
}

.error-msg {
    background: #f8d7da;
    padding: 0.4rem;
    border-left: 4px solid #dc3545;
    border-radius: 8px;
    font-size: 0.85rem;
}

/* FOOTER */
.footer-text {
    text-align: center;
    font-size: 0.75rem;
    padding: 0.25rem 0;
}

</style>
""", unsafe_allow_html=True)


# ================= HELPERS =================
def validate_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)

def validate_asin(asin):
    return 8 <= len(asin.strip()) <= 15


def track_product(asin, email):
    try:
        db = SaveToDB()
        tracker = TrackingManager()

        api = ApiCall(asin)
        result = api.call_load()
        if not result:
            return False, "Invalid ASIN"

        db.save_product_data(result, asin)
        tracker.add_tracking(asin, email)

        return True, result
    except Exception as e:
        return False, str(e)


# ================= BACKGROUND CHECKER =================
def run_price_checker():
    tracker = TrackingManager()
    db = SaveToDB()
    monitor = PriceMonitor()

    while True:
        for asin in tracker.get_all_tracked_asins():
            try:
                api = ApiCall(asin)
                data = api.call_load()
                if data:
                    db.save_product_data(data, asin)
                    price = monitor.check_price_changes(asin, "asin")
                    if price and price["price_dropped"]:
                        for email in tracker.get_subscribers_for_asin(asin):
                            NotifyUser(email).send_price_drop_alert(price["product_data"])
            except:
                pass
        time.sleep(43200)


if "checker_started" not in st.session_state:
    st.session_state.checker_started = True
    threading.Thread(target=run_price_checker, daemon=True).start()


# ================= MAIN APP =================
def main():

    st.markdown("""
    <div class="emoji-hero">
        <span class="blink">👀</span>
        <span class="pulse">🔥</span>
        <span class="float">💸</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='subtitle'>Amazon Price Drop Tracker 🚀</div>",
        unsafe_allow_html=True
    )

    with st.form("tracking_form", clear_on_submit=True):
        asin = st.text_input("📦 Amazon ASIN", placeholder="e.g. B0D11HXZNR")
        email = st.text_input("📧 Your Email", placeholder="you@email.com")
        submit = st.form_submit_button("🚀 Start Tracking")

        if submit:
            if not asin or not email:
                st.markdown("<div class='error-msg'>❌ Fill all fields</div>", unsafe_allow_html=True)
            elif not validate_asin(asin):
                st.markdown("<div class='error-msg'>❌ Invalid ASIN</div>", unsafe_allow_html=True)
            elif not validate_email(email):
                st.markdown("<div class='error-msg'>❌ Invalid Email</div>", unsafe_allow_html=True)
            else:
                ok, _ = track_product(asin.strip(), email.strip())
                if ok:
                    msg = st.empty() 
                    st.markdown("<div class='success-msg'>✅ Tracking Started 🎉</div>", unsafe_allow_html=True)
                    st.balloons()
                    time.sleep(5)
                    msg.empty()  
                else:
                    st.markdown("<div class='error-msg'>❌ Failed to track product</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='footer-text'>👁️ <b>KeepAnyEye</b> — Never Miss a Deal 💰 | © {datetime.now().year}</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
