# ========================================== 
# RETRO JERSEY SHOP - PROFESSIONAL EDITION 
# Enhanced UI, SEO-Optimized, Mobile-First, Ultra-Fast
# ========================================== 
import streamlit as st
import gspread, pandas as pd, os, json, random, requests, smtplib
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cloudinary, cloudinary.uploader
from urllib.parse import quote
import threading
import time

# Must be first Streamlit command
st.set_page_config(
    page_title="Retro Jersey Shop Ghana | Premium Vintage Football Jerseys",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Retro Jersey Shop - Ghana's #1 destination for authentic vintage football jerseys 🇬🇭"
    }
)

# Cloudinary Setup with optimization
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
    secure=True
)

def generate_reference(product_name, location):
    return f"RJ-{product_name[:3].upper()}-{location[:3].upper()}-{random.randint(1000, 9999)}"

def upload_to_cloudinary(file, filename, resource_type="image"):
    try:
        file.seek(0)
        transformations = {
            "image": [
                {'width': 800, 'height': 800, 'crop': 'limit', 'quality': 'auto:good', 'fetch_format': 'auto'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ],
            "video": [
                {'width': 640, 'height': 640, 'crop': 'limit'},
                {'quality': 'auto:low'},
                {'video_codec': 'h264'},
                {'bit_rate': '500k'}
            ]
        }
        result = cloudinary.uploader.upload(
            file,
            public_id=f"RetroJerseyShop/{filename.rsplit('.', 1)[0]}",
            overwrite=True,
            resource_type=resource_type,
            transformation=transformations.get(resource_type, [])
        )
        return result.get('secure_url')
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def delete_from_cloudinary(media_url):
    try:
        if 'cloudinary.com' in media_url:
            parts = media_url.split('/')
            public_id = '/'.join(parts[parts.index('upload') + 2:]).rsplit('.', 1)[0]
            resource_type = "video" if any(ext in media_url for ext in ['.mp4', '.mov']) else "image"
            return cloudinary.uploader.destroy(public_id, resource_type=resource_type).get('result') == 'ok'
    except:
        pass
    return False

# ASYNC NOTIFICATION FUNCTIONS - Non-blocking
def send_notifications_async(telegram_msg, email_subject, email_body):
    def _send():
        try:
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            if token and chat_id:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": telegram_msg, "parse_mode": "HTML"},
                    timeout=5
                )
            
            admin_email = os.environ.get("ADMIN_EMAIL")
            password = os.environ.get("EMAIL_APP_PASSWORD")
            if admin_email and password:
                msg = MIMEMultipart('alternative')
                msg['From'] = admin_email
                msg['To'] = admin_email
                msg['Subject'] = email_subject
                msg.attach(MIMEText(email_body, 'html'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.set_debuglevel(0)
                server.starttls()
                server.login(admin_email, password)
                server.send_message(msg)
                server.quit()
        except:
            pass
    
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

def get_share_url(product_name, product_price, product_image):
    base_url = "https://retrogh.shop"
    text = f"Check out {product_name} - Only GHS {product_price}!"
    return {
        "whatsapp": f"https://wa.me/?text={quote(text + ' ' + base_url)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={quote(base_url)}",
        "twitter": f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(base_url)}",
        "telegram": f"https://t.me/share/url?url={quote(base_url)}&text={quote(text)}"
    }

# ==========================================
# ENHANCED SEO & PERFORMANCE META TAGS
# ==========================================
st.markdown("""
    <!-- Critical Preconnect for Performance -->
    <link rel="preconnect" href="https://res.cloudinary.com" crossorigin>
    <link rel="dns-prefetch" href="https://res.cloudinary.com">
    
    <!-- Mobile & Responsive -->
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <meta name="theme-color" content="#667eea">
    
    <!-- Primary SEO -->
    <meta name="description" content="Buy authentic vintage football jerseys in Ghana. Premium quality retro jerseys from Manchester United, Real Madrid, Barcelona & more. Fast delivery in Accra, Kumasi & across Ghana. Shop now!">
    <meta name="keywords" content="retro jerseys ghana, vintage football shirts ghana, classic jerseys accra, football jerseys ghana, retro soccer jerseys, buy jerseys ghana, vintage sports wear accra, premier league jerseys ghana">
    <meta name="author" content="Retro Jersey Shop Ghana">
    <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
    <link rel="canonical" href="https://retrogh.shop/">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://retrogh.shop/">
    <meta property="og:title" content="Retro Jersey Shop Ghana | Premium Vintage Football Jerseys">
    <meta property="og:description" content="Ghana's #1 destination for authentic vintage football jerseys. Premium quality, fast delivery nationwide. Shop Manchester United, Real Madrid, Barcelona retro kits!">
    <meta property="og:image" content="https://res.cloudinary.com/your-cloud/image/upload/v1/RetroJerseyShop/og-image.jpg">
    <meta property="og:locale" content="en_GH">
    <meta property="og:site_name" content="Retro Jersey Shop">
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://retrogh.shop/">
    <meta name="twitter:title" content="Retro Jersey Shop Ghana | Premium Vintage Football Jerseys">
    <meta name="twitter:description" content="Ghana's #1 destination for authentic vintage football jerseys. Premium quality, fast delivery nationwide.">
    <meta name="twitter:image" content="https://res.cloudinary.com/your-cloud/image/upload/v1/RetroJerseyShop/og-image.jpg">
    
    <!-- Structured Data for Google -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SportsActivityLocation",
      "name": "Retro Jersey Shop Ghana",
      "description": "Premium vintage football jerseys in Ghana",
      "url": "https://retrogh.shop",
      "telephone": "+233541468102",
      "address": {
        "@type": "PostalAddress",
        "addressLocality": "Accra",
        "addressCountry": "GH"
      },
      "priceRange": "GHS 100-500",
      "openingHours": "Mo-Sa 08:00-18:00"
    }
    </script>
    
    <!-- Favicon -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚽</text></svg>">
    
    <!-- Performance: Preload Critical Resources -->
    <link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap">
""", unsafe_allow_html=True)

# Session State
for key in ["admin_logged", "show_admin_login", "visit_tracked", "loading", "cart"]:
    if key not in st.session_state:
        st.session_state[key] = False if key != "cart" else []

if "page" in st.query_params and st.query_params["page"] == "admin":
    st.session_state.show_admin_login = True

# ==========================================
# HIDE STREAMLIT BRANDING - CLEAN UI
# ==========================================
st.markdown("""<style>
    /* Aggressive Streamlit UI Removal */
    #MainMenu, footer, header, .stDeployButton, 
    .viewerBadge_container__1QSob, .styles_viewerBadge__1yB5_,
    [data-testid="stToolbar"], [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
</style>""", unsafe_allow_html=True)

# ==========================================
# PROFESSIONAL THEME - MOBILE FIRST
# ==========================================
st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        background-attachment: fixed;
    }
    
    /* ==========================================
       PROFESSIONAL HEADER
       ========================================== */
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.8rem;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 20px 20px;
        opacity: 0.3;
    }
    
    .logo-container {
        position: relative;
        z-index: 1;
    }
    
    .logo {
        width: 50px;
        height: 50px;
        background: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.2rem;
        color: #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        flex-shrink: 0;
        transform: rotate(-3deg);
        transition: transform 0.3s ease;
    }
    
    .logo:hover {
        transform: rotate(0deg) scale(1.05);
    }
    
    .brand-container {
        position: relative;
        z-index: 1;
        flex: 1;
    }
    
    .brand {
        font-size: 1.3rem;
        font-weight: 800;
        color: white;
        line-height: 1.2;
        letter-spacing: -0.02em;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .brand-subtitle {
        font-size: 0.75rem;
        opacity: 0.95;
        color: rgba(255,255,255,0.9);
        margin-top: 4px;
        font-weight: 500;
    }
    
    /* Mobile optimizations */
    @media (max-width: 480px) {
        .header {
            padding: 0.8rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .logo {
            width: 45px;
            height: 45px;
            font-size: 1rem;
        }
        .brand {
            font-size: 1.1rem;
        }
        .brand-subtitle {
            font-size: 0.7rem;
        }
    }
    
    @media (min-width: 768px) {
        .header {
            padding: 1.5rem;
            gap: 1.2rem;
        }
        .logo {
            width: 60px;
            height: 60px;
            font-size: 1.4rem;
        }
        .brand {
            font-size: 1.8rem;
        }
        .brand-subtitle {
            font-size: 0.9rem;
        }
    }
    
    /* ==========================================
       FLASH SALE BANNER
       ========================================== */
    .flash-sale {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 50%, #f093fb 100%);
        background-size: 200% auto;
        color: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 700;
        margin: 1rem 0 1.5rem 0;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
        animation: shimmer 3s linear infinite;
        border: 2px solid rgba(255,255,255,0.3);
    }
    
    @keyframes shimmer {
        to { background-position: 200% center; }
    }
    
    .flash-sale-text {
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    @media (min-width: 768px) {
        .flash-sale {
            padding: 1.2rem;
            font-size: 1.2rem;
        }
    }
    
    /* ==========================================
       SECTION TITLES
       ========================================== */
    .section-title {
        font-size: 1.5rem;
        font-weight: 800;
        color: #1a202c;
        margin: 2rem 0 1rem 0;
        text-align: center;
        position: relative;
        display: inline-block;
        width: 100%;
    }
    
    .section-title::after {
        content: '';
        display: block;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        margin: 0.5rem auto 0;
        border-radius: 2px;
    }
    
    @media (min-width: 768px) {
        .section-title {
            font-size: 2rem;
            margin: 2.5rem 0 1.5rem 0;
        }
    }
    
    /* ==========================================
       PRODUCT CARDS - MODERN GLASSMORPHISM
       ========================================== */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        padding: 0.5rem;
    }
    
    .product-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 10px 20px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255,255,255,0.5);
        backdrop-filter: blur(10px);
        position: relative;
    }
    
    .product-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 40px rgba(102, 126, 234, 0.2);
    }
    
    .product-image-container {
        position: relative;
        width: 100%;
        padding-top: 100%; /* 1:1 Aspect Ratio */
        overflow: hidden;
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
    }
    
    .product-image {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }
    
    .product-card:hover .product-image {
        transform: scale(1.05);
    }
    
    .badge {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        z-index: 2;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .badge-in-stock {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
    }
    
    .badge-out-stock {
        background: linear-gradient(135deg, #f56565, #e53e3e);
        color: white;
    }
    
    .product-content {
        padding: 1.2rem;
    }
    
    .product-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.5rem;
        line-height: 1.3;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .product-desc {
        color: #718096;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
        line-height: 1.5;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    
    .product-price {
        font-size: 1.4rem;
        color: #667eea;
        font-weight: 800;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .product-price::before {
        content: 'GHS';
        font-size: 0.8rem;
        color: #a0aec0;
        font-weight: 600;
    }
    
    /* Mobile optimizations */
    @media (max-width: 480px) {
        .product-grid {
            grid-template-columns: repeat(2, 1fr);
            gap: 0.8rem;
        }
        .product-content {
            padding: 0.8rem;
        }
        .product-name {
            font-size: 0.9rem;
        }
        .product-price {
            font-size: 1.1rem;
        }
    }
    
    /* ==========================================
       CAROUSEL CONTROLS
       ========================================== */
    .carousel-container {
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(0,0,0,0.6);
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        backdrop-filter: blur(10px);
    }
    
    .carousel-btn {
        background: rgba(255,255,255,0.9);
        border: none;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 0.8rem;
        color: #333;
        transition: all 0.2s;
    }
    
    .carousel-btn:hover {
        background: white;
        transform: scale(1.1);
    }
    
    .carousel-indicator {
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        min-width: 30px;
        text-align: center;
    }
    
    /* ==========================================
       BUTTONS - MODERN STYLING
       ========================================== */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    .stButton > button:disabled {
        background: #cbd5e0 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: none !important;
    }
    
    /* Secondary button style */
    .secondary-btn > button {
        background: white !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
    }
    
    /* ==========================================
       FORMS - CLEAN INPUTS
       ========================================== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: white !important;
        color: #1a202c !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 0.9rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
        outline: none !important;
    }
    
    .stTextInput > label,
    .stNumberInput > label,
    .stTextArea > label {
        color: #2d3748 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* ==========================================
       ADMIN DASHBOARD - CLEAN CARDS
       ========================================== */
    .admin-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.5);
    }
    
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin-bottom: 2rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem 1rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .stat-box:hover {
        transform: translateY(-3px);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.85rem;
        opacity: 0.9;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* ==========================================
       ORDER SUCCESS - CELEBRATION
       ========================================== */
    .order-success {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 2.5rem 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 40px rgba(72, 187, 120, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .order-success::before {
        content: '🎉';
        position: absolute;
        top: -20px;
        right: -20px;
        font-size: 100px;
        opacity: 0.2;
        transform: rotate(15deg);
    }
    
    .order-success-title {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 1rem;
        position: relative;
        z-index: 1;
    }
    
    .order-success-details {
        font-size: 1rem;
        opacity: 0.95;
        line-height: 1.6;
        position: relative;
        z-index: 1;
    }
    
    /* ==========================================
       LOADING OVERLAY - SMOOTH ANIMATION
       ========================================== */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.98);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(10px);
    }
    
    .loading-spinner {
        width: 60px;
        height: 60px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1.5rem;
        font-size: 1.1rem;
        color: #667eea;
        font-weight: 600;
    }
    
    /* ==========================================
       FOOTER - PROFESSIONAL
       ========================================== */
    .footer {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 20px 20px 0 0;
        margin-top: 3rem;
        text-align: center;
        position: relative;
    }
    
    .footer-content {
        max-width: 600px;
        margin: 0 auto;
    }
    
    .footer-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        color: #fff;
    }
    
    .footer-contact {
        font-size: 0.95rem;
        margin-bottom: 1rem;
        line-height: 1.8;
        color: #cbd5e0;
    }
    
    .footer-contact a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
        transition: color 0.3s;
    }
    
    .footer-contact a:hover {
        color: #764ba2;
        text-decoration: underline;
    }
    
    .footer-social {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .social-link {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.1);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        text-decoration: none;
        transition: all 0.3s;
        font-size: 1.2rem;
    }
    
    .social-link:hover {
        background: #667eea;
        transform: translateY(-3px);
    }
    
    .footer-copyright {
        font-size: 0.8rem;
        opacity: 0.7;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }
    
    @media (min-width: 768px) {
        .footer {
            padding: 3rem 2rem;
        }
    }
    
    /* ==========================================
       UTILITY CLASSES
       ========================================== */
    .text-center { text-align: center; }
    .mb-1 { margin-bottom: 0.5rem; }
    .mb-2 { margin-bottom: 1rem; }
    .mt-2 { margin-top: 1rem; }
    
    /* Hide file uploader drag text */
    .uploadedFile {
        display: none;
    }
    
    /* Custom file upload button */
    .stFileUploader > div > button {
        background: white !important;
        color: #667eea !important;
        border: 2px dashed #cbd5e0 !important;
        border-radius: 12px !important;
        padding: 2rem !important;
        width: 100% !important;
    }
    
    .stFileUploader > div > button:hover {
        border-color: #667eea !important;
        background: #f7fafc !important;
    }
</style>""", unsafe_allow_html=True)

# ==========================================
# OPTIMIZED GOOGLE SHEETS CONNECTION
# ==========================================
@st.cache_resource(ttl=3600)
def get_sheets_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.environ.get("GCP_SERVICE_ACCOUNT")), 
            scope
        )
        return gspread.authorize(creds)
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        st.stop()

@st.cache_data(ttl=300, show_spinner=False)  # 5 min cache for freshness
def load_products():
    try:
        client = get_sheets_client()
        sheet = client.open("retro_jersey_shop").worksheet("products")
        records = sheet.get_all_records()
        for i, r in enumerate(records, start=2):
            r["_row"] = i
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"Failed to load products: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=120, show_spinner=False)
def load_orders():
    try:
        client = get_sheets_client()
        sheet = client.open("retro_jersey_shop").worksheet("orders")
        records = sheet.get_all_records()
        for i, r in enumerate(records, start=2):
            r["_row"] = i
        return pd.DataFrame(records)
    except:
        return pd.DataFrame()

# ==========================================
# HEADER COMPONENT
# ==========================================
st.markdown("""
<div class='header'>
    <div class='logo-container'>
        <div class='logo'>RJ</div>
    </div>
    <div class='brand-container'>
        <div class='brand'>RETRO JERSEY SHOP</div>
        <div class='brand-subtitle'>Ghana's Premium Vintage Football Collection ⚽</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Admin Login Toggle
col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🔐", key="admin_toggle", help="Admin Login"):
        st.session_state.show_admin_login = not st.session_state.show_admin_login
        st.rerun()

# ==========================================
# ADMIN PANEL
# ==========================================
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Access")
    
    with st.form("admin_login"):
        password = st.text_input("Password", type="password", placeholder="Enter admin password")
        cols = st.columns([1, 1])
        with cols[0]:
            if st.form_submit_button("Login", use_container_width=True):
                if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
                    st.session_state.admin_logged = True
                    st.session_state.show_admin_login = False
                    st.cache_data.clear()
                    st.success("✅ Access granted!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Invalid password")
        with cols[1]:
            if st.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_admin_login = False
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

if st.session_state.admin_logged:
    st.markdown("<div class='section-title'>📊 Admin Dashboard</div>", unsafe_allow_html=True)
    
    # Stats
    products_df = load_products()
    orders_df = load_orders()
    approved_revenue = orders_df[orders_df['status'] == 'Approved']['amount'].sum() if not orders_df.empty else 0
    
    st.markdown(f"""
    <div class='stat-grid'>
        <div class='stat-box'>
            <div class='stat-number'>{len(products_df)}</div>
            <div class='stat-label'>Products</div>
        </div>
        <div class='stat-box'>
            <div class='stat-number'>{len(orders_df)}</div>
            <div class='stat-label'>Orders</div>
        </div>
        <div class='stat-box'>
            <div class='stat-number'>GHS {approved_revenue:,.0f}</div>
            <div class='stat-label'>Revenue</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged = False
            st.cache_data.clear()
            st.rerun()
    
    # Add Product
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### ➕ Add New Product")
    
    with st.form("add_product", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Product Name *", placeholder="e.g., Man Utd 1999 Retro")
        price = col1.number_input("Price (GHS) *", min_value=0, value=150)
        stock = col2.number_input("Stock Quantity *", min_value=0, value=10)
        desc = st.text_area("Description", placeholder="Describe the jersey, material, size availability...")
        
        st.markdown("**Media Upload**")
        col_img, col_vid = st.columns(2)
        with col_img:
            images = st.file_uploader("Images (Max 3)", type=["png","jpg","jpeg"], accept_multiple_files=True)
        with col_vid:
            video = st.file_uploader("Video (Optional)", type=["mp4","mov"])
        
        if st.form_submit_button("🚀 Add Product", use_container_width=True):
            if name and images:
                with st.spinner("Uploading..."):
                    image_urls, video_url = [], ""
                    for idx, img in enumerate(images[:3], 1):
                        url = upload_to_cloudinary(img, f"{name.replace(' ', '_')}_{idx}_{int(time.time())}.jpg")
                        if url:
                            image_urls.append(url)
                    if video:
                        video_url = upload_to_cloudinary(video, f"{name.replace(' ', '_')}_video.mp4", "video")
                    
                    while len(image_urls) < 3:
                        image_urls.append("")
                    
                    try:
                        client = get_sheets_client()
                        sheet = client.open("retro_jersey_shop").worksheet("products")
                        new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
                        sheet.append_row([new_id, name, price, stock, *image_urls, video_url, desc, "In Stock" if stock > 0 else "Out of Stock"])
                        st.cache_data.clear()
                        st.success("✅ Product added successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
            else:
                st.warning("⚠️ Please provide product name and at least one image")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Manage Products
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Manage Products")
    
    if not products_df.empty:
        for idx in range(0, len(products_df), 3):
            cols = st.columns(3)
            for i, col in enumerate(cols):
                if idx + i < len(products_df):
                    row = products_df.iloc[idx + i]
                    with col:
                        if row.get("image1") and str(row["image1"]).strip():
                            st.image(row["image1"], use_container_width=True)
                        else:
                            st.info("No image")
                        st.markdown(f"**{row['name']}**")
                        st.markdown(f"<span style='color:#667eea;font-weight:700;'>GHS {row['price']}</span>", unsafe_allow_html=True)
                        st.caption(f"Stock: {row.get('stock', 0)}")
                        
                        if st.button("🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                            for col_name in ['image1', 'image2', 'image3', 'video']:
                                if row.get(col_name) and 'cloudinary.com' in str(row[col_name]):
                                    delete_from_cloudinary(row[col_name])
                            try:
                                client = get_sheets_client()
                                sheet = client.open("retro_jersey_shop").worksheet("products")
                                sheet.delete_rows(row["_row"])
                                st.cache_data.clear()
                                st.success("Deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    else:
        st.info("No products found")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Orders Management
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 📦 Recent Orders")
    
    if not orders_df.empty:
        for idx, order in orders_df.iterrows():
            status_color = "#48bb78" if order['status'] == 'Approved' else "#ed8936"
            with st.expander(f"📦 {order['reference']} - {order['name']} - GHS {order['amount']} - <span style='color:{status_color}'>{order['status']}</span>"):
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
                        **Date:** {order['timestamp']}
                    """, unsafe_allow_html=True)
                with col2:
                    # WhatsApp contact
                    clean_phone = ''.join(filter(str.isdigit, str(order['phone'])))
                    if not clean_phone.startswith('233'):
                        clean_phone = '233' + clean_phone.lstrip('0')
                    
                    msg = f"Hi {order['name']}! Your order {order['reference']} for {order['items']} (GHS {order['amount']}) is confirmed!"
                    wa_url = f"https://wa.me/{clean_phone}?text={quote(msg)}"
                    
                    st.markdown(f"""
                        <a href="{wa_url}" target="_blank" style="display:block;background:#25D366;color:white;padding:10px;border-radius:8px;text-align:center;text-decoration:none;margin-bottom:10px;font-weight:600;">
                            📱 WhatsApp Customer
                        </a>
                    """, unsafe_allow_html=True)
                    
                    if order['status'] == 'Pending':
                        if st.button("✅ Approve", key=f"app_{idx}", use_container_width=True):
                            try:
                                client = get_sheets_client()
                                sheet = client.open("retro_jersey_shop").worksheet("orders")
                                sheet.update_cell(order["_row"], 9, "Approved")
                                st.cache_data.clear()
                                st.success("Approved!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    else:
        st.info("No orders yet")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# PUBLIC SHOP - OPTIMIZED UI
# ==========================================
products_df = load_products()

# Flash Sale Banner
st.markdown("""
<div class='flash-sale'>
    <div class='flash-sale-text'>🔥 FLASH SALE: 20% OFF THIS WEEKEND ONLY! 🔥</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>⚡ Featured Collection</div>", unsafe_allow_html=True)

# Search/Filter (SEO friendly)
search_col, filter_col = st.columns([3, 1])
with search_col:
    search_term = st.text_input("🔍 Search jerseys...", placeholder="Search by team, player, or year...", label_visibility="collapsed")
with filter_col:
    sort_by = st.selectbox("Sort by", ["Newest", "Price: Low to High", "Price: High to Low"], label_visibility="collapsed")

# Filter products
if not products_df.empty:
    filtered_df = products_df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]
    
    if sort_by == "Price: Low to High":
        filtered_df = filtered_df.sort_values('price')
    elif sort_by == "Price: High to Low":
        filtered_df = filtered_df.sort_values('price', ascending=False)
    
    if filtered_df.empty:
        st.info("No products found matching your search.")
    else:
        # Responsive Grid
        for idx in range(0, len(filtered_df), 3):
            cols = st.columns(3)
            for i, col in enumerate(cols):
                if idx + i < len(filtered_df):
                    row = filtered_df.iloc[idx + i]
                    with col:
                        images = [row.get(f"image{i}", "") for i in range(1, 4) if row.get(f"image{i}")]
                        video = row.get("video", "")
                        
                        carousel_key = f"carousel_{row['id']}"
                        if carousel_key not in st.session_state:
                            st.session_state[carousel_key] = 0
                        
                        badge_class = "badge-in-stock" if row["status"] == "In Stock" else "badge-out-stock"
                        
                        # Media display with lazy loading
                        if video and 'cloudinary.com' in str(video):
                            media_html = f"""
                                <div class='product-image-container'>
                                    <video class='product-image' controls loading='lazy' poster='{images[0] if images else ''}'>
                                        <source src='{video}' type='video/mp4'>
                                    </video>
                                    <div class='badge {badge_class}'>{row['status']}</div>
                                </div>
                            """
                        else:
                            current_img = images[st.session_state[carousel_key]] if images else ""
                            media_html = f"""
                                <div class='product-image-container'>
                                    <img src='{current_img}' class='product-image' loading='lazy' alt='{row['name']}' width='400' height='400'>
                                    <div class='badge {badge_class}'>{row['status']}</div>
                                </div>
                            """
                        
                        st.markdown(f"<div class='product-card'>{media_html}", unsafe_allow_html=True)
                        
                        # Carousel controls
                        if len(images) > 1:
                            col_l, col_m, col_r = st.columns([1, 2, 1])
                            with col_l:
                                if st.button("◀", key=f"prev_{row['id']}", use_container_width=True):
                                    st.session_state[carousel_key] = (st.session_state[carousel_key] - 1) % len(images)
                                    st.rerun()
                            with col_m:
                                st.markdown(f"<div style='text-align:center;font-size:0.8rem;color:#718096;padding-top:5px;'>{st.session_state[carousel_key] + 1}/{len(images)}</div>", unsafe_allow_html=True)
                            with col_r:
                                if st.button("▶", key=f"next_{row['id']}", use_container_width=True):
                                    st.session_state[carousel_key] = (st.session_state[carousel_key] + 1) % len(images)
                                    st.rerun()
                        
                        st.markdown(f"""
                            <div class='product-content'>
                                <div class='product-name'>{row['name']}</div>
                                <div class='product-desc'>{row.get('description', 'Authentic vintage football jersey')}</div>
                                <div class='product-price'>{row['price']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if row["status"] == "Out of Stock":
                            st.button("❌ Out of Stock", key=f"out_{row['id']}", disabled=True, use_container_width=True)
                        else:
                            if st.button("🛒 Order Now", key=f"order_{row['id']}", use_container_width=True):
                                st.session_state.selected = row
                                st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
else:
    st.info("🏃‍♂️ Loading products... Please wait!")

# ==========================================
# CHECKOUT FORM - OPTIMIZED
# ==========================================
if "selected" in st.session_state:
    p = st.session_state.selected
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🛒 Complete Your Order\n**{p['name']}**")
    
    with st.form("checkout", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *", placeholder="John Doe")
        phone = col1.text_input("Phone Number *", placeholder="0541234567")
        location = col2.text_input("Delivery Location *", placeholder="Accra, Kumasi, etc.")
        qty = col2.number_input("Quantity *", min_value=1, value=1, max_value=int(p.get('stock', 10)))
        
        total = int(p["price"]) * int(qty)
        st.markdown(f"""
            <div style='background:linear-gradient(135deg, #667eea, #764ba2);color:white;padding:1rem;border-radius:12px;text-align:center;margin:1rem 0;'>
                <div style='font-size:0.9rem;opacity:0.9;'>Total Amount</div>
                <div style='font-size:2rem;font-weight:800;'>GHS {total}</div>
            </div>
        """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Place Order Now", use_container_width=True)
        
        if submitted:
            if not all([name, phone, location]):
                st.warning("⚠️ Please fill in all required fields")
            else:
                # Loading overlay
                loading = st.empty()
                loading.markdown("""
                    <div class='loading-overlay'>
                        <div class='loading-spinner'></div>
                        <div class='loading-text'>Processing your order...</div>
                    </div>
                """, unsafe_allow_html=True)
                
                try:
                    ref = generate_reference(p["name"], location)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Save to sheets
                    client = get_sheets_client()
                    orders_sheet = client.open("retro_jersey_shop").worksheet("orders")
                    orders_sheet.append_row([name, phone, location, p["name"], qty, total, ref, timestamp, "Pending"])
                    
                    # Async notifications
                    telegram_msg = f"""🛒 NEW ORDER!
📦 {p['name']}
👤 {name}
📱 {phone}
📍 {location}
💰 GHS {total}
🔖 {ref}"""
                    
                    email_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto;'>
                        <div style='background:linear-gradient(135deg,#667eea,#764ba2);color:white;padding:30px;text-align:center;border-radius:15px 15px 0 0;'>
                            <h1>🛒 New Order Received!</h1>
                        </div>
                        <div style='background:#f7fafc;padding:30px;border:1px solid #e2e8f0;border-top:none;'>
                            <p><strong>Product:</strong> {p['name']}</p>
                            <p><strong>Customer:</strong> {name}</p>
                            <p><strong>Phone:</strong> {phone}</p>
                            <p><strong>Location:</strong> {location}</p>
                            <p><strong>Quantity:</strong> {qty}</p>
                            <p><strong>Total:</strong> GHS {total}</p>
                            <p><strong>Reference:</strong> {ref}</p>
                        </div>
                    </body>
                    </html>
                    """
                    
                    send_notifications_async(telegram_msg, f"New Order: {ref}", email_html)
                    
                    loading.empty()
                    
                    st.markdown(f"""
                        <div class='order-success'>
                            <div class='order-success-title'>✅ Order Confirmed!</div>
                            <div class='order-success-details'>
                                <strong>Reference:</strong> {ref}<br>
                                <strong>Product:</strong> {p['name']}<br>
                                <strong>Total:</strong> GHS {total}<br>
                                <strong>Phone:</strong> {phone}<br><br>
                                We'll contact you shortly for delivery confirmation!
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if "selected" in st.session_state:
                        del st.session_state.selected
                    
                    # Auto-refresh after 3 seconds
                    time.sleep(3)
                    st.rerun()
                    
                except Exception as e:
                    loading.empty()
                    st.error(f"❌ Error processing order: {str(e)}")
    
    if st.button("← Continue Shopping", use_container_width=True):
        if "selected" in st.session_state:
            del st.session_state.selected
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# PROFESSIONAL FOOTER
# ==========================================
st.markdown("""
<div class='footer'>
    <div class='footer-content'>
        <div class='footer-title'>Retro Jersey Shop Ghana</div>
        <div class='footer-contact'>
            📞 <a href='tel:+233541468102'>054 146 8102</a> | 
            📱 Snapchat: <strong>@retroshop</strong><br>
            📍 Accra, Ghana | Nationwide Delivery 🚚
        </div>
        <div class='footer-social'>
            <a href='https://wa.me/233541468102' class='social-link' target='_blank' title='WhatsApp'>📱</a>
            <a href='#' class='social-link' target='_blank' title='Snapchat'>👻</a>
            <a href='#' class='social-link' target='_blank' title='Instagram'>📷</a>
        </div>
        <div class='footer-copyright'>
            © 2026 Retro Jersey Shop Ghana. All Rights Reserved.<br>
            <small>Authentic Vintage Football Jerseys | Premium Quality Guaranteed</small>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
