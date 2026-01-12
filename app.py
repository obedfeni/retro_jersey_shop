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

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Retro Jersey Shop",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------- GLOBAL CSS ----------------
st.markdown("""
<style>
#MainMenu, footer, header {visibility:hidden;}
.stDeployButton {display:none;}

html, body, .stApp {
  background:#f8fafc;
  color:#0f172a;
  font-family: Inter, system-ui, sans-serif;
}

/* HEADER */
.shop-header {
  display:flex;
  justify-content:space-between;
  align-items:center;
  padding:24px 40px;
  border-bottom:1px solid #e5e7eb;
}
.brand {
  display:flex;
  align-items:center;
  gap:12px;
}
.logo {
  width:40px;
  height:40px;
  background:#2563eb;
  color:white;
  font-weight:800;
  border-radius:8px;
  display:flex;
  align-items:center;
  justify-content:center;
}
.brand h1 {
  font-size:1.6rem;
  margin:0;
}
.menu-btn {
  font-size:26px;
  background:none;
  border:none;
  cursor:pointer;
}

/* CARDS */
.card {
  background:white;
  padding:16px;
  border-radius:16px;
  box-shadow:0 8px 20px rgba(0,0,0,.06);
  margin-bottom:24px;
}
.small { color:#64748b; font-size:0.9rem }

/* FOOTER */
.footer {
  background:#0f172a;
  color:white;
  padding:64px 24px 32px;
  margin-top:80px;
}
.footer-container {
  max-width:1200px;
  margin:auto;
}
.footer-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
  gap:48px;
}
.footer h3 {
  font-size:0.75rem;
  letter-spacing:0.12em;
  color:#94a3b8;
}
.footer p, .footer a {
  color:#94a3b8;
  font-size:0.9rem;
  line-height:1.6;
  text-decoration:none;
}
.footer a:hover { color:white }
.footer-bottom {
  border-top:1px solid #1e293b;
  margin-top:48px;
  padding-top:24px;
  text-align:center;
  font-size:0.8rem;
  color:#64748b;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<div class="shop-header">
  <div class="brand">
    <div class="logo">R</div>
    <h1>Retro Jersey</h1>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- ADMIN STATE ----------------
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = False
if "show_admin_login" not in st.session_state:
    st.session_state.show_admin_login = False

# ---------------- ADMIN MENU (TOP-RIGHT) ----------------
col1, col2 = st.columns([0.94, 0.06])
with col2:
    if st.button("⋮"):
        st.session_state.show_admin_login = not st.session_state.show_admin_login

# ---------------- ADMIN LOGIN ----------------
if st.session_state.show_admin_login and not st.session_state.admin_mode:
    st.markdown("### 🔐 Admin Login")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Enter Admin Mode"):
        if pw == os.environ.get("ADMIN_PASSWORD", "change_me"):
            st.session_state.admin_mode = True
            st.session_state.show_admin_login = False
            st.rerun()
        else:
            st.error("Wrong password")

# ---------------- GOOGLE SHEETS ----------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(os.environ["GCP_SERVICE_ACCOUNT"]),
    scope
)
client = gspread.authorize(creds)

products_sheet = client.open("retro_jersey_shop").worksheet("products")
orders_sheet = client.open("retro_jersey_shop").worksheet("orders")

def load_products():
    rows = []
    records = products_sheet.get_all_records(expected_headers=[
        "id","name","price","stock",
        "image1","image2","image3",
        "description","status"
    ])
    for i, r in enumerate(records, start=2):
        r["_row"] = i
        rows.append(r)
    return pd.DataFrame(rows)

products_df = load_products()

# ==============================
# ADMIN DASHBOARD
# ==============================
if st.session_state.admin_mode:

    st.markdown("## 📊 Admin Dashboard")

    if st.button("🚪 Exit Admin Mode"):
        st.session_state.admin_mode = False
        st.rerun()

    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0)
        stock = st.number_input("Stock Quantity", min_value=0)
        desc = st.text_area("Description")
        images = st.file_uploader("Upload up to 3 images", accept_multiple_files=True)
        add = st.form_submit_button("Add Product")

        if add and name and images:
            imgs = []
            for img in images[:3]:
                imgs.append(f"data:image/png;base64,{base64.b64encode(img.read()).decode()}")
            while len(imgs) < 3:
                imgs.append("")

            status = "In Stock" if stock > 0 else "Out of Stock"
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1

            products_sheet.append_row([
                new_id, name, price, stock,
                imgs[0], imgs[1], imgs[2],
                desc, status
            ])
            st.success("Product added")
            st.rerun()

    st.markdown("### 🗑️ Manage Products")
    products_df = load_products()
    for _, row in products_df.iterrows():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.image(row["image1"], width=180)
        st.markdown(f"**{row['name']}** — {row['status']}")
        if st.button(f"Delete {row['name']}", key=f"d{row['id']}"):
            products_sheet.delete_rows(row["_row"])
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ==============================
# SHOP PAGE
# ==============================
else:
    st.markdown("## Premium Retro Jerseys")

    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.image(row["image1"], width=260)
            st.markdown(f"### {row['name']}")
            st.markdown(f"<p class='small'>{row['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"**GHS {row['price']}**")

            if row["status"] == "Out of Stock":
                st.error("Out of Stock")
            else:
                if st.button("Order", key=row["id"]):
                    st.session_state.selected = row
            st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
  <div class="footer-container">
    <div class="footer-grid">
      <div>
        <div class="brand">
          <div class="logo">R</div>
          <h2>Retro Jersey</h2>
        </div>
        <p>Curating iconic football moments through premium retro jerseys. Based in Accra, shipping nationwide.</p>
      </div>
      <div>
        <h3>SUPPORT</h3>
        <p><a href="#">Shipping Policy</a></p>
        <p><a href="#">Size Guide</a></p>
      </div>
      <div>
        <h3>CONTACT</h3>
        <p>📞 054 146 8102</p>
        <p>📍 East Legon, Accra</p>
      </div>
    </div>
    <div class="footer-bottom">
      © 2026 Retro Jersey Shop. All rights reserved.
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
