
# RETRO JERSEY SHOP 

import streamlit as st
import gspread, pandas as pd, os, json, random, requests, smtplib
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cloudinary, cloudinary.uploader
from urllib.parse import quote
import threading

# Cloudinary Setup
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
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'}
            ],
            "video": [
                {'width': 800, 'height': 800, 'crop': 'limit'},
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

# ASYNC NOTIFICATION FUNCTIONS - Don't block the main thread
def send_notifications_async(telegram_msg, email_subject, email_body):
    """Send notifications in background thread - never blocks UI"""
    def _send():
        try:
            # Telegram
            token = os.environ.get("TELEGRAM_BOT_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            if token and chat_id:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    data={"chat_id": chat_id, "text": telegram_msg, "parse_mode": "HTML"},
                    timeout=5
                )
            
            # Email
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
            pass  # Fail silently in background
    
    # Start thread and return immediately
    thread = threading.Thread(target=_send, daemon=True)
    thread.start()

def get_share_url(product_name, product_price, product_image):
    """Generate shareable URLs for social media"""
    base_url = "https://retrogh.shop"
    text = f"Check out {product_name} - Only GHS {product_price}!"
    return {
        "whatsapp": f"https://wa.me/?text={quote(text + ' ' + base_url)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={quote(base_url)}",
        "twitter": f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(base_url)}",
        "telegram": f"https://t.me/share/url?url={quote(base_url)}&text={quote(text)}"
    }

# Page Config with SEO
st.set_page_config(
    page_title="Retro Jersey Shop - Premium Vintage Football Jerseys in Ghana",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "Retro Jersey Shop - Your #1 destination for premium vintage football jerseys in Ghana 🇬🇭"
    }
)

# SEO Meta Tags & Favicon
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <meta name="description" content="Retro Jersey Shop - Buy authentic vintage football jerseys in Ghana. Premium quality retro jerseys from top clubs. Fast delivery in Accra and across Ghana. Shop now!">
    <meta name="keywords" content="retro jerseys ghana, vintage football shirts, classic jerseys accra, football jerseys ghana, retro soccer jerseys, vintage sports wear ghana">
    <meta name="author" content="Retro Jersey Shop">
    <meta property="og:title" content="Retro Jersey Shop - Premium Vintage Football Jerseys">
    <meta property="og:description" content="Your #1 destination for authentic vintage football jerseys in Ghana. Premium quality, fast delivery.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://retrogh.shop">
    <meta property="og:site_name" content="Retro Jersey Shop">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Retro Jersey Shop Ghana">
    <meta name="twitter:description" content="Premium vintage football jerseys in Ghana. Shop authentic retro jerseys now!">
    <link rel="canonical" href="https://retrogh.shop">
    
    <!-- Favicon as emoji -->
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>⚽</text></svg>">
""", unsafe_allow_html=True)

# Session State
for key in ["admin_logged", "show_admin_login", "visit_tracked", "loading"]:
    if key not in st.session_state:
        st.session_state[key] = False

if "page" in st.query_params and st.query_params["page"] == "admin":
    st.session_state.show_admin_login = True

# Hide Streamlit UI
st.markdown("""<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

# Professional Theme + Loading Animation
st.markdown("""<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        .stApp {
            background: linear-gradient(to bottom, #f0f4ff, #e6f0ff);
        }
        
        /* LOADING OVERLAY - GLOBAL */
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.95);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        }
        
        .loading-dots {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 12px;
            padding: 20px;
        }
        .loading-dots span {
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #667eea;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .loading-dots span:nth-child(1) {
            animation-delay: -0.32s;
        }
        .loading-dots span:nth-child(2) {
            animation-delay: -0.16s;
        }
        @keyframes bounce {
            0%, 80%, 100% { 
                transform: scale(0);
                opacity: 0.5;
            } 
            40% { 
                transform: scale(1.2);
                opacity: 1;
            }
        }
        .loading-text {
            margin-top: 20px;
            font-size: 1.2rem;
            color: #667eea;
            font-weight: 600;
        }
        
        /* HEADER */
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0.8rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }
        .logo {
            width: 45px;
            height: 45px;
            background: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.1rem;
            color: #667eea;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            flex-shrink: 0;
        }
        .brand {
            font-size: 1.1rem;
            font-weight: bold;
            color: white;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            line-height: 1.3;
        }
        .brand-subtitle {
            font-size: 0.7rem;
            opacity: 0.9;
            color: white;
            margin-top: 2px;
        }
        
        @media (min-width: 768px) {
            .header {
                padding: 1.2rem;
                gap: 1rem;
                border-radius: 15px;
            }
            .logo {
                width: 55px;
                height: 55px;
                font-size: 1.4rem;
            }
            .brand {
                font-size: 1.5rem;
            }
            .brand-subtitle {
                font-size: 0.85rem;
            }
        }
        
        @media (min-width: 1024px) {
            .logo {
                width: 60px;
                height: 60px;
                font-size: 1.5rem;
            }
            .brand {
                font-size: 1.8rem;
            }
            .brand-subtitle {
                font-size: 0.9rem;
            }
        }
        
        .product-card {
            background: white;
            border-radius: 15px;
            padding: 1.2rem;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            margin-bottom: 1.5rem;
            border: 1px solid #e8ecf7;
        }
        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.15);
        }
        .product-image {
            width: 100%;
            height: 250px;
            object-fit: cover;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .product-name {
            font-size: 1.3rem;
            font-weight: 600;
            color: #2d3748;
            margin-bottom: 0.5rem;
        }
        .product-price {
            font-size: 1.5rem;
            color: #667eea;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        .product-desc {
            color: #718096;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        
        .badge {
            position: absolute;
            top: 10px;
            right: 10px;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-in-stock {
            background: #48bb78;
            color: white;
        }
        .badge-out-stock {
            background: #f56565;
            color: white;
        }
        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 0.3rem;
        }
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .flash-sale {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 0.8rem;
            border-radius: 10px;
            text-align: center;
            font-size: 1rem;
            font-weight: bold;
            margin: 1rem 0;
            box-shadow: 0 5px 15px rgba(245, 87, 108, 0.3);
            animation: pulse 2s infinite;
        }
        @media (min-width: 768px) {
            .flash-sale {
                padding: 1rem;
                font-size: 1.2rem;
            }
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2d3748;
            margin: 1.5rem 0 1rem 0;
            text-align: center;
        }
        @media (min-width: 768px) {
            .section-title {
                font-size: 2rem;
                margin: 2rem 0 1rem 0;
            }
        }
        .admin-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            margin-bottom: 2rem;
        }
        .order-success {
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            font-size: 1.2rem;
            margin: 2rem 0;
            box-shadow: 0 10px 30px rgba(72, 187, 120, 0.3);
        }
        
        .footer {
            background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            margin-top: 2rem;
            text-align: center;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
        }
        .footer-contact {
            font-size: 0.85rem;
            margin-bottom: 0.8rem;
            line-height: 1.6;
            opacity: 0.95;
        }
        .footer-contact a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        .footer-contact a:hover {
            color: #764ba2;
            text-decoration: underline;
        }
        .footer-copyright {
            font-size: 0.75rem;
            opacity: 0.8;
            margin-top: 0.5rem;
        }
        
        @media (min-width: 768px) {
            .footer {
                padding: 2rem;
                border-radius: 15px;
                margin-top: 3rem;
            }
            .footer-contact {
                font-size: 1rem;
                margin-bottom: 1rem;
            }
            .footer-copyright {
                font-size: 0.85rem;
            }
        }
        
        .carousel-controls {
            text-align: center;
            font-size: 0.85rem;
            color: #718096;
            margin: 0.5rem 0;
            font-weight: 500;
        }
        
        /* DARK MODE FIX */
        input[type="text"],
        input[type="number"],
        input[type="password"],
        textarea,
        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            background-color: white !important;
            color: #2d3748 !important;
            border: 2px solid #e2e8f0 !important;
            border-radius: 8px !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
        }
        
        input[type="text"]:focus,
        input[type="number"]:focus,
        input[type="password"]:focus,
        textarea:focus,
        .stTextInput input:focus,
        .stNumberInput input:focus,
        .stTextArea textarea:focus {
            border-color: #667eea !important;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
            outline: none !important;
        }
        
        label, .stTextInput label, .stNumberInput label, .stTextArea label {
            color: #2d3748 !important;
            font-weight: 600 !important;
            margin-bottom: 0.5rem !important;
            display: block !important;
            font-size: 0.95rem !important;
        }
        
        @media (max-width: 768px) {
            .product-image {
                height: 200px;
            }
        }
</style>""", unsafe_allow_html=True)

