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

/* ===== NO SCROLL (EDGE SAFE) ===== */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {
    height: 100svh !important;
    overflow: hidden !important;
    margin: 0 !important;
}

.main .block-container {
    height: 100%;
    max-height: 100%;
    padding: 0.5rem 1rem !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

/* ===== BACKGROUND ===== */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
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

/* ===== ANIMATED EMOJIS ===== */
.emoji-hero {
    text-align: center;
    font-size: clamp(2.4rem, 4vw, 3.2rem);
    margin-bottom: 0.3rem;
}

.blink { animation: blink 4s infinite; display: inline-block; }
@keyframes blink { 96% { transform: scaleY(0.1); } }

.pulse { animation: pulse 1.5s infinite; display: inline-block; }
@keyframes pulse {
    0% { transform: scale(1); }
    50% { transform: scale(1.15); }
    100% { transform: scale(1); }
}

.float { animation: float 2.4s ease-in-out infinite; display: inline-block; }
@keyframes float {
    50% { transform: translateY(-6px); }
}

/* ===== TITLE ===== */
.subtitle {
    text-align: center;
    font-size: clamp(1.7rem, 3.6vw, 2.5rem);
    font-weight: 900;
    color: white;
    margin-bottom: 0.5rem;
}

/* ===== FORM ===== */
[data-testid="stForm"] {
    background: white !important;
    padding: 0.6rem !important;
    border-radius: 16px !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15) !important;
}

.stTextInput input {
    border-radius: 10px;
    padding: 0.5rem;
}

.stTextInput > label {
    color: #333 !important;
    font-weight: 500;
}

/* ===== BUTTON ===== */
.stButton > button {
    width: 100%;
    border-radius: 25px;
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    color: white;
    font-weight: 700;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(79, 172, 254, 0.4);
}

/* ===== MESSAGES ===== */
.success-msg {
    background: #d4edda;
    padding: 0.5rem;
    border-left: 5px solid #28a745;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #155724;
}

.error-msg {
    background: #f8d7da;
    padding: 0.5rem;
    border-left: 5px solid #dc3545;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #721c24;
}

/* ===== FOOTER (BIGGER) ===== */
.footer-text {
    text-align: center;
    font-size: 1rem;
    padding: 0.6rem 0;
    font-weight: 600;
    color: white;
}

</style>
""", unsafe_allow_html=True)


# ================= HELPERS =================
def validate_email(email):
    """Validate email format"""
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)


def validate_asin(asin):
    """Validate ASIN format (8-15 characters)"""
    return 8 <= len(asin.strip()) <= 15


def track_product(asin, email):
    """Track a single product - only makes API call for THIS product"""
    try:
        db_handler = SaveToDB()
        tracking_mgr = TrackingManager()
        
        # ONLY fetch data for THIS specific ASIN
        with st.spinner('🔍 Fetching product...'):
            api_caller = ApiCall(asin)
            results = api_caller.call_load()
            
            if not results:
                return False, "Could not fetch product data. Check ASIN."
        
        # Save to database
        with st.spinner('💾 Saving...'):
            saved_doc = db_handler.save_product_data(results, asin)
            if not saved_doc:
                return False, "Could not save product data."
        
        # Add tracking subscription for this user
        tracking_mgr.add_tracking(asin, email)
        
        return True, saved_doc
        
    except Exception as e:
        return False, f"Error: {str(e)}"


# ================= BACKGROUND CHECKER =================
def run_price_checker():
    """Background task - checks ALL tracked products every 12 hours"""
    tracking_mgr = TrackingManager()
    db_handler = SaveToDB()
    monitor = PriceMonitor()
    
    while True:
        try:
            # Get ALL products being tracked by any user
            tracked_asins = tracking_mgr.get_all_tracked_asins()
            
            print(f"🔍 Checking {len(tracked_asins)} products...")
            
            for asin in tracked_asins:
                try:
                    # Fetch latest price for this ASIN
                    api_caller = ApiCall(asin)
                    results = api_caller.call_load()
                    
                    if results:
                        # Save new price data
                        db_handler.save_product_data(results, asin)
                        
                        # Check if price dropped
                        price_result = monitor.check_price_changes(asin, 'asin')
                        
                        if price_result and price_result['price_dropped']:
                            print(f"💰 Price drop detected for {asin}!")
                            
                            # Get ALL subscribers for this ASIN
                            subscribers = tracking_mgr.get_subscribers_for_asin(asin)
                            
                            # Send email to EACH subscriber
                            for email in subscribers:
                                try:
                                    notifier = NotifyUser(email) 
                                    notifier.send_price_drop_alert(price_result['product_data'])
                                    print(f"📧 Email sent to {email}")
                                except Exception as e:
                                    print(f"❌ Email failed for {email}: {str(e)}")
                        else:
                            print(f"📊 No price drop for {asin}")
                            
                except Exception as e:
                    print(f"❌ Error checking {asin}: {str(e)}")
                    continue
            
            print(f"✅ Completed check cycle. Sleeping 12 hours...")
            time.sleep(43200)  # 12 hours
            
        except Exception as e:
            print(f"❌ Checker error: {str(e)}")
            time.sleep(3600)  # Wait 1 hour on error


# Initialize background checker once
if "checker_started" not in st.session_state:
    st.session_state.checker_started = True
    threading.Thread(target=run_price_checker, daemon=True).start()


# ================= MAIN APP =================
def main():
    """Main application UI"""
    
    # Animated emoji header
    st.markdown("""
    <div class="emoji-hero">
        <span class="blink">👀</span>
        <span class="pulse">🔥</span>
        <span class="float">💸</span>
    </div>
    """, unsafe_allow_html=True)

    # Title
    st.markdown(
        "<div class='subtitle'>Amazon Price Drop Tracker 🚀</div>",
        unsafe_allow_html=True
    )

    # Status message placeholder
    status = st.empty()

    # Tracking form
    with st.form("tracking_form", clear_on_submit=True):
        asin = st.text_input("📦 Amazon ASIN", placeholder="e.g. B0D11HXZNR")
        email = st.text_input("📧 Your Email", placeholder="you@email.com")
        submit = st.form_submit_button("🚀 Start Tracking")

        if submit:
            # Validation
            if not asin or not email:
                status.markdown("<div class='error-msg'>❌ Fill all fields</div>", unsafe_allow_html=True)
            elif not validate_asin(asin):
                status.markdown("<div class='error-msg'>❌ Invalid ASIN (8-15 characters)</div>", unsafe_allow_html=True)
            elif not validate_email(email):
                status.markdown("<div class='error-msg'>❌ Invalid Email</div>", unsafe_allow_html=True)
            else:
                # Process tracking
                status.markdown("<div class='success-msg'>⏳ Starting Tracking…</div>", unsafe_allow_html=True)

                ok, result = track_product(asin.strip(), email.strip())

                if ok:
                    status.markdown("<div class='success-msg'>✅ Tracking Started 🎉</div>", unsafe_allow_html=True)
                    st.balloons()
                    time.sleep(3)
                    status.empty()
                else:
                    status.markdown(f"<div class='error-msg'>❌ {result}</div>", unsafe_allow_html=True)

    # Footer
    st.markdown(
        f"<div class='footer-text'>👁️ KeepAnyEye — Never Miss a Deal 💰 | © {datetime.now().year}</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()