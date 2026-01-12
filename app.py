# ==============================
# Retro Jersey Shop – Production App
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

# ---------------- HIDE STREAMLIT UI ----------------
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

# ---------------- GLOBAL THEME ----------------
st.markdown("""
<style>
html, body, .stApp { background:#f0f6ff; color:#0d1b2a; }
h1,h2,h3,h4 { color:#1e3a8a }
.stButton>button {
    background:#2563eb; color:white; border-radius:12px;
    padding:10px 16px; font-weight:600; border:none
}
.stButton>button:hover { background:#1e40af }
.card {
    background:white; padding:16px; border-radius:16px;
    box-shadow:0 8px 20px rgba(0,0,0,.08);
    margin-bottom:20px
}
.small { font-size:0.9rem; color:#334155 }
.logo {
    width:55px;
    height:55px;
    background:#2563eb;
    border-radius:10px;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:800;
    font-size:22px;
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
    st.error("Server configuration error")
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
# HEADER + SECRET ADMIN TRIGGER
# ==============================
col1, col2, col3 = st.columns([0.1, 0.6, 0.3])

with col1:
    st.markdown("<div class='logo'>R</div>", unsafe_allow_html=True)

with col2:
    st.markdown("## Retro Jersey Shop")
    st.markdown("<p class='small'>Premium retro jerseys delivered to your door</p>", unsafe_allow_html=True)

with col3:
    search = st.text_input("Search", placeholder="Search jerseys...")
    if search.strip().lower() == "admin2026":
        st.session_state.show_admin_login = True

st.markdown("---")

# ==============================
# 🔐 ADMIN LOGIN (SECRET)
# ==============================
if st.session_state.show_admin_login and not st.session_state.admin_logged:
    st.markdown("### 🔐 Admin Login")

    password = st.text_input("Admin Password", type="password")

    if st.button("Login"):
        if password == os.environ.get("ADMIN_PASSWORD", "change_me"):
            st.session_state.admin_logged = True
            st.session_state.show_admin_login = False
            st.success("Admin access granted")
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()

# ==============================
# 📊 ADMIN DASHBOARD
# ==============================
if st.session_state.admin_logged:

    st.markdown("# 📊 Admin Dashboard")

    if st.button("🚪 Logout"):
        st.session_state.admin_logged = False
        st.rerun()

    # ADD PRODUCT
    st.markdown("## ➕ Add Product")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0)
        stock = st.number_input("Stock Quantity", min_value=0)
        desc = st.text_area("Description")
        images = st.file_uploader(
            "Upload up to 3 images",
            type=["png","jpg","jpeg"],
            accept_multiple_files=True
        )
        add = st.form_submit_button("Add Product")

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

            st.success("✅ Product added")
            st.rerun()

    # MANAGE PRODUCTS
    st.markdown("## 🗑️ Manage Products")
    products_df = load_products()
    for _, row in products_df.iterrows():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image(row["image1"], width=180)
        st.markdown(f"**{row['name']}**")
        st.markdown(f"Stock: {row['stock']} | Status: {row['status']}")

        if st.button(f"Delete {row['name']}", key=f"del_{row['id']}"):
            products_sheet.delete_rows(row["_row"])
            st.success("Product deleted")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ORDERS
    st.markdown("## 📦 Orders")
    orders_df = pd.DataFrame(
        orders_sheet.get_all_records(expected_headers=[
            "name","phone","location","items",
            "qty","amount","reference","timestamp","status"
        ])
    )
    st.dataframe(orders_df, use_container_width=True)

    st.stop()

# ==============================
# 🛍️ PUBLIC SHOP
# ==============================
if products_df.empty:
    st.info("No products available")
else:
    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.image(row["image1"], width=260)
            st.markdown(f"### {row['name']}")
            st.markdown(f"<p class='small'>{row['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"**Price:** GHS {row['price']}")

            if row["status"] == "Out of Stock":
                st.error("Out of Stock")
            else:
                if st.button("Order", key=f"order_{row['id']}"):
                    st.session_state.selected = row

            st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# ORDER FORM
# ==============================
if "selected" in st.session_state:
    p = st.session_state.selected
    st.markdown("---")
    st.markdown(f"## Order: {p['name']}")

    with st.form("order"):
        name = st.text_input("Your Name")
        phone = st.text_input("Phone / WhatsApp")
        location = st.text_input("Delivery Location")
        qty = st.number_input("Quantity", min_value=1)
        send = st.form_submit_button("Submit Order")

        if send and name and phone and location:
            reference = generate_reference(p["name"], location)

            orders_sheet.append_row([
                name,
                phone,
                location,
                items["name"],
                qty,
                amount["price"],
                reference,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Pending"
            ])

            st.success("🎉 Order received!")

            st.markdown("""
            ### 📌 Payment Reference
            Your payment reference will be sent to you via WhatsApp or SMS.

            Please use it when making your Mobile Money payment.
            You will be contacted shortly.
            """)

            del st.session_state.selected

# ==============================
# FOOTER
# ==============================
st.markdown("""
<div style="margin-top:80px;padding:32px;text-align:center;color:#64748b">
 📞 0541468102<br>
 Snapchat: @retroshop<br><br>
 © 2026 Retro Jersey Shop · Accra, Ghana · Relive the heritage
</div>
""", unsafe_allow_html=True)