# Google Sheets Auth with caching
@st.cache_resource(ttl=3600)  # Cache for 1 hour
def get_sheets_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(os.environ.get("GCP_SERVICE_ACCOUNT")), 
            scope
        )
        client = gspread.authorize(creds)
        return client
    except:
        st.error("⚠️ Connection error")
        st.stop()

client = get_sheets_client()
SHEET_NAME = "retro_jersey_shop"

try:
    products_sheet = client.open(SHEET_NAME).worksheet("products")
    orders_sheet = client.open(SHEET_NAME).worksheet("orders")
except:
    st.error("⚠️ Sheets not found")
    st.stop()

# ULTRA AGGRESSIVE CACHING - 10 minutes for products
@st.cache_data(ttl=600, show_spinner=False)
def load_products():
    records = products_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

# Cache orders for 2 minutes
@st.cache_data(ttl=120, show_spinner=False)
def load_orders():
    records = orders_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

# Load products ONCE at start
if "products_loaded" not in st.session_state:
    with st.spinner(""):
        products_df = load_products()
        st.session_state.products_loaded = True
else:
    products_df = load_products()

# Header
st.markdown("""
<div class='header'>
    <div class='logo'>RJ</div>
    <div>
        <div class='brand'>RETRO JERSEY SHOP</div>
        <div class='brand-subtitle'>Premium Vintage Collection</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Admin Login
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Login")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
            st.session_state.admin_logged = True
            st.session_state.show_admin_login = False
            st.cache_data.clear()
            st.rerun()
        else:
            st.error("❌ Incorrect password")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("← Back"):
        st.session_state.show_admin_login = False
        st.rerun()
    st.stop()

# Admin Dashboard
if st.session_state.admin_logged:
    st.markdown("<div class='section-title'>📊 Admin Dashboard</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_logged = False
            st.cache_data.clear()
            st.rerun()
    
    orders_df = load_orders()
    approved_revenue = orders_df[orders_df['status'] == 'Approved']['amount'].sum() if not orders_df.empty else 0
    
    col1, col2, col3 = st.columns(3)
    for col, (num, label) in zip([col1, col2, col3], [(len(products_df), "Products"), (len(orders_df), "Orders"), (f"GHS {approved_revenue:,.0f}", "Revenue")]):
        col.markdown(f"<div class='stat-box'><div class='stat-number'>{num}</div><div class='stat-label'>{label}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### ➕ Add Product")
    with st.form("add_product"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Product Name *")
        price = col1.number_input("Price (GHS) *", min_value=0)
        stock = col2.number_input("Stock *", min_value=0)
        desc = st.text_area("Description")
        images = st.file_uploader("Upload Images (Max 3)", type=["png","jpg","jpeg"], accept_multiple_files=True)
        video = st.file_uploader("Upload Video (Optional - Will be compressed)", type=["mp4","mov"])
        if st.form_submit_button("Add Product", use_container_width=True) and name and images:
            # Show loading
            loading_container = st.empty()
            loading_container.markdown("""
                <div class='loading-overlay'>
                    <div class='loading-dots'>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div class='loading-text'>Uploading & Optimizing...</div>
                </div>
            """, unsafe_allow_html=True)
            
            image_urls, video_url = [], ""
            for idx, img in enumerate(images[:3], 1):
                url = upload_to_cloudinary(img, f"{name.replace(' ', '_')}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                if url:
                    image_urls.append(url)
            if video:
                video_url = upload_to_cloudinary(video, f"{name.replace(' ', '_')}_video.mp4", "video")
            
            while len(image_urls) < 3:
                image_urls.append("")
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            products_sheet.append_row([new_id, name, price, stock, *image_urls, video_url, desc, "In Stock" if stock > 0 else "Out of Stock"])
            
            loading_container.empty()
            st.cache_data.clear()
            st.success("✅ Product added!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Manage Products")
    if not products_df.empty:
        cols = st.columns(3)
        for idx, row in products_df.iterrows():
            with cols[idx % 3]:
                if row.get("image1") and str(row["image1"]).strip():
                    st.image(row["image1"], width=None, use_container_width=True)
                else:
                    st.info("No image")
                st.markdown(f"**{row['name']}** | GHS {row['price']}")
                if st.button("Delete", key=f"del_{row['id']}", use_container_width=True):
                    for col in ['image1', 'image2', 'image3', 'video']:
                        if row.get(col) and 'cloudinary.com' in str(row[col]):
                            delete_from_cloudinary(row[col])
                    products_sheet.delete_rows(row["_row"])
                    st.cache_data.clear()
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 📦 Orders")
    if not orders_df.empty:
        for idx, order in orders_df.iterrows():
            with st.expander(f"📦 {order['reference']} - {order['name']} - GHS {order['amount']} - {order['status']}"):
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
                    whatsapp_message = f"""Hi {order['name']}! 👋

Thank you for your order! 🎉

📦 Product: {order['items']}
🔢 Quantity: {order['qty']}
💰 Total: GHS {order['amount']}
🔖 Reference: {order['reference']}

✅ Your order has been received! We'll contact you shortly to confirm delivery to {order['location']}.

For any questions, just reply to this message.

- Retro Jersey Shop"""
                    
                    clean_phone = ''.join(filter(str.isdigit, str(order['phone'])))
                    if not clean_phone.startswith('233'):
                        if clean_phone.startswith('0'):
                            clean_phone = '233' + clean_phone[1:]
                        else:
                            clean_phone = '233' + clean_phone
                    
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={quote(whatsapp_message)}"
                    st.markdown(f"""
                        <a href="{whatsapp_url}" target="_blank" style="display:inline-block;background:#25D366;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;text-align:center;width:100%;margin-bottom:10px;">
                            📱 Contact via WhatsApp
                        </a>
                    """, unsafe_allow_html=True)
                    
                    share_urls = get_share_url(order['items'], order['amount'], "")
                    st.markdown(f"""
                        <div style='margin-top:10px;'>
                            <a href="{share_urls['whatsapp']}" target="_blank" style="display:inline-block;background:#25D366;color:white;padding:8px 12px;border-radius:5px;text-decoration:none;margin:2px;font-size:0.8rem;">📱 Share</a>
                            <a href="{share_urls['facebook']}" target="_blank" style="display:inline-block;background:#1877F2;color:white;padding:8px 12px;border-radius:5px;text-decoration:none;margin:2px;font-size:0.8rem;">👍 Share</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if order['status'] == 'Pending':
                        if st.button("✅ Approve Order", key=f"app_{idx}", use_container_width=True):
                            orders_sheet.update_cell(idx + 2, 9, "Approved")
                            st.cache_data.clear()
                            st.success("✅ Approved!")
                            st.rerun()
                    else:
                        st.success("✅ Approved")
    else:
        st.info("No orders yet")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# Public Shop
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    if st.button("🔐 Admin"):
        st.session_state.show_admin_login = True
        st.rerun()

st.markdown("<div class='flash-sale'>🔥 FLASH SALE 🔥<br>20% OFF this weekend!</div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>⚡ Featured Products</div>", unsafe_allow_html=True)

if not products_df.empty:
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            images = [row.get(f"image{i}", "") for i in range(1, 4) if row.get(f"image{i}")]
            video = row.get("video", "")
            
            carousel_key = f"carousel_{row['id']}"
            if carousel_key not in st.session_state:
                st.session_state[carousel_key] = 0
            
            badge = "badge-in-stock" if row["status"] == "In Stock" else "badge-out-stock"
            
            if video and 'cloudinary.com' in str(video):
                media_html = f"<video class='product-image' controls loading='lazy'><source src='{video}' type='video/mp4'></video>"
            else:
                media_html = f"<img src='{images[st.session_state[carousel_key]]}' class='product-image' loading='lazy'>" if images else ""
            
            st.markdown(f"""
                <div class='product-card' style='position:relative;'>
                    {media_html}
                    <div class='badge {badge}'>{row["status"]}</div>
                </div>
            """, unsafe_allow_html=True)
            
            if len(images) > 1:
                col_l, col_m, col_r = st.columns([1, 2, 1])
                with col_l:
                    if st.button("◀", key=f"prev_{row['id']}", use_container_width=True):
                        st.session_state[carousel_key] = (st.session_state[carousel_key] - 1) % len(images)
                        st.rerun()
                with col_m:
                    st.markdown(f"<div class='carousel-controls'>{st.session_state[carousel_key] + 1} / {len(images)}</div>", unsafe_allow_html=True)
                with col_r:
                    if st.button("▶", key=f"next_{row['id']}", use_container_width=True):
                        st.session_state[carousel_key] = (st.session_state[carousel_key] + 1) % len(images)
                        st.rerun()
            
            st.markdown(f"""
                <div class='product-name'>{row['name']}</div>
                <div class='product-desc'>{row.get('description', '')}</div>
                <div class='product-price'>GHS {row['price']}</div>
            """, unsafe_allow_html=True)
            
            if row["status"] == "Out of Stock":
                st.button("Unavailable", key=f"out_{row['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 Add to Cart", key=f"order_{row['id']}", use_container_width=True):
                    st.session_state.selected = row
                    st.rerun()

# ULTRA FAST Order Form
if "selected" in st.session_state:
    p = st.session_state.selected
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🛒 Checkout\n**Product:** {p['name']}")
    
    with st.form("order", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        phone = col1.text_input("Phone *")
        location = col2.text_input("Location *")
        qty = col2.number_input("Quantity *", min_value=1, value=1)
        total = int(p["price"]) * int(qty)
        st.markdown(f"<div class='product-price'>Total: GHS {total}</div>", unsafe_allow_html=True)
        
        submitted = st.form_submit_button("🚀 Place Order", use_container_width=True)
        
        if submitted and name and phone and location:
            # Show loading immediately
            loading_container = st.empty()
            loading_container.markdown("""
                <div class='loading-overlay'>
                    <div class='loading-dots'>
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <div class='loading-text'>Processing Order...</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Generate reference
            ref = generate_reference(p["name"], location)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to Google Sheets IMMEDIATELY (this is the priority)
            try:
                orders_sheet.append_row([name, phone, location, p["name"], qty, total, ref, timestamp, "Pending"])
                
                # Send notifications asynchronously in background (doesn't block)
                telegram_msg = f"🛒 NEW ORDER!\n📦 {p['name']}\n👤 {name}\n📱 {phone}\n📍 {location}\n💰 GHS {total}\n🔖 {ref}"
                email_body = f"""
                <!DOCTYPE html>
                <html>
                <body style='font-family: Arial, sans-serif;'>
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center;'>
                        <h1>🛒 NEW ORDER!</h1>
                    </div>
                    <div style='padding: 20px;'>
                        <p><strong>📦 Product:</strong> {p['name']}</p>
                        <p><strong>👤 Customer:</strong> {name}</p>
                        <p><strong>📱 Phone:</strong> {phone}</p>
                        <p><strong>📍 Location:</strong> {location}</p>
                        <p><strong>🔢 Quantity:</strong> {qty}</p>
                        <p><strong>💰 Total:</strong> GHS {total}</p>
                        <p><strong>🔖 Reference:</strong> {ref}</p>
                    </div>
                </body>
                </html>
                """
                send_notifications_async(telegram_msg, f"🛒 New Order: {ref}", email_body)
                
                # Clear loading and show success IMMEDIATELY
                loading_container.empty()
                st.cache_data.clear()
                
                st.markdown(f"""
                    <div class='order-success'>
                        ✅ Order Placed Successfully!<br><br>
                        📦 Product: {p['name']}<br>
                        💰 Total: GHS {total}<br>
                        🔖 Reference: {ref}<br><br>
                        We'll contact you shortly at {phone}!
                    </div>
                """, unsafe_allow_html=True)
                
                # Clean up
                if "selected" in st.session_state:
                    del st.session_state.selected
                
                # Redirect after 2 seconds
                st.markdown("""
                    <script>
                    setTimeout(function() {
                        window.location.href = window.location.pathname;
                    }, 2000);
                    </script>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                loading_container.empty()
                st.error(f"❌ Error: {e}")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("""
<div class='footer'>
    <div class='footer-contact'>
        📞 <a href='tel:0541468102'>0541468102</a> | 
        📱 Snapchat: <strong>@retroshop</strong> | 
        📍 Accra, Ghana
    </div>
    <div class='footer-copyright'>
        © 2026 Retro Jersey Shop • All Rights Reserved
    </div>
</div>
""", unsafe_allow_html=True)
