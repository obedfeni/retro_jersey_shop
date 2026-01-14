# ==============================
# Retro Jersey Shop – Professional Edition
# Hosting: Render
# Backend: Google Sheets
# Notifications: Telegram + Email
# ==============================

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

# ---------------- REFERENCE GENERATOR ----------------
def generate_reference(product_name, location):
    product_code = product_name[:3].upper()
    location_code = location[:3].upper()
    rand = random.randint(1000, 9999)
    return f"RJ-{product_code}-{location_code}-{rand}"

# ---------------- EMAIL NOTIFICATION ----------------
def send_email_notification(subject, message):
    """Send email notification using Gmail SMTP"""
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
    """Send notification to Telegram when order is placed"""
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

if "cart" not in st.session_state:
    st.session_state.cart = []

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

# ---------------- CLEAN E-COMMERCE THEME (Mobile Optimized) ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, .stApp { 
    background: #f7f9fc;
    color: #232f3e;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

h1, h2, h3, h4 { 
    color: #232f3e;
    font-weight: 600;
}

/* Top Navigation Bar - Mobile Optimized */
.top-nav {
    background: #ffffff;
    padding: 20px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    margin-bottom: 0;
    display: flex;
    align-items: center;
    gap: 15px;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: 15px;
    flex: 1;
}

.logo-icon {
    width: 60px;
    height: 60px;
    background: #2874f0;
    border-radius: 12px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 28px;
    flex-shrink: 0;
}

.logo-text {
    font-size: 24px;
    font-weight: 700;
    color: #232f3e;
    margin: 0;
    line-height: 1.2;
}

.nav-tagline {
    font-size: 12px;
    color: #565959;
    margin: 3px 0 0 0;
    font-style: italic;
}

/* Mobile responsive header */
@media (max-width: 768px) {
    .top-nav {
        padding: 15px 15px;
    }
    .logo-icon {
        width: 50px;
        height: 50px;
        font-size: 24px;
    }
    .logo-text {
        font-size: 18px;
    }
    .nav-tagline {
        font-size: 10px;
    }
}

/* Content Container */
.content-wrapper {
    max-width: 1400px;
    margin: 0 auto;
    padding: 30px 20px;
    background: #f7f9fc;
}

@media (max-width: 768px) {
    .content-wrapper {
        padding: 20px 10px;
    }
}

/* Section Headers */
.section-header {
    font-size: 24px;
    font-weight: 600;
    color: #232f3e;
    margin: 30px 0 20px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid #e7e9ec;
}

/* Product Card - Amazon/Etsy Style */
.product-card {
    background: #ffffff;
    border: 1px solid #e7e9ec;
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.product-card:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
    border-color: #c7c9cc;
}

.product-image-wrapper {
    width: 100%;
    height: 300px;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    border-bottom: 1px solid #e7e9ec;
    position: relative;
}

.product-image-wrapper img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

.stock-badge {
    position: absolute;
    top: 12px;
    right: 12px;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
}

.badge-in-stock {
    background: #e7f5e9;
    color: #067d62;
}

.badge-out-stock {
    background: #fce8e8;
    color: #c7254e;
}

.product-info {
    padding: 16px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.product-title {
    font-size: 16px;
    font-weight: 500;
    color: #0066c0;
    margin-bottom: 8px;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.product-description {
    font-size: 13px;
    color: #565959;
    line-height: 1.5;
    margin-bottom: 12px;
    flex: 1;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.product-price {
    font-size: 24px;
    font-weight: 700;
    color: #b12704;
    margin-bottom: 12px;
}

.price-currency {
    font-size: 14px;
    font-weight: 500;
    color: #565959;
    margin-right: 2px;
}

/* Buttons */
.stButton>button {
    background: #ffd814;
    color: #0f1111;
    border: 1px solid #fcd200;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 14px;
    width: 100%;
    transition: all 0.2s ease;
    box-shadow: 0 2px 5px rgba(213, 217, 217, 0.5);
}

.stButton>button:hover {
    background: #f7ca00;
    border-color: #f2c200;
}

.stButton>button:disabled {
    background: #f0f2f2;
    color: #565959;
    border-color: #d5d9d9;
}

/* Small Admin Button */
.admin-btn-small button {
    padding: 6px 12px !important;
    font-size: 12px !important;
    width: auto !important;
    min-width: 100px !important;
}

/* Admin Card */
.admin-container {
    background: white;
    border: 1px solid #e7e9ec;
    border-radius: 8px;
    padding: 30px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Stats Cards */
.stat-card {
    background: white;
    border: 1px solid #e7e9ec;
    border-radius: 8px;
    padding: 24px;
    text-align: center;
}

.stat-number {
    font-size: 32px;
    font-weight: 700;
    color: #232f3e;
    margin-bottom: 8px;
}

.stat-label {
    font-size: 14px;
    color: #565959;
    font-weight: 500;
}

/* Form Styles */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
    border-radius: 4px;
    border: 1px solid #d5d9d9;
    padding: 10px 12px;
    font-size: 14px;
}

.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus,
.stNumberInput>div>div>input:focus {
    border-color: #e77600;
    box-shadow: 0 0 0 3px rgba(231, 118, 0, 0.1);
}

/* Order Form */
.order-container {
    background: white;
    border: 1px solid #e7e9ec;
    border-radius: 8px;
    padding: 30px;
    margin: 30px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.order-summary {
    background: #f0f2f2;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
}

/* Success Message */
.success-message {
    background: #dff0d8;
    border: 1px solid #d6e9c6;
    color: #3c763d;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}

/* Footer */
.footer-section {
    background: #232f3e;
    color: #ffffff;
    padding: 40px 20px;
    margin-top: 60px;
    text-align: center;
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.footer-link {
    color: #ffffff;
    font-size: 14px;
    text-decoration: none;
}

.footer-link:hover {
    text-decoration: underline;
}

.footer-copyright {
    color: #999;
    font-size: 12px;
    margin-top: 20px;
}

/* Admin Login */
.admin-login-box {
    max-width: 400px;
    margin: 60px auto;
    background: white;
    border: 1px solid #e7e9ec;
    border-radius: 8px;
    padding: 40px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* Info Box */
.info-box {
    background: #e7f5ff;
    border: 1px solid #b3d9ff;
    border-radius: 8px;
    padding: 16px;
    margin: 20px 0;
    font-size: 14px;
    color: #0066c0;
}

/* Dataframe Styling */
.dataframe {
    font-size: 14px;
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

creds_dict = json.loads(raw_creds)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ---------------- LOAD SHEETS ----------------
SHEET_NAME = "retro_jersey_shop"
products_sheet = client.open(SHEET_NAME).worksheet("products")
orders_sheet = client.open(SHEET_NAME).worksheet("orders")

def load_products():
    records = products_sheet.get_all_records(expected_headers=[
        "id","name","price","stock",
        "image1","image2","image3",
        "description","status"
    ])
    rows = []
    for i, r in enumerate(records, start=2):
        r["_row"] = i
        rows.append(r)
    return pd.DataFrame(rows)

products_df = load_products()

# ==============================
# TOP NAVIGATION
# ==============================
st.markdown("""
<div class='top-nav'>
    <div class='logo-container'>
        <div class='logo-icon'>RJ</div>
        <div>
            <div class='logo-text'>Retro Jersey Shop</div>
            <div class='nav-tagline'>Authentic vintage jerseys</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Content wrapper
st.markdown("<div class='content-wrapper'>", unsafe_allow_html=True)

# ==============================
# 🔐 ADMIN LOGIN
# ==============================
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-login-box'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Login")
    st.markdown("Enter your credentials to access the dashboard")
    
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
# 📊 ADMIN DASHBOARD
# ==============================
if st.session_state.admin_logged:
    
    st.markdown("<h1 style='color:#232f3e; margin-bottom:10px;'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#565959; margin-bottom:30px;'>Manage your store products and orders</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged = False
            st.rerun()
    
    # Check Notification Configuration
    telegram_configured = bool(os.environ.get("TELEGRAM_BOT_TOKEN") and os.environ.get("TELEGRAM_CHAT_ID"))
    email_configured = bool(os.environ.get("ADMIN_EMAIL") and os.environ.get("EMAIL_APP_PASSWORD"))
    
    if not telegram_configured and not email_configured:
        st.markdown("""
        <div class='info-box'>
            ⚠️ <strong>No notifications configured!</strong><br>
            Set up Telegram or Email to receive instant order alerts.
        </div>
        """, unsafe_allow_html=True)
    else:
        notif_status = []
        if telegram_configured:
            notif_status.append("Telegram")
        if email_configured:
            notif_status.append("Email")
        
        st.markdown(f"""
        <div style='background:#e7f5e9; border:1px solid #c6e9d0; border-radius:8px; padding:16px; margin:20px 0;'>
            ✅ <strong>Notifications active via: {', '.join(notif_status)}</strong>
        </div>
        """, unsafe_allow_html=True)
    
    # Statistics
    orders_df = pd.DataFrame(
        orders_sheet.get_all_records(expected_headers=[
            "name","phone","location","items",
            "qty","amount","reference","timestamp","status"
        ])
    )
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(products_df)}</div>
            <div class='stat-label'>Total Products</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>{len(orders_df)}</div>
            <div class='stat-label'>Total Orders</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        total_revenue = orders_df['amount'].sum() if not orders_df.empty else 0
        st.markdown(f"""
        <div class='stat-card'>
            <div class='stat-number'>GHS {total_revenue:,.0f}</div>
            <div class='stat-label'>Total Revenue</div>
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
        add = st.form_submit_button("Add Product", use_container_width=True)
        
        if add and name and images:
            encoded = []
            for img in images[:3]:
                encoded.append(
                    f"data:image/png;base64,{base64.b64encode(img.read()).decode()}"
                )
            while len(encoded) < 3:
                encoded.append("")
            
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            status = "In Stock" if stock > 0 else "Out of Stock"
            
            products_sheet.append_row([
                new_id, name, price, stock,
                encoded[0], encoded[1], encoded[2],
                desc, status
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
                
                if st.button(f"Delete Product", key=f"del_{row['id']}", use_container_width=True):
                    products_sheet.delete_rows(row["_row"])
                    st.success("Product deleted!")
                    st.rerun()
    else:
        st.info("No products yet")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ORDERS
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 📦 Recent Orders")
    if not orders_df.empty:
        st.dataframe(orders_df, use_container_width=True, height=400)
    else:
        st.info("No orders yet")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # NOTIFICATION SETUP
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 🔔 Notification Setup")
    
    tab1, tab2 = st.tabs(["📧 Email (Free)", "📱 Telegram (Free)"])
    
    with tab1:
        st.markdown("""
        **Setup Gmail Notifications (5 minutes)**
        
        1. **Get App Password:**
           - Go to [Google Account](https://myaccount.google.com)
           - Security → 2-Step Verification (enable if not enabled)
           - Scroll down → App passwords
           - Select app: Mail, Device: Other (name it "Store")
           - Click Generate → Copy the 16-character password
        
        2. **Add to Render:**
           - `ADMIN_EMAIL` = your_email@gmail.com
           - `EMAIL_APP_PASSWORD` = the 16-char password (no spaces)
        
        3. **Done!** You'll get emails for new orders.
        """)
    
    with tab2:
        st.markdown("""
        **Setup Telegram Bot (5 minutes)**
        
        1. **Create Bot:**
           - Search `@BotFather` on Telegram
           - Send `/newbot`
           - Name: "Store Alerts"
           - Username: "yourstore_bot"
           - Copy TOKEN
        
        2. **Get Chat ID:**
           - Search `@userinfobot`
           - Send any message
           - Copy your ID
        
        3. **Add to Render:**
           - `TELEGRAM_BOT_TOKEN` = your bot token
           - `TELEGRAM_CHAT_ID` = your chat ID
        
        4. **Start bot:** Send `/start` to your bot
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ==============================
# 🛍️ PUBLIC SHOP
# ==============================

# Small admin button
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    st.markdown("<div class='admin-btn-small'>", unsafe_allow_html=True)
    if st.button("🔐 Admin"):
        st.session_state.show_admin_login = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='section-header'>Featured Products</div>", unsafe_allow_html=True)

if products_df.empty:
    st.info("🏗️ No products available at the moment. Check back soon!")
else:
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            badge_class = "badge-in-stock" if row["status"] == "In Stock" else "badge-out-stock"
            
            st.markdown(f"""
            <div class='product-card'>
                <div class='product-image-wrapper'>
                    <img src='{row["image1"]}' alt='{row["name"]}'>
                    <div class='stock-badge {badge_class}'>{row["status"]}</div>
                </div>
                <div class='product-info'>
                    <div class='product-title'>{row['name']}</div>
                    <div class='product-description'>{row['description']}</div>
                    <div class='product-price'>
                        <span class='price-currency'>GHS</span>{row['price']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if row["status"] == "Out of Stock":
                st.button("Unavailable", key=f"out_{row['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("Add to Cart", key=f"order_{row['id']}", use_container_width=True):
                    st.session_state.selected = row

# ==============================
# ORDER FORM
# ==============================
if "selected" in st.session_state:
    p = st.session_state.selected
    
    st.markdown("<div class='order-container'>", unsafe_allow_html=True)
    st.markdown(f"### Checkout")
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
        <div class='order-summary'>
            <strong>Order Summary</strong><br>
            Item: {p['name']}<br>
            Quantity: {qty}<br>
            <strong style='font-size:18px; color:#b12704;'>Total: GHS {total}</strong>
        </div>
        """, unsafe_allow_html=True)
        
        send = st.form_submit_button("Place Order", use_container_width=True)
        
        if send and name and phone and location:
            reference = generate_reference(p["name"], location)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            orders_sheet.append_row([
                name,
                phone,
                location,
                p["name"],
                qty,
                total,
                reference,
                timestamp,
                "Pending"
            ])
            
            # Send Telegram Notification
            telegram_message = f"""🛒 <b>NEW ORDER!</b>

📦 <b>Product:</b> {p['name']}
👤 <b>Customer:</b> {name}
📱 <b>Phone:</b> {phone}
📍 <b>Location:</b> {location}
🔢 <b>Qty:</b> {qty}
💰 <b>Total:</b> GHS {total}
🔖 <b>Ref:</b> {reference}
⏰ <b>Time:</b> {timestamp}

Status: ⏳ Pending"""
            
            telegram_sent = send_telegram_notification(telegram_message)
            
            # Send Email Notification
            email_subject = f"🛒 New Order: {reference}"
            email_body = f"""
            <html>
            <body style='font-family: Arial, sans-serif;'>
                <h2 style='color: #2874f0;'>New Order Received!</h2>
                <table style='border-collapse: collapse; width: 100%;'>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Product:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{p['name']}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Customer:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{name}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Phone:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{phone}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Location:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{location}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Quantity:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{qty}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Total:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>GHS {total}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Reference:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{reference}</td></tr>
                    <tr><td style='padding: 8px; border-bottom: 1px solid #ddd;'><strong>Time:</strong></td><td style='padding: 8px; border-bottom: 1px solid #ddd;'>{timestamp}</td></tr>
                </table>
                <p style='margin-top: 20px; color: #666;'>Status: Pending</p>
            </body>
            </html>
            """
            
            email_sent = send_email_notification(email_subject, email_body)

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div class='footer-section'>
    <div class='footer-links'>
        <a href='tel:0541468102' class='footer-link'>📞 0541468102</a>
        <span style='color:#999;'>|</span>
        <a href='#' class='footer-link'>📱 Snapchat: @retroshop</a>
        <span style='color:#999;'>|</span>
        <a href='#' class='footer-link'>📍 Accra, Ghana</a>
    </div>
    <div class='footer-copyright'>
        © 2026 Retro Jersey Shop • All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)

