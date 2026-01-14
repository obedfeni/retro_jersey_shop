# ==============================
# Retro Jersey Shop – Professional Edition
# Hosting: Render
# Backend: Google Sheets
# ==============================

import streamlit as st
import gspread
import pandas as pd
import os, json, base64
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
import random

# ---------------- REFERENCE GENERATOR ----------------
def generate_reference(product_name, location):
    product_code = product_name[:3].upper()
    location_code = location[:3].upper()
    rand = random.randint(1000, 9999)
    return f"RJ-{product_code}-{location_code}-{rand}"

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

# ---------------- HIDE STREAMLIT UI ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ---------------- PROFESSIONAL THEME ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, .stApp { 
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #1a1a2e;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, h4 { 
    color: #1a1a2e;
    font-weight: 700;
}

/* Header Styles */
.header-container {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 20px 40px;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    margin-bottom: 40px;
    display: flex;
    align-items: center;
    gap: 20px;
}

.logo-pro {
    width: 70px;
    height: 70px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 16px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 32px;
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.header-text {
    flex: 1;
}

.header-title {
    font-size: 32px;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0;
    line-height: 1.2;
}

.header-subtitle {
    font-size: 14px;
    color: #64748b;
    margin: 5px 0 0 0;
}

/* Product Card Styles */
.product-card {
    background: white;
    border-radius: 20px;
    padding: 0;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.product-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
}

.product-image-container {
    width: 100%;
    height: 280px;
    overflow: hidden;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    position: relative;
}

.product-image-container img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.product-badge {
    position: absolute;
    top: 15px;
    right: 15px;
    background: rgba(102, 126, 234, 0.95);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    backdrop-filter: blur(10px);
}

.product-content {
    padding: 24px;
    flex: 1;
    display: flex;
    flex-direction: column;
}

.product-name {
    font-size: 20px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 8px;
}

.product-description {
    font-size: 14px;
    color: #64748b;
    line-height: 1.6;
    margin-bottom: 16px;
    flex: 1;
}

.product-price {
    font-size: 28px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 16px;
}

/* Button Styles */
.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 14px 28px;
    font-weight: 600;
    border: none;
    width: 100%;
    font-size: 15px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
}

/* Admin Card */
.admin-card {
    background: white;
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
}

/* Form Styles */
.stTextInput>div>div>input,
.stTextArea>div>div>textarea,
.stNumberInput>div>div>input {
    border-radius: 12px;
    border: 2px solid #e2e8f0;
    padding: 12px 16px;
    font-size: 15px;
    transition: all 0.3s ease;
}

.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus,
.stNumberInput>div>div>input:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* Order Form */
.order-form-container {
    background: white;
    border-radius: 20px;
    padding: 40px;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    margin-top: 40px;
}

/* Success Message */
.success-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 16px;
    margin: 20px 0;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

/* Footer */
.footer-pro {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    padding: 40px;
    text-align: center;
    border-radius: 20px;
    margin-top: 80px;
    box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.1);
}

.footer-links {
    display: flex;
    justify-content: center;
    gap: 30px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.footer-link {
    color: #667eea;
    font-weight: 600;
    text-decoration: none;
    font-size: 15px;
}

/* Status Badge */
.status-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

.status-in-stock {
    background: #d1fae5;
    color: #065f46;
}

.status-out-stock {
    background: #fee2e2;
    color: #991b1b;
}

/* Admin Dashboard */
.admin-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 30px;
    box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
}

.stat-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    text-align: center;
}

