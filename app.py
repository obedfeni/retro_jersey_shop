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
                {'fetch_format': 'auto'} # Auto WebP/AVIF for faster loading
            ],
            "video": [
                {'width': 800, 'height': 800, 'crop': 'limit'},
                {'quality': 'auto:low'}, # Compress videos more
                {'video_codec': 'h264'}, # Better compression
                {'bit_rate': '500k'} # Reduce file size significantly
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

def send_telegram_notification(message):
    token, chat_id = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            return requests.post(f"https://api.telegram.org/bot{token}/sendMessage", data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"}, timeout=10).status_code == 200
        except:
            pass
    return False

def send_email_notification(subject, message):
    admin_email, password = os.environ.get("ADMIN_EMAIL"), os.environ.get("EMAIL_APP_PASSWORD")
    if admin_email and password:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = admin_email
            msg['To'] = admin_email
            msg['Subject'] = subject
            
            # HTML version
            html_part = MIMEText(message, 'html')
            msg.attach(html_part)
            
            # Connect and send
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.set_debuglevel(0)  # Set to 1 to debug
            server.starttls()
            server.login(admin_email, password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"❌ Email error: {e}")
            return False
    return False

def get_share_url(product_name, product_price, product_image):
    """Generate shareable URLs for social media"""
    base_url = "https://retro-jersey-shop.onrender.com" # Update with your actual URL
    text = f"Check out {product_name} - Only GHS {product_price}!"
    return {
        "whatsapp": f"https://wa.me/?text={quote(text + ' ' + base_url)}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={quote(base_url)}",
        "twitter": f"https://twitter.com/intent/tweet?text={quote(text)}&url={quote(base_url)}",
        "telegram": f"https://t.me/share/url?url={quote(base_url)}&text={quote(text)}"
    }

# Page Config
st.set_page_config(
    page_title="Retro Jersey Shop",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Add viewport meta tag for mobile optimization
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
""", unsafe_allow_html=True)

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
</style>""", unsafe_allow_html=True)

# Professional Light Blue Theme with BETTER Mobile Responsiveness
st.markdown("""<style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        .stApp {
            background: linear-gradient(to bottom, #f0f4ff, #e6f0ff);
        }
        
        /* FIXED MOBILE HEADER */
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
        
        /* Tablet and larger */
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
        
        /* Desktop */
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
        
        /* FIXED CAROUSEL ARROWS FOR MOBILE */
        .carousel-btn {
            background: rgba(102, 126, 234, 0.9) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 6px 10px !important;
            font-size: 0.85rem !important;
            cursor: pointer;
            transition: all 0.3s ease;
            min-height: 35px !important;
        }
        .carousel-btn:hover {
            background: rgba(102, 126, 234, 1) !important;
            transform: scale(1.05);
        }
        
        @media (min-width: 768px) {
            .carousel-btn {
                padding: 8px 14px !important;
                font-size: 1rem !important;
                min-height: 38px !important;
            }
        }
        
        /* Loading Spinner */
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        /* Badges */
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
        
        /* IMPROVED FOOTER FOR MOBILE */
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
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .product-image {
                height: 200px;
            }
        }
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
@st.cache_data(ttl=300, show_spinner=False) # Cache for 5 minutes
def load_products():
    records = products_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

# PERFORMANCE: Cache orders separately
@st.cache_data(ttl=60, show_spinner=False) # Cache for 1 minute
def load_orders():
    records = orders_sheet.get_all_records()
    for i, r in enumerate(records, start=2):
        r["_row"] = i
    return pd.DataFrame(records)

products_df = load_products()

# Header - FIXED FOR MOBILE
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
            while len(image_urls) < 3:
                image_urls.append("")
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            products_sheet.append_row([new_id, name, price, stock, *image_urls, video_url, desc, "In Stock" if stock > 0 else "Out of Stock"])
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
                    with st.spinner("Loading checkout..."):
                        st.session_state.selected = row
                        st.rerun()

# Order Form
if "selected" in st.session_state:
    p = st.session_state.selected
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🛒 Checkout\n**Product:** {p['name']}")
    with st.form("order"):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name *")
        phone = col1.text_input("Phone *")
        location = col2.text_input("Location *")
        qty = col2.number_input("Quantity *", min_value=1, value=1)
        total = int(p["price"]) * int(qty)
        st.markdown(f"<div class='product-price'>Total: GHS {total}</div>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 Place Order", use_container_width=True) and name and phone and location:
            with st.spinner("🚀 Processing your order..."):
                ref = generate_reference(p["name"], location)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                orders_sheet.append_row([name, phone, location, p["name"], qty, total, ref, timestamp, "Pending"])
                
                email_body = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                        .container {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                        .content {{ padding: 20px; }}
                        .order-detail {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-left: 4px solid #667eea; }}
                        .label {{ font-weight: bold; color: #667eea; }}
                        .total {{ font-size: 24px; color: #28a745; font-weight: bold; margin-top: 20px; }}
                        .footer {{ text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; }}
                    </style>
                </head>
                <body>
                    <div class='container'>
                        <div class='header'>
                            <h1>🛒 NEW ORDER RECEIVED!</h1>
                        </div>
                        <div class='content'>
                            <div class='order-detail'>
                                <span class='label'>📦 Product:</span> {p['name']}
                            </div>
                            <div class='order-detail'>
                                <span class='label'>👤 Customer:</span> {name}
                            </div>
                            <div class='order-detail'>
                                <span class='label'>📱 Phone:</span> <a href='tel:{phone}'>{phone}</a>
                            </div>
                            <div class='order-detail'>
                                <span class='label'>📍 Location:</span> {location}
                            </div>
                            <div class='order-detail'>
                                <span class='label'>🔢 Quantity:</span> {qty}
                            </div>
                            <div class='order-detail'>
                                <span class='label'>🔖 Reference:</span> {ref}
                            </div>
                            <div class='order-detail'>
                                <span class='label'>🕐 Time:</span> {timestamp}
                            </div>
                            <div class='total'>
                                💰 Total: GHS {total}
                            </div>
                        </div>
                        <div class='footer'>
                            <p>Log in to your admin dashboard to manage this order</p>
                            <p><small>Retro Jersey Shop © 2026</small></p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                msg = f"🛒 NEW ORDER!\n📦 {p['name']}\n👤 {name}\n📱 {phone}\n📍 {location}\n💰 GHS {total}\n🔖 {ref}"
                send_telegram_notification(msg)
                
                email_sent = send_email_notification(f"🛒 New Order: {ref}", email_body)
                
                st.cache_data.clear()
                st.markdown(f"<div class='order-success'>✅ Order Placed!<br>Total: GHS {total}<br>Ref: {ref}</div>", unsafe_allow_html=True)
                
                if not email_sent:
                    st.warning("⚠️ Order placed but email notification failed. Please check your email settings.")
                
                del st.session_state.selected
    st.markdown("</div>", unsafe_allow_html=True)

# IMPROVED FOOTER - CLEAR AND READABLE
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
