# ==============================
# Retro Jersey Shop – Final Production App
# Hosting: Render (NO Streamlit Cloud UI)
# Backend: Google Sheets
# ==============================

import streamlit as st
import gspread
import pandas as pd
import os, json, base64
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Retro Jersey Shop",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- HIDE STREAMLIT UI ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ---------------- THEME ----------------
st.markdown("""
<style>
html, body, .stApp { background: #f0f6ff; color: #0d1b2a; }
h1,h2,h3,h4 { color:#1e3a8a }
.stButton>button {
    background:#2563eb; color:white; border-radius:12px;
    padding:10px 16px; font-weight:600; border:none
}
.stButton>button:hover { background:#1e40af }
.card {
    background:white; padding:16px; border-radius:16px;
    box-shadow:0 8px 20px rgba(0,0,0,.08); margin-bottom:20px
}
.small { font-size:0.9rem; color:#334155 }
</style>
""", unsafe_allow_html=True)

# ---------------- GOOGLE SHEETS AUTH ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

raw_creds = os.environ.get("GCP_SERVICE_ACCOUNT")
if not raw_creds:
    st.error("Server configuration error")
    st.stop()

creds_dict = json.loads(raw_creds)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ---------------- LOAD SHEETS ----------------
SHEET_NAME = "retro_jersey_shop"
products_sheet = client.open(SHEET_NAME).worksheet("products")
orders_sheet = client.open(SHEET_NAME).worksheet("orders")

products_df = pd.DataFrame(products_sheet.get_all_records())

# ---------------- ADMIN AUTH ----------------
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change_me")

query = st.query_params
is_admin = query.get("admin") == "true"

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# ==============================
# ADMIN LOGIN PAGE
# ==============================
if is_admin and not st.session_state.admin_logged:
    st.markdown("## 🔐 Admin Login")
    with st.form("login"):
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

        if login:
            if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
                st.session_state.admin_logged = True
                st.rerun()
            else:
                st.error("Invalid credentials")

# ==============================
# ADMIN DASHBOARD
# ==============================
elif is_admin and st.session_state.admin_logged:
    st.markdown("# 📊 Admin Dashboard")

    # ADD PRODUCT
    st.markdown("## ➕ Add Product")
    with st.form("add_product"):
        name = st.text_input("Product name")
        price = st.number_input("Price", min_value=0)
        desc = st.text_area("Description")
        img = st.file_uploader("Image", type=["png","jpg","jpeg"])
        add = st.form_submit_button("Add")

        if add and name and price and desc and img:
            img_b64 = base64.b64encode(img.read()).decode()
            img_url = f"data:image/png;base64,{img_b64}"
            new_id = int(products_df['id'].max()) + 1 if not products_df.empty else 1
            products_sheet.append_row([
                new_id, name, price, img_url, desc
            ])
            st.success("Product added")
            st.rerun()

    # VIEW ORDERS
    st.markdown("## 📦 Orders")
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    st.dataframe(orders_df, use_container_width=True)

# ==============================
# PUBLIC SHOP PAGE
# ==============================
else:
    st.markdown("# Retro Jersey Shop")
    st.markdown("### Premium retro jerseys delivered to your door")
    st.markdown("---")

    if products_df.empty:
        st.info("No products yet")
        st.stop()

    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.image(row['image_url'], use_column_width=True)
            st.markdown(f"### {row['name']}")
            st.markdown(f"<p class='small'>{row['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"**Price:** GHS {row['price']}")

            if st.button("Order", key=f"order_{row['id']}"):
                st.session_state.selected = row

            st.markdown("</div>", unsafe_allow_html=True)

    # ORDER FORM
    if "selected" in st.session_state:
        p = st.session_state.selected
        st.markdown("---")
        st.markdown(f"## Order: {p['name']}")

        with st.form("order"):
            name = st.text_input("Your Name")
            phone = st.text_input("Phone / WhatsApp")
            location = st.text_input("Delivery Location")
            qty = st.number_input("Quantity", min_value=1)
            amount = st.number_input("Amount Paid", min_value=0)
            send = st.form_submit_button("Submit Order")

            if send and name and phone and location:
                orders_sheet.append_row([
                    name, phone, location, p['id'], qty, amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
                st.success("Order received 🎉")
                del st.session_state.selected

    # CONTACT
    st.markdown("---")
    st.markdown("0541468102 📞 Contact")
    st.markdown("WhatsApp: +233541468102 ")
    st.markdown("Instagram: @retroshop")