.stat-number {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-label {
    color: #64748b;
    font-size: 14px;
    margin-top: 8px;
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
# PROFESSIONAL HEADER
# ==============================
st.markdown("""
<div class='header-container'>
    <div class='logo-pro'>RJ</div>
    <div class='header-text'>
        <h1 class='header-title'>Retro Jersey Shop</h1>
        <p class='header-subtitle'>Premium Vintage Jerseys • Authentic Heritage • Delivered Nationwide</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Secret admin trigger
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    search = st.text_input("🔍 Search", placeholder="Search jerseys...", label_visibility="collapsed")
    if search.strip().lower() == "admin2026":
        st.session_state.show_admin_login = True

# ==============================
# 🔐 ADMIN LOGIN
# ==============================
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Admin Access")
    
    password = st.text_input("Enter Admin Password", type="password")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("🚀 Login", use_container_width=True):
            if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
                st.session_state.admin_logged = True
                st.session_state.show_admin_login = False
                st.success("✅ Admin access granted!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==============================
# 📊 ADMIN DASHBOARD
# ==============================
if st.session_state.admin_logged:
    
    st.markdown("""
    <div class='admin-header'>
        <h1 style='margin:0; color:white;'>📊 Admin Dashboard</h1>
        <p style='margin:5px 0 0 0; color:rgba(255,255,255,0.9);'>Manage products and orders</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Logout", use_container_width=False):
        st.session_state.admin_logged = False
        st.rerun()
    
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
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("## ➕ Add New Product")
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
        add = st.form_submit_button("✨ Add Product", use_container_width=True)
        
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
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("## 📦 Manage Products")
    products_df = load_products()
    
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            st.image(row["image1"], use_column_width=True)
            st.markdown(f"**{row['name']}**")
            st.markdown(f"Stock: {row['stock']} | GHS {row['price']}")
            
            if st.button(f"🗑️ Delete", key=f"del_{row['id']}", use_container_width=True):
                products_sheet.delete_rows(row["_row"])
                st.success("Product deleted!")
                st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ORDERS
    st.markdown("<div class='admin-card'>", unsafe_allow_html=True)
    st.markdown("## 📋 Recent Orders")
    st.dataframe(orders_df, use_container_width=True, height=400)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.stop()

# ==============================
# 🛍️ PUBLIC SHOP
# ==============================
st.markdown("## 🔥 Featured Collection")
st.markdown("<br>", unsafe_allow_html=True)

if products_df.empty:
    st.info("🏗️ No products available at the moment. Check back soon!")
else:
    cols = st.columns(3)
    for idx, row in products_df.iterrows():
        with cols[idx % 3]:
            status_class = "status-in-stock" if row["status"] == "In Stock" else "status-out-stock"
            
            st.markdown(f"""
            <div class='product-card'>
                <div class='product-image-container'>
                    <img src='{row["image1"]}' alt='{row["name"]}'>
                    <div class='product-badge'>{row["status"]}</div>
                </div>
                <div class='product-content'>
                    <div class='product-name'>{row['name']}</div>
                    <div class='product-description'>{row['description']}</div>
                    <div class='product-price'>GHS {row['price']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if row["status"] == "Out of Stock":
                st.button("❌ Out of Stock", key=f"out_{row['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("🛒 Order Now", key=f"order_{row['id']}", use_container_width=True):
                    st.session_state.selected = row

# ==============================
# ORDER FORM
# ==============================
if "selected" in st.session_state:
    p = st.session_state.selected
    
    st.markdown("<div class='order-form-container'>", unsafe_allow_html=True)
    st.markdown(f"## 📝 Complete Your Order")
    st.markdown(f"### {p['name']}")
    
    with st.form("order"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            phone = st.text_input("Phone / WhatsApp *")
        with col2:
            location = st.text_input("Delivery Location *")
            qty = st.number_input("Quantity *", min_value=1, value=1)
        
        total = int(p["price"]) * int(qty)
        st.markdown(f"### Total: **GHS {total}**")
        
        send = st.form_submit_button("🚀 Submit Order", use_container_width=True)
        
        if send and name and phone and location:
            reference = generate_reference(p["name"], location)
            
            orders_sheet.append_row([
                name,
                phone,
                location,
                p["name"],
                qty,
                total,
                reference,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Pending"
            ])
            
            st.markdown(f"""
            <div class='success-box'>
                <h2 style='color:white; margin:0 0 15px 0;'>🎉 Order Received Successfully!</h2>
                <p style='margin:0; font-size:16px;'>
                    Your order has been placed. We'll contact you via WhatsApp or SMS with your unique reference code for payment.
                </p>
                <p style='margin:15px 0 0 0; font-size:18px; font-weight:600;'>
                    Total Amount: GHS {total}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            del st.session_state.selected
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# PROFESSIONAL FOOTER
# ==============================
st.markdown("""
<div class='footer-pro'>
    <div class='footer-links'>
        <a href='#' class='footer-link'>📞 0541468102</a>
        <a href='#' class='footer-link'>📱 Snapchat: @retroshop</a>
        <a href='#' class='footer-link'>📍 Accra, Ghana</a>
    </div>
    <p style='color:#64748b; margin:20px 0 0 0; font-size:14px;'>
        © 2026 Retro Jersey Shop • Relive the Heritage • Premium Vintage Collection
    </p>
</div>
""", unsafe_allow_html=True)
