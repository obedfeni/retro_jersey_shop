# ==============================
# Retro Jersey Shop – Final Production App
# Hosting: Render
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

def load_products_with_rows():
    records = products_sheet.get_all_records()
    rows = []
    for i, r in enumerate(records, start=2):
        r["_row"] = i
        rows.append(r)
    return pd.DataFrame(rows)

products_df = load_products_with_rows()

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

    # -------- ADD PRODUCT --------
    st.markdown("## ➕ Add Product")

    with st.form("add_product"):
        name = st.text_input("Product name")
        price = st.number_input("Price", min_value=0)
        desc = st.text_area("Description")
        images = st.file_uploader(
            "Upload up to 3 images",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True
        )
        stock = st.number_input("Stock Quantity", min_value=0)
        add = st.form_submit_button("Add Product")

        if add and name and price and desc and images:
            encoded_images = []
            for img in images[:3]:
                encoded = base64.b64encode(img.read()).decode()
                encoded_images.append(f"data:image/png;base64,{encoded}")

            while len(encoded_images) < 3:
                encoded_images.append("")

            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1

            products_sheet.append_row([
                new_id,
                name,
                price,
                encoded_images[0],
                encoded_images[1],
                encoded_images[2],
                desc,
                stock
            ])

            st.success("✅ Product added successfully")
            st.rerun()

    # -------- MANAGE PRODUCTS --------
    st.markdown("## 🗑️ Manage Products")

    if products_df.empty:
        st.info("No products available")
    else:
        for _, row in products_df.iterrows():
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            st.image(row.get("image_1"), width=200)
            st.markdown(f"### {row['name']}")
            st.markdown(f"Price: GHS {row['price']}")
            st.markdown(f"Stock: {row.get('stock', 0)}")

            confirm = st.checkbox(
                f"Confirm delete {row['name']}",
                key=f"confirm_{row['id']}"
            )

            if st.button("Delete Product", key=f"delete_{row['id']}"):
                if confirm:
                    products_sheet.delete_rows(row["_row"])
                    st.success(f"🗑️ {row['name']} deleted")
                    st.rerun()
                else:
                    st.warning("Please confirm deletion")

            st.markdown("</div>", unsafe_allow_html=True)

    # -------- ORDERS --------
    st.markdown("## 📦 Orders")

    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    st.dataframe(orders_df, use_container_width=True)

    if not orders_df.empty:
        st.markdown("### 🚚 Update Order Status")

        order_index = st.selectbox(
            "Select Order",
            orders_df.index,
            format_func=lambda i: f"{orders_df.loc[i,'name']} - {orders_df.loc[i,'status']}"
        )

        new_status = st.selectbox(
            "New Status",
            ["Pending", "Paid", "Delivered"]
        )

        if st.button("Update Status"):
            orders_sheet.update_cell(order_index + 2, 7, new_status)
            st.success("Order status updated")
            st.rerun()

# ==============================
# PUBLIC SHOP PAGE
# ==============================
else:
    st.markdown("# Retro Jersey Shop")
    st.markdown("### Premium retro jerseys delivered to your door")
    st.markdown("---")

    search = st.text_input("🔍 Search jerseys")

    if search:
        products_df = products_df[
            products_df["name"].str.contains(search, case=False, na=False)
        ]

    if products_df.empty:
        st.info("No products available")
        st.stop()

    cols = st.columns(3)

    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            images = [row.get("image_1"), row.get("image_2"), row.get("image_3")]
            for img in images:
                if img:
                    st.image(img, width=280)

            st.markdown(f"### {row['name']}")
            st.markdown(f"<p class='small'>{row['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"**Price:** GHS {row['price']}")

            if row.get("stock", 0) <= 0:
                st.markdown("### ❌ Out of Stock")
            else:
                if st.button("Order", key=f"order_{row['id']}"):
                    st.session_state.selected = row

            st.markdown("</div>", unsafe_allow_html=True)

    # -------- ORDER FORM --------
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
                    name,
                    phone,
                    location,
                    p["id"],
                    qty,
                    amount,
                    "Pending",
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
                st.success("🎉 Order received")
                del st.session_state.selected

    # -------- CONTACT --------
    st.markdown("---")
    st.markdown("📞 0541468102")
    st.markdown("WhatsApp: +233541468102")
    st.markdown("Instagram: @retroshop")
