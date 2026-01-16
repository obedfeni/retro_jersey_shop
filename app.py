# ==========================================
# RETRO JERSEY SHOP - ADVANCED EDITION
# Features: Cloudinary, Analytics, Ads, Video Support
# ==========================================

import streamlit as st
import gspread
import pandas as pd
import os, json, base64
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import random
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image
import io
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# ---------------- CLOUDINARY SETUP ----------------
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

# ---------------- REFERENCE GENERATOR ----------------
def generate_reference(product_name, location):
    product_code = product_name[:3].upper()
    location_code = location[:3].upper()
    rand = random.randint(1000, 9999)
    return f"RJ-{product_code}-{location_code}-{rand}"

# ---------------- CLOUDINARY UPLOAD (IMAGE & VIDEO) ----------------
def upload_to_cloudinary(file, filename, resource_type="image"):
    """Upload image or video to Cloudinary"""
    try:
        file.seek(0)
        public_id = f"RetroJerseyShop/{filename.replace('.jpg', '').replace('.mp4', '')}"
        
        if resource_type == "video":
            result = cloudinary.uploader.upload(
                file,
                public_id=public_id,
                folder="RetroJerseyShop",
                overwrite=True,
                resource_type="video",
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
        else:
            result = cloudinary.uploader.upload(
                file,
                public_id=public_id,
                folder="RetroJerseyShop",
                overwrite=True,
                resource_type="image",
                format="jpg",
                transformation=[
                    {'width': 800, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'},
                    {'fetch_format': 'auto'}
                ]
            )
        
        secure_url = result.get('secure_url')
        print(f"✅ Uploaded to Cloudinary: {secure_url}")
        return secure_url
    
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        return None

# ---------------- DELETE FROM CLOUDINARY ----------------
def delete_from_cloudinary(media_url):
    """Delete media from Cloudinary"""
    try:
        if 'cloudinary.com' in media_url:
            parts = media_url.split('/')
            upload_idx = parts.index('upload')
            public_id_parts = parts[upload_idx + 2:]
            public_id = '/'.join(public_id_parts).rsplit('.', 1)[0]
            
            # Detect resource type
            resource_type = "video" if any(ext in media_url for ext in ['.mp4', '.mov', '.avi']) else "image"
            
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            print(f"🗑️ Deleted from Cloudinary: {public_id}")
            return result.get('result') == 'ok'
    except Exception as e:
        print(f"❌ Cloudinary delete error: {e}")
    return False

# ---------------- ANALYTICS TRACKER ----------------
def track_visit():
    """Track website visits in Google Sheets"""
    try:
        analytics_sheet = client.open(SHEET_NAME).worksheet("analytics")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        analytics_sheet.append_row([timestamp, "page_visit"])
        print(f"📊 Visit tracked: {timestamp}")
    except Exception as e:
        print(f"Analytics error: {e}")

def get_visit_count():
    """Get total visit count"""
    try:
        analytics_sheet = client.open(SHEET_NAME).worksheet("analytics")
        records = analytics_sheet.get_all_records()
        return len(records)
    except:
        return 0

# ---------------- EMAIL NOTIFICATION ----------------
def send_email_notification(subject, message):
    admin_email = os.environ.get("ADMIN_EMAIL")
    email_password = os.environ.get("EMAIL_APP_PASSWORD")
    
    if not admin_email or not email_password:
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = admin_email
        msg['To'] = admin_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(admin_email, email_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ---------------- TELEGRAM NOTIFICATION ----------------
def send_telegram_notification(message):
    telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not telegram_bot_token or not telegram_chat_id:
        return False
    
    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        data = {
            "chat_id": telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Retro Jersey Shop",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- SESSION STATE ----------------
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "show_admin_login" not in st.session_state:
    st.session_state.show_admin_login = False

if "visit_tracked" not in st.session_state:
    st.session_state.visit_tracked = False

# ---------------- CHECK FOR ADMIN ROUTE ----------------
query_params = st.query_params
if "page" in query_params and query_params["page"] == "admin":
    st.session_state.show_admin_login = True

# ---------------- HIDE STREAMLIT UI ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ---------------- ADVANCED DYNAMIC THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary: #ff6b35;
    --secondary: #004e89;
    --accent: #f7931e;
    --dark: #1a1a2e;
    --light: #f8f9fa;
}

html, body, .stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #1a1a2e;
    font-family: 'Inter', sans-serif;
}

/* Dynamic Animated Background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        radial-gradient(circle at 20% 50%, rgba(255, 107, 53, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 80%, rgba(0, 78, 137, 0.1) 0%, transparent 50%);
    animation: backgroundPulse 15s ease-in-out infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes backgroundPulse {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 0.8; }
}

/* Mega Header with Animation */
.mega-header {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    padding: 50px 40px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
    margin-bottom: 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    animation: slideDown 0.5s ease-out;
}

@keyframes slideDown {
    from {
        transform: translateY(-100%);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    gap: 30px;
}

/* Epic Logo Emblem */
.logo-emblem {
    width: 120px;
    height: 120px;
    background: linear-gradient(135deg, #fff 0%, #f0f0f0 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 
        0 0 0 8px rgba(255, 255, 255, 0.3),
        0 0 0 16px rgba(255, 255, 255, 0.1),
        0 15px 40px rgba(0, 0, 0, 0.4);
    position: relative;
    animation: floatBounce 3s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes floatBounce {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    25% { transform: translateY(-10px) rotate(-5deg); }
    50% { transform: translateY(0) rotate(0deg); }
    75% { transform: translateY(-10px) rotate(5deg); }
}

.logo-emblem svg {
    width: 70px;
    height: 70px;
}

.header-text {
    flex: 1;
}

.store-name {
    font-family: 'Orbitron', sans-serif;
    font-size: 56px;
    font-weight: 900;
    color: white;
    margin: 0;
    line-height: 1.1;
    text-shadow: 
        3px 3px 6px rgba(0, 0, 0, 0.3),
        0 0 30px rgba(255, 255, 255, 0.3);
    letter-spacing: 2px;
    animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
    0%, 100% { text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3), 0 0 30px rgba(255, 255, 255, 0.3); }
    50% { text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3), 0 0 50px rgba(255, 255, 255, 0.5); }
}

.store-tagline {
    font-size: 22px;
    color: rgba(255, 255, 255, 0.95);
    margin: 10px 0 0 0;
    font-weight: 500;
    letter-spacing: 1px;
}

/* Mobile responsive header */
@media (max-width: 768px) {
    .mega-header { padding: 30px 20px; }
    .logo-emblem { width: 80px; height: 80px; }
    .logo-emblem svg { width: 50px; height: 50px; }
    .store-name { font-size: 32px; }
    .store-tagline { font-size: 14px; }
}

/* Content Wrapper */
.content-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 40px 20px;
    position: relative;
    z-index: 1;
}

/* Floating Ad Banner */
.ad-banner {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    border: 3px solid #ff6b35;
    border-radius: 20px;
    padding: 30px;
    margin: 30px 0;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    animation: pulse 2s ease-in-out infinite;
    position: relative;
    overflow: hidden;
}

.ad-banner::before {
    content: '🎉';
    position: absolute;
    font-size: 100px;
    opacity: 0.1;
    top: -20px;
    right: -20px;
    animation: rotate 10s linear infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.ad-title {
    font-size: 32px;
    font-weight: 900;
    color: #ff6b35;
    margin: 0 0 10px 0;
    text-transform: uppercase;
}

.ad-text {
    font-size: 18px;
    color: #1a1a2e;
    font-weight: 600;
}

/* Section Headers */
.section-header {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 40px 0 25px 0;
    padding-bottom: 15px;
    border-bottom: 4px solid #ff6b35;
    text-align: center;
}

/* Premium Product Cards with Hover Effects */
.product-card {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    height: 100%;
    display: flex;
    flex-direction: column;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.product-card:hover {
    transform: translateY(-15px) scale(1.02);
    box-shadow: 0 20px 60px rgba(255, 107, 53, 0.3);
    border-color: #ff6b35;
}

.product-image-wrapper {
    width: 100%;
    height: 320px;
    background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

.product-image-wrapper img,
.product-image-wrapper video {
    width: 100%;
    height: 100%;
    object-fit: contain;
    transition: transform 0.5s ease;
}

.product-card:hover .product-image-wrapper img,
.product-card:hover .product-image-wrapper video {
    transform: scale(1.1) rotate(2deg);
}

.stock-badge {
    position: absolute;
    top: 15px;
    right: 15px;
    padding: 8px 16px;
    border-radius: 25px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.badge-in-stock {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
}

.badge-out-stock {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
}

.product-info {
    padding: 25px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.product-title {
    font-size: 19px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 12px;
    line-height: 1.4;
}

.product-description {
    font-size: 14px;
    color: #666;
    line-height: 1.6;
    margin-bottom: 15px;
    flex: 1;
}

.product-price {
    font-size: 32px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 15px;
}

/* Epic Buttons */
.stButton>button {
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    color: white;
    border: none;
    border-radius: 15px;
    padding: 15px 30px;
    font-weight: 700;
    font-size: 16px;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: 0 6px 20px rgba(255, 107, 53, 0.4);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 30px rgba(255, 107, 53, 0.6);
    background: linear-gradient(135deg, #f7931e 0%, #ff6b35 100%);
}

.stButton>button:disabled {
    background: #ccc;
    box-shadow: none;
}

/* Admin Stats Cards */
.stat-card {
    background: linear-gradient(135deg, white 0%, #f8f9fa 100%);
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    padding: 30px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    border-color: #ff6b35;
}

.stat-number {
    font-size: 48px;
    font-weight: 900;
    background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 10px;
}

.stat-label {
    font-size: 16px;
    color: #666;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Admin Container */
.admin-container {
    background: white;
    border: 2px solid #e0e0e0;
    border-radius: 20px;
    padding: 35px;
    margin-bottom: 30px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

/* Success Message */
.success-message {
    background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
    border: 3px solid #10b981;
    color: #065f46;
    padding: 25px;
    border-radius: 20px;
    margin: 25px 0;
    box-shadow: 0 5px 20px rgba(16, 185, 129, 0.3);
    animation: slideIn 0.5s ease-out;
}

@keyframes slideIn {
    from {
        transform: translateX(-100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

/* Footer */
.footer-section {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    padding: 60px 20px;
    margin-top: 80px;
    text-align: center;
    border-top: 5px solid #ff6b35;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-bottom: 30px;
    flex-wrap: wrap;
}

.footer-link {
    color: white;
    font-size: 16px;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
}

.footer-link:hover {
    color: #ff6b35;
    transform: translateY(-3px);
}
</style>
""", unsafe_allow_html=True)

# ---------------- GOOGLE SHEETS AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

raw_creds = os.environ.get("GCP_SERVICE_ACCOUNT")
if not raw_creds:
    st.error("⚠️ Server configuration error")
    st.stop()

try:
    creds_dict = json.loads(raw_creds)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
except Exception as e:
    st.error(f"⚠️ Google Sheets connection error: {str(e)}")
    st.stop()

# ---------------- LOAD SHEETS ----------------
SHEET_NAME = "retro_jersey_shop"
try:
    products_sheet = client.open(SHEET_NAME).worksheet("products")
    orders_sheet = client.open(SHEET_NAME).worksheet("orders")
except Exception as e:
    st.error(f"⚠️ Could not find sheets. Error: {str(e)}")
    st.stop()

def load_products():
    records = products_sheet.get_all_records(expected_headers=[
        "id","name","price","stock",
        "image1","image2","image3",
        "video","description","status"
    ])
    rows = []
    for i, r in enumerate(records, start=2):
        r["_row"] = i
        rows.append(r)
    return pd.DataFrame(rows)

def load_orders():
    records = orders_sheet.get_all_records(expected_headers=[
        "name","phone","location","items",
        "qty","amount","reference","timestamp","status"
    ])
    rows = []
    for i, r in enumerate(records, start=2):
        r["_row"] = i
        rows.append(r)
    return pd.DataFrame(rows)

products_df = load_products()

# ---------------- TRACK VISIT (ONCE PER SESSION) ----------------
if not st.session_state.visit_tracked and not st.session_state.admin_logged:
    track_visit()
    st.session_state.visit_tracked = True

# ==============================
# MEGA HEADER WITH EMBLEM
# ==============================
st.markdown("""
<div class='mega-header'>
    <div class='header-content'>
        <div class='logo-emblem'>
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <!-- Shield Background -->
                <path d="M50 10 L85 25 L85 50 Q85 75 50 90 Q15 75 15 50 L15 25 Z" 
                      fill="url(#gradient1)" stroke="#ff6b35" stroke-width="3"/>
                
                <!-- Gradient Definition -->
                <defs>
                    <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" style="stop-color:#ff6b35;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#f7931e;stop-opacity:1" />
                    </linearGradient>
                </defs>
                
                <!-- RJ Letters -->
                <text x="50" y="60" font-family="Orbitron" font-size="35" font-weight="900" 
                      fill="white" text-anchor="middle">RJ</text>
                
                <!-- Star Accent -->
                <path d="M50 25 L52 32 L59 32 L53 37 L55 44 L50 39 L45 44 L47 37 L41 32 L48 32 Z" 
                      fill="white" opacity="0.8"/>
            </svg>
        </div>
        <div class='header-text'>
            <h1 class='store-name'>RETRO JERSEY SHOP</h1>
            <p class='store-tagline'>Authentic Vintage Jerseys • Premium Quality</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='content-wrapper'>", unsafe_allow_html=True)

# ==============================
# ADMIN LOGIN
# ==============================
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-container' style='max-width:500px; margin:80px auto;'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Login")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login to Dashboard", use_container_width=True):
        if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
            st.session_state.admin_logged = True
            st.session_state.show_admin_login = False
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("← Back to Shop"):
        st.session_state.show_admin_login = False
        st.rerun()
    
    st.stop()

# ==============================
# ADMIN DASHBOARD
# ==============================
if st.session_state.admin_logged:
    
    st.markdown("<h1 style='text-align:center; font-size:48px; margin-bottom:40px;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged = False
            st.rerun()
    
    # Load orders
    orders_df = load_orders()
    
    # Calculate approved revenue only
    approved_orders = orders_df[orders_df['status'] == 'Approved']
    approved_revenue = approved_orders['amount'].sum() if not approved_orders.empty else 0
    visit_count = get_visit_count()
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(products_df)}</div>
            <div class='stat-label'>Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(orders_df)}</div>
            <div class='stat-label'>Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>GHS {approved_revenue:,.0f}</div>
            <div class='stat-label'>Revenue</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{visit_count}</div>
            <div class='stat-label'>Visits</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ADD PRODUCT
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### ➕ Add New Product")
    with st.form("add_product"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Product Name *")
            price = st.number_input("Price (GHS) *", min_value=0)
        with col2:
            stock = st.number_input("Stock Quantity *", min_value=0)
            
        desc = st.text_area("Product Description")
        images = st.file_uploader(
            "Upload Product Images (Up to 3)",
            type=["png","jpg","jpeg"],
            accept_multiple_files=True
        )
        video = st.file_uploader(
            "Upload Product Video (Optional)",
            type=["mp4","mov","avi"]
        )
        add = st.form_submit_button("Add Product", use_container_width=True)
        
        if add and name and images:
            image_urls = []
            video_url = ""
            
            with st.spinner("☁️ Uploading to Cloudinary..."):
                # Upload images
                for idx, img in enumerate(images[:3], 1):
                    filename = f"{name.replace(' ', '_')}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    url = upload_to_cloudinary(img, filename, "image")
                    
                    if url:
                        image_urls.append(url)
                        st.success(f"✅ Image {idx} uploaded")
                    else:
                        st.error(f"❌ Failed to upload image {idx}")
                        st.stop()
                
                # Upload video if provided
                if video:
                    video_filename = f"{name.replace(' ', '_')}_video_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
                    video_url = upload_to_cloudinary(video, video_filename, "video")
                    if video_url:
                        st.success("✅ Video uploaded")
            
            while len(image_urls) < 3:
                image_urls.append("")
            
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            status = "In Stock" if stock > 0 else "Out of Stock"
            
            products_sheet.append_row([
                new_id, name, price, stock,
                image_urls[0], image_urls[1], image_urls[2],
                video_url, desc, status
            ])
            
            st.success("✅ Product added successfully!")
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # MANAGE PRODUCTS
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Manage Products")
    products_df = load_products()
    
    if not products_df.empty:
        cols = st.columns(3)
        for idx, row in products_df.iterrows():
            with cols[idx % 3]:
                st.image(row["image1"], use_column_width=True)
                st.markdown(f"**{row['name']}**")
                st.markdown(f"Stock: {row['stock']} | GHS {row['price']}")
                
                if st.button(f"Delete", key=f"del_{row['id']}", use_container_width=True):
                    # Delete media from Cloudinary
                    for img_col in ['image1', 'image2', 'image3', 'video']:
                        media_url = row.get(img_col, '')
                        if media_url and 'cloudinary.com' in media_url:
                            delete_from_cloudinary(media_url)
                    
                    products_sheet.delete_rows(row["_row"])
                    st.success("Product deleted!")
                    st.rerun()
    else:
        st.info("No products yet")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ORDERS MANAGEMENT
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 📦 Orders Management")
    
    if not orders_df.empty:
        for idx, order in orders_df.iterrows():
            with st.expander(f"📦 {order['reference']} - {order['name']} - GHS {order['amount']} - Status: {order['status']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    **Customer:** {order['name']}<br>
                    **Phone:** {order['phone']}<br>
                    **Location:** {order['location']}<br>
                    **Product:** {order['items']}<br>
                    **Quantity:** {order['qty']}<br>
                    **Amount:** GHS {order['amount']}<br>
                    **Reference:** {order['reference']}<br>
                    **Time:** {order['timestamp']}
                    """, unsafe_allow_html=True)
                
                with col2:
                    if order['status'] == 'Pending':
                        if st.button("✅ Approve Order", key=f"approve_{idx}", use_container_width=True):
                            # Update status to Approved
                            orders_sheet.update_cell(order["_row"], 9, "Approved")
                            st.success("✅ Order approved! Revenue updated.")
                            st.rerun()
                    else:
                        st.success("✅ Approved")
    else:
        st.info("No orders yet")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # SETUP GUIDES
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 🔧 Setup Guides")
    
    tab1, tab2, tab3 = st.tabs(["☁️ Cloudinary", "📱 Telegram", "📧 Email"])
    
    with tab1:
        st.markdown("""
        **Cloudinary Setup (5 minutes)**
        
        1. Sign up at [cloudinary.com](https://cloudinary.com)
        2. Go to Dashboard
        3. Copy these credentials:
           - Cloud Name
           - API Key
           - API Secret
        4. Add to Render Environment Variables:
           - `CLOUDINARY_CLOUD_NAME`
           - `CLOUDINARY_API_KEY`
           - `CLOUDINARY_API_SECRET`
        5. Free tier: 25GB storage + 25GB bandwidth/month
        """)
    
    with tab2:
        st.markdown("""
        **Telegram Bot Setup (5 minutes)**
        
        1. Open Telegram, search `@BotFather`
        2. Send `/newbot`
        3. Name: "Store Alerts"
        4. Username: "yourstore_bot"
        5. Copy the TOKEN
        6. Search `@userinfobot`
        7. Send any message to get your Chat ID
        8. Add to Render:
           - `TELEGRAM_BOT_TOKEN`
           - `TELEGRAM_CHAT_ID`
        9. Send `/start` to your bot
        """)
    
    with tab3:
        st.markdown("""
        **Gmail Setup (5 minutes)**
        
        1. Go to [Google Account Security](https://myaccount.google.com/security)
        2. Enable 2-Step Verification
        3. Go to App passwords
        4. Select Mail → Generate
        5. Copy the 16-character password
        6. Add to Render:
           - `ADMIN_EMAIL` = your_email@gmail.com
           - `EMAIL_APP_PASSWORD` = the 16-char code
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ==============================
# PUBLIC SHOP
# ==============================

# Small admin button
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    if st.button("🔐 Admin", key="admin_btn"):
        st.session_state.show_admin_login = True
        st.rerun()

# FLOATING AD BANNER
st.markdown("""
<div class='ad-banner'>
    <div class='ad-title'>🔥 FLASH SALE ALERT! 🔥</div>
    <div class='ad-text'>Get 20% OFF on all vintage jerseys this weekend! Limited stock available. Order now!</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-header'>⚡ Featured Products</div>", unsafe_allow_html=True)

if products_df.empty:
    st.info("🏗️ No products available. Check back soon!")
else:
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            badge_class = "badge-in-stock" if row["status"] == "In Stock" else "badge-out-stock"
            
            # Check if video exists
            has_video = row.get("video", "") and 'cloudinary.com' in str(row.get("video", ""))
            
            if has_video:
                media_html = f"<video src='{row['video']}' autoplay loop muted playsinline style='width:100%;height:100%;object-fit:contain;'></video>"
            else:
                media_html = f"<img src='{row['image1']}' alt='{row['name']}'>"
            
            st.markdown(f"""
            <div class='product-card'>
                <div class='product-image-wrapper'>
                    {media_html}
                    <div class='stock-badge {badge_class}'>{row["status"]}</div>
                </div>
                <div class='product-info'>
                    <div class='product-title'>{row['name']}</div>
                    <div class='product-description'>{row['description']}</div>
                    <div class='product-price'>GHS {row['price']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if row["status"] == "Out of Stock":
                st.button("Unavailable", key=f"out_{row['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 Add to Cart", key=f"order_{row['id']}", use_container_width=True):
                    st.session_state.selected = row

# ==============================
# ORDER FORM
# ==============================
if "selected" in st.session_state:
    p = st.session_state.selected
    
    st.markdown("<div class='admin-container' style='max-width:800px; margin:50px auto;'>", unsafe_allow_html=True)
    st.markdown(f"### 🛒 Checkout")
    st.markdown(f"**Product:** {p['name']}")
    
    with st.form("order"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone / WhatsApp *")
        with col2:
            location = st.text_input("Delivery Location *")
            qty = st.number_input("Quantity *", min_value=1, value=1)
        
        total = int(p["price"]) * int(qty)
        
        st.markdown(f"""
        <div style='background:#f8f9fa; padding:20px; border-radius:15px; margin-top:20px;'>
            <strong style='font-size:18px;'>Order Summary</strong><br><br>
            <strong>Item:</strong> {p['name']}<br>
            <strong>Quantity:</strong> {qty}<br>
            <strong style='font-size:24px; color:#ff6b35;'>Total: GHS {total}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        send = st.form_submit_button("🚀 Place Order", use_container_width=True)
        
        if send and name and phone and location:
            reference = generate_reference(p["name"], location)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            orders_sheet.append_row([
                name, phone, location, p["name"],
                qty, total, reference, timestamp, "Pending"
            ])
            
            # Notifications
            telegram_msg = f"""🛒 <b>NEW ORDER!</b>

📦 <b>Product:</b> {p['name']}
👤 <b>Customer:</b> {name}
📱 <b>Phone:</b> {phone}
📍 <b>Location:</b> {location}
🔢 <b>Qty:</b> {qty}
💰 <b>Total:</b> GHS {total}
🔖 <b>Ref:</b> {reference}
⏰ <b>Time:</b> {timestamp}

Status: ⏳ Pending"""
            
            telegram_sent = send_telegram_notification(telegram_msg)
            
            email_subject = f"🛒 New Order: {reference}"
            email_body = f"""
            <html><body style='font-family:Arial,sans-serif;'>
                <h2 style='color:#ff6b35;'>New Order Received!</h2>
                <table style='border-collapse:collapse;width:100%;'>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Product:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{p['name']}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Customer:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{name}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Phone:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{phone}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Location:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{location}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Quantity:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{qty}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Total:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>GHS {total}</td></tr>
                    <tr><td style='padding:10px;border-bottom:1px solid #ddd;'><strong>Reference:</strong></td><td style='padding:10px;border-bottom:1px solid #ddd;'>{reference}</td></tr>
                </table>
                <p style='margin-top:20px;color:#666;'>Status: Pending</p>
            </body></html>
            """
            
            email_sent = send_email_notification(email_subject, email_body)
            
            notif_info = []
            if telegram_sent:
                notif_info.append("Telegram")
            if email_sent:
                notif_info.append("Email")
            notif_text = f" (Notified via {', '.join(notif_info)})" if notif_info else ""
            
            st.markdown(f"""
            <div class='success-message'>
                <h3 style='margin:0 0 15px 0;'>✅ Order Placed Successfully!{notif_text}</h3>
                <p style='margin:0; font-size:16px;'>Thank you for your order! We'll contact you shortly to confirm delivery.</p>
                <p style='margin:15px 0 0 0;'><strong style='font-size:20px;'>Order Total: GHS {total}</strong></p>
                <p style='margin:10px 0 0 0;'><strong>Reference:</strong> {reference}</p>
            </div>
            """, unsafe_allow_html=True)
            
            del st.session_state.selected
    
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div class='footer-section'>
    <div class='footer-links'>
        <a href='tel:0541468102' class='footer-link'>📞 0541468102</a>
        <span style='color:#666;'>|</span>
        <a href='#' class='footer-link'>📱 Snapchat: @retroshop</a>
        <span style='color:#666;'>|</span>
        <a href='#' class='footer-link'>📍 Accra, Ghana</a>
    </div>
    <div class='footer-copyright' style='color:#999; font-size:14px; margin-top:25px;'>
        © 2026 Retro Jersey Shop • All Rights Reserved • Powered by Cloudinary
    </div>
</div>
""", unsafe_allow_html=True)
