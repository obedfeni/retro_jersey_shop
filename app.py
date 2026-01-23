# ==========================================
# RETRO JERSEY SHOP - PERFORMANCE + MARKETING EDITION
# Lazy Loading, Caching, Video Compression, Share Buttons
# ==========================================

import streamlit as st
import gspread, pandas as pd, os, json, random, requests, smtplib
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import cloudinary, cloudinary.uploader
from urllib.parse import quote

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
                {'fetch_format': 'auto'}  # Auto WebP/AVIF for faster loading
            ],
            "video": [
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:low'},  # Compress videos more
                {'video_codec': 'h264'},  # Better compression
                {'bit_rate': '500k'}  # Reduce file size significantly
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
    except: pass
    return False

def send_telegram_notification(message):
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            return requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                               data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10).status_code == 200
        except: pass
    return False

def send_email_notification(subject, message):
    admin_email, password = os.environ.get("ADMIN_EMAIL"), os.environ.get("EMAIL_APP_PASSWORD")
    if admin_email and password:
        try:
            msg = MIMEMultipart()
            msg['From'], msg['To'], msg['Subject'] = admin_email, admin_email, subject
            msg.attach(MIMEText(message, 'html'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(admin_email, password)
            server.send_message(msg)
            server.quit()
            return True
        except: pass
    return False

def get_share_url(product_name, product_price, product_image):
    """Generate shareable URLs for social media"""
    base_url = "https://retro-jersey-shop.onrender.com"  # Update with your actual URL
    text = f"Check out {product_name} - Only GHS {product_price}!"
    
    return {
        "whatsapp": f"https://wa.me/?text={quote(text + ' ' + base_url)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={quote(base_url)}",
        "twitter": f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(base_url)}",
        "telegram": f"https://t.me/share/url?url={quote(base_url)}&text={quote(text)}"
    }

# Page Config
st.set_page_config(page_title="Retro Jersey Shop", layout="wide", initial_sidebar_state="collapsed")

# Session State
for key in ["admin_logged", "show_admin_login", "visit_tracked"]:
    if key not in st.session_state:
        st.session_state[key] = False

if "page" in st.query_params and st.query_params["page"] == "admin":
    st.session_state.show_admin_login = True

# Hide Streamlit UI
st.markdown("""<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>""", unsafe_allow_html=True)

# Professional Light Blue Theme with Performance Optimizations
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Poppins:wght@500;600;700;800;900&display=swap');
:root {--primary:#60a5fa;--secondary:#3b82f6;--light-blue:#dbeafe;--text:#1e293b;--border:#e2e8f0;}
html,body,.stApp{background:linear-gradient(135deg,#eff6ff 0%,#dbeafe 50%,#bfdbfe 100%);color:var(--text);font-family:'Inter',sans-serif}

/* Performance: GPU acceleration for animations */
.product-card,.product-image-wrapper img,.product-image-wrapper video {
    will-change: transform;
    transform: translateZ(0);
}

/* Lazy loading optimization */
.product-image-wrapper img,
.product-image-wrapper video {
    loading: lazy;
    content-visibility: auto;
}

.compact-header{background:linear-gradient(135deg,#3b82f6 0%,#60a5fa 100%);padding:20px 30px;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:sticky;top:0;z-index:1000}
.header-content{max-width:1400px;margin:0 auto;display:flex;align-items:center;gap:20px}
.logo-compact{width:50px;height:50px;background:white;border-radius:10px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 8px rgba(0,0,0,0.2)}
.store-name{font-family:'Poppins',sans-serif;font-size:28px;font-weight:800;color:white;margin:0;letter-spacing:0.5px}
.store-tagline{font-size:13px;color:rgba(255,255,255,0.9);margin:3px 0 0 0}
.content-wrapper{max-width:1400px;margin:0 auto;padding:30px 20px}
.ad-banner{background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);border:2px solid #f59e0b;border-radius:12px;padding:15px 20px;margin:20px 0;text-align:center}
.ad-title{font-size:18px;font-weight:800;color:#ea580c;margin:0 0 5px 0}
.ad-text{font-size:14px;color:#78350f;font-weight:500;margin:0}
.section-header{font-size:28px;font-weight:800;color:var(--secondary);margin:30px 0 20px 0;padding-bottom:10px;border-bottom:3px solid var(--primary);text-align:center}
.product-card{background:white;border:1px solid var(--border);border-radius:12px;overflow:hidden;transition:all 0.3s ease;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.product-card:hover{transform:translateY(-8px);box-shadow:0 12px 24px rgba(96,165,250,0.2);border-color:#60a5fa}
.product-image-wrapper{width:100%;height:280px;background:#f8fafc;display:flex;align-items:center;justify-content:center;padding:15px;position:relative}
.product-image-wrapper img,.product-image-wrapper video{width:100%;height:100%;object-fit:contain;transition:transform 0.4s ease}
.product-card:hover .product-image-wrapper img,.product-card:hover .product-image-wrapper video{transform:scale(1.05)}
.stock-badge{position:absolute;top:10px;right:10px;padding:6px 12px;border-radius:20px;font-size:11px;font-weight:700;text-transform:uppercase;box-shadow:0 2px 8px rgba(0,0,0,0.15)}
.badge-in-stock{background:linear-gradient(135deg,#10b981 0%,#059669 100%);color:white}
.badge-out-stock{background:linear-gradient(135deg,#ef4444 0%,#dc2626 100%);color:white}
.image-counter{font-size:12px;color:#64748b;font-weight:600;text-align:center;padding:8px;background:#f8fafc;border-top:1px solid var(--border)}
.product-info{padding:20px}
.product-title{font-size:17px;font-weight:700;color:var(--text);margin-bottom:10px}
.product-description{font-size:13px;color:#64748b;line-height:1.5;margin-bottom:12px}
.product-price{font-size:28px;font-weight:900;color:#3b82f6;margin-bottom:12px}

/* Share Buttons Styling */
.share-buttons{display:flex;gap:8px;padding:10px 0;flex-wrap:wrap;justify-content:center}
.share-btn{display:inline-flex;align-items:center;gap:6px;padding:8px 16px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;color:white;transition:all 0.3s ease;box-shadow:0 2px 6px rgba(0,0,0,0.1)}
.share-btn:hover{transform:translateY(-2px);box-shadow:0 4px 10px rgba(0,0,0,0.15)}
.share-whatsapp{background:linear-gradient(135deg,#25D366 0%,#128C7E 100%)}
.share-facebook{background:linear-gradient(135deg,#1877f2 0%,#0c5ec4 100%)}
.share-twitter{background:linear-gradient(135deg,#1DA1F2 0%,#0d8bd9 100%)}
.share-telegram{background:linear-gradient(135deg,#0088cc 0%,#006ba8 100%)}

.stButton>button{background:linear-gradient(135deg,#60a5fa 0%,#3b82f6 100%);color:white;border:none;border-radius:8px;padding:12px 24px;font-weight:700;font-size:14px;width:100%;transition:all 0.3s ease;box-shadow:0 2px 8px rgba(96,165,250,0.4);text-transform:uppercase}
.stButton>button:hover{transform:translateY(-2px);box-shadow:0 4px 12px rgba(96,165,250,0.5)}
.stButton>button:disabled{background:#94a3b8;box-shadow:none}
.stat-card{background:white;border:1px solid var(--border);border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.stat-number{font-size:36px;font-weight:900;color:#60a5fa;margin-bottom:8px}
.stat-label{font-size:13px;color:#64748b;font-weight:600;text-transform:uppercase}
.admin-container{background:white;border:1px solid var(--border);border-radius:12px;padding:25px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,0.08)}
.success-message{background:linear-gradient(135deg,#d1fae5 0%,#a7f3d0 100%);border:2px solid #10b981;color:#065f46;padding:20px;border-radius:12px;margin:20px 0}
.footer-section{background:linear-gradient(135deg,#3b82f6 0%,#60a5fa 100%);color:white;padding:40px 20px;margin-top:60px;text-align:center}
.footer-link{color:white;font-size:14px;text-decoration:none;transition:all 0.3s ease}
.footer-link:hover{color:var(--light-blue)}

/* Loading skeleton for lazy loading */
.skeleton{background:linear-gradient(90deg,#f0f0f0 25%,#e0e0e0 50%,#f0f0f0 75%);background-size:200% 100%;animation:loading 1.5s infinite}
@keyframes loading{0%{background-position:200% 0}100%{background-position:-200% 0}}

@media(max-width:768px){.compact-header{padding:15px 20px}.logo-compact{width:40px;height:40px}.store-name{font-size:20px}.store-tagline{font-size:11px}.share-buttons{gap:6px}.share-btn{padding:6px 12px;font-size:12px}}
</style>""", unsafe_allow_html=True)

# Google Sheets Auth
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
try:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(os.environ.get("GCP_SERVICE_ACCOUNT")), scope)
    client = gspread.authorize(creds)
except:
    st.error("⚠️ Connection error")
    st.stop()

SHEET_NAME = "retro_jersey_shop"
try:
    products_sheet = client.open(SHEET_NAME).worksheet("products")
    orders_sheet = client.open(SHEET_NAME).worksheet("orders")
except:
    st.error("⚠️ Sheets not found")
    st.stop()

# PERFORMANCE: Aggressive caching with longer TTL
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5 minutes
def load_products():
    records = products_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

# PERFORMANCE: Cache orders separately
@st.cache_data(ttl=60, show_spinner=False)  # Cache for 1 minute
def load_orders():
    records = orders_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

products_df = load_products()

# Header
st.markdown("""<div class='compact-header'><div class='header-content'>
<div class='logo-compact'><svg viewBox="0 0 100 100"><defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" style="stop-color:#60a5fa"/><stop offset="100%" style="stop-color:#3b82f6"/></linearGradient></defs>
<text x="50" y="65" font-family="Poppins" font-size="50" font-weight="900" fill="url(#g1)" text-anchor="middle">RJ</text></svg></div>
<div><h1 class='store-name'>RETRO JERSEY SHOP</h1><p class='store-tagline'>Premium Vintage Collection</p></div>
</div></div><div class='content-wrapper'>""", unsafe_allow_html=True)

# Admin Login
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-container' style='max-width:500px;margin:80px auto'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Login")
    password = st.text_input("Password", type="password")
    if st.button("Login", use_container_width=True):
        if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
            st.session_state.admin_logged = True
            st.session_state.show_admin_login = False
            st.cache_data.clear()  # Clear cache on login
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
    st.markdown("<h1 style='text-align:center;color:var(--secondary)'>📊 Admin Dashboard</h1>", unsafe_allow_html=True)
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
        col.markdown(f"<div class='stat-card'><div class='stat-number'>{num}</div><div class='stat-label'>{label}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
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
            image_urls, video_url = [], ""
            with st.spinner("☁️ Uploading & optimizing..."):
                for idx, img in enumerate(images[:3], 1):
                    url = upload_to_cloudinary(img, f"{name.replace(' ', '_')}_{idx}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg")
                    if url: 
                        image_urls.append(url)
                        st.success(f"✅ Image {idx} optimized")
                if video: 
                    video_url = upload_to_cloudinary(video, f"{name.replace(' ', '_')}_video.mp4", "video")
                    if video_url:
                        st.success("✅ Video compressed & uploaded")
            while len(image_urls) < 3: image_urls.append("")
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            products_sheet.append_row([new_id, name, price, stock, *image_urls, video_url, desc, "In Stock" if stock > 0 else "Out of Stock"])
            st.cache_data.clear()  # Clear cache after adding
            st.success("✅ Product added!")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
    st.markdown("### 🗂️ Manage Products")
    if not products_df.empty:
        cols = st.columns(3)
        for idx, row in products_df.iterrows():
            with cols[idx % 3]:
                # Only show image if URL exists and is valid
                if row.get("image1") and str(row["image1"]).strip():
                    st.image(row["image1"], width=None, use_container_width=True)
                else:
                    st.info("No image")
                st.markdown(f"**{row['name']}** | GHS {row['price']}")
                if st.button("Delete", key=f"del_{row['id']}", use_container_width=True):
                    for col in ['image1', 'image2', 'image3', 'video']:
                        if row.get(col) and 'cloudinary.com' in str(row[col]): delete_from_cloudinary(row[col])
                    products_sheet.delete_rows(row["_row"])
                    st.cache_data.clear()
                    st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='admin-container'>", unsafe_allow_html=True)
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
                    # WhatsApp Contact Button
                    whatsapp_message = f"""Hi {order['name']}! 👋

Thank you for your order! 🎉

📦 Product: {order['items']}
🔢 Quantity: {order['qty']}
💰 Total: GHS {order['amount']}
🔖 Reference: {order['reference']}

✅ Your order has been received!
We'll contact you shortly to confirm delivery to {order['location']}.

For any questions, just reply to this message.

- Retro Jersey Shop"""
                    
                    # Clean phone number (remove spaces, dashes, etc)
                    clean_phone = ''.join(filter(str.isdigit, str(order['phone'])))
                    # Add Ghana country code if not present
                    if not clean_phone.startswith('233'):
                        if clean_phone.startswith('0'):
                            clean_phone = '233' + clean_phone[1:]
                        else:
                            clean_phone = '233' + clean_phone
                    
                    whatsapp_url = f"https://wa.me/{clean_phone}?text={quote(whatsapp_message)}"
                    
                    st.markdown(f"""
                    <a href='{whatsapp_url}' target='_blank' style='display:block;margin-bottom:10px'>
                        <button style='width:100%;background:linear-gradient(135deg,#25D366 0%,#128C7E 100%);
                        color:white;border:none;border-radius:8px;padding:12px;font-weight:700;cursor:pointer;
                        font-size:14px;box-shadow:0 2px 8px rgba(37,211,102,0.3)'>
                            📱 Contact via WhatsApp
                        </button>
                    </a>
                    """, unsafe_allow_html=True)
                    
                    # Share Buttons for Admin
                    share_urls = get_share_url(order['items'], order['amount'], "")
                    st.markdown(f"""
                    <div style='margin-bottom:10px'>
                        <a href='{share_urls["whatsapp"]}' target='_blank' style='display:inline-block;width:48%;margin-right:2%'>
                            <button style='width:100%;background:linear-gradient(135deg,#25D366 0%,#128C7E 100%);
                            color:white;border:none;border-radius:6px;padding:8px;font-weight:600;cursor:pointer;
                            font-size:12px;box-shadow:0 2px 6px rgba(37,211,102,0.3)'>
                                📱 Share
                            </button>
                        </a>
                        <a href='{share_urls["facebook"]}' target='_blank' style='display:inline-block;width:48%'>
                            <button style='width:100%;background:linear-gradient(135deg,#1877f2 0%,#0c5ec4 100%);
                            color:white;border:none;border-radius:6px;padding:8px;font-weight:600;cursor:pointer;
                            font-size:12px;box-shadow:0 2px 6px rgba(24,119,242,0.3)'>
                                👍 Share
                            </button>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Approve Order Button
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

st.markdown("<div class='ad-banner'><div class='ad-title'>🔥 FLASH SALE 🔥</div><div class='ad-text'>20% OFF this weekend!</div></div>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>⚡ Featured Products</div>", unsafe_allow_html=True)

if not products_df.empty:
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            # Multi-image carousel with lazy loading
            images = [row.get(f"image{i}", "") for i in range(1, 4) if row.get(f"image{i}")]
            video = row.get("video", "")
            
            carousel_key = f"carousel_{row['id']}"
            if carousel_key not in st.session_state: st.session_state[carousel_key] = 0
            
            badge = "badge-in-stock" if row["status"] == "In Stock" else "badge-out-stock"
            
            # PERFORMANCE: Lazy loading with loading attribute
            if video and 'cloudinary.com' in str(video):
                media_html = f"<video src='{video}' autoplay loop muted playsinline loading='lazy' style='width:100%;height:100%;object-fit:contain'></video>"
            else:
                media_html = f"<img src='{images[st.session_state[carousel_key]]}' alt='{row['name']}' loading='lazy'>" if images else ""
            
            st.markdown(f"""<div class='product-card'><div class='product-image-wrapper'>{media_html}
            <div class='stock-badge {badge}'>{row["status"]}</div></div>""", unsafe_allow_html=True)
            
            if len(images) > 1:
                col_l, col_m, col_r = st.columns([1, 2, 1])
                with col_l:
                    if st.button("◀", key=f"prev_{row['id']}", use_container_width=True):
                        st.session_state[carousel_key] = (st.session_state[carousel_key] - 1) % len(images)
                        st.rerun()
                with col_m:
                    st.markdown(f"<div class='image-counter'>{st.session_state[carousel_key] + 1} / {len(images)}</div>", unsafe_allow_html=True)
                with col_r:
                    if st.button("▶", key=f"next_{row['id']}", use_container_width=True):
                        st.session_state[carousel_key] = (st.session_state[carousel_key] + 1) % len(images)
                        st.rerun()
            
            st.markdown(f"""<div class='product-info'><div class='product-title'>{row['name']}</div>
            <div class='product-description'>{row.get('description', '')}</div><div class='product-price'>GHS {row['price']}</div>
            </div></div>""", unsafe_allow_html=True)
            
            if row["status"] == "Out of Stock":
                st.button("Unavailable", key=f"out_{row['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 Add to Cart", key=f"order_{row['id']}", use_container_width=True):
                    st.session_state.selected = row

# Order Form
if "selected" in st.session_state:
    p = st.session_state.selected
    st.markdown("<div class='admin-container' style='max-width:800px;margin:50px auto'>", unsafe_allow_html=True)
    st.markdown(f"### 🛒 Checkout\n**Product:** {p['name']}")
    with st.form("order"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        phone = col1.text_input("Phone *")
        location = col2.text_input("Location *")
        qty = col2.number_input("Quantity *", min_value=1, value=1)
        total = int(p["price"]) * int(qty)
        st.markdown(f"<div style='background:#f8f9fa;padding:20px;border-radius:12px'><strong>Total: GHS {total}</strong></div>", unsafe_allow_html=True)
        
        if st.form_submit_button("🚀 Place Order", use_container_width=True) and name and phone and location:
            ref = generate_reference(p["name"], location)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            orders_sheet.append_row([name, phone, location, p["name"], qty, total, ref, timestamp, "Pending"])
            
            msg = f"🛒 <b>NEW ORDER!</b>\n📦 {p['name']}\n👤 {name}\n📱 {phone}\n📍 {location}\n💰 GHS {total}\n🔖 {ref}"
            send_telegram_notification(msg)
            send_email_notification(f"New Order: {ref}", f"<h2>Product: {p['name']}</h2><p>Customer: {name}<br>Phone: {phone}<br>Location: {location}<br>Total: GHS {total}</p>")
            
            st.cache_data.clear()  # Clear cache after order
            st.markdown(f"<div class='success-message'><h3>✅ Order Placed!</h3><p>Total: GHS {total}</p><p>Ref: {ref}</p></div>", unsafe_allow_html=True)
            del st.session_state.selected
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("""<div class='footer-section'><a href='tel:0541468102' class='footer-link'>📞 0541468102</a> | 
<a href='#' class='footer-link'>📱 Snapchat: @retroshop</a> | <a href='#' class='footer-link'>📍 Accra, Ghana</a>
<div style='color:#999;font-size:14px;margin-top:20px'>© 2026 Retro Jersey Shop • All Rights Reserved</div></div>""", unsafe_allow_html=True)
