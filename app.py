import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64
import json

# =====================
# CONFIG
# =====================
st.set_page_config(page_title="Retro Jersey Shop", layout="wide")

ADMIN_USERNAME = "retro_admin"
ADMIN_PASSWORD = "RetroShop@2026"

# =====================
# STYLE
# =====================
st.markdown("""
<style>
#MainMenu, footer, header {visibility: hidden;}
.stButton button {
    background-color:#2563eb;
    color:white;
    border-radius:10px;
    font-weight:600;
}
.card {
    background:white;
    padding:15px;
    border-radius:14px;
    box-shadow:0 6px 18px rgba(0,0,0,.08);
}
</style>
""", unsafe_allow_html=True)

# =====================
# GOOGLE SHEETS AUTH
# =====================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)
client = gspread.authorize(creds)

products_sheet = client.open("retro_jersey_shop").worksheet("products")
orders_sheet = client.open("retro_jersey_shop").worksheet("orders")

products_df = pd.DataFrame(products_sheet.get_all_records())

# =====================
# ROUTING
# =====================
params = st.query_params
page = params.get("page", "shop")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# =====================
# SHOP PAGE
# =====================
if page == "shop":
    st.title("👕 Retro Jersey Shop")
    st.write("High-quality retro jerseys delivered to your door.")

    cols = st.columns(3)
    for i, row in products_df.iterrows():
        with cols[i % 3]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.image(row["image_url"], use_column_width=True)
            st.subheader(row["name"])
            st.write(row["description"])
            st.write(f"**Price:** ${row['price']}")

            if st.button("Order", key=row["id"]):
                st.session_state["product"] = row
            st.markdown("</div>", unsafe_allow_html=True)

    if "product" in st.session_state:
        p = st.session_state["product"]
        st.divider()
        st.subheader(f"Order: {p['name']}")

        with st.form("order"):
            name = st.text_input("Your Name")
            phone = st.text_input("Phone / WhatsApp")
            location = st.text_input("Delivery Location")
            qty = st.number_input("Quantity", min_value=1)
            amount = st.number_input("Amount Paid", min_value=0)
            submit = st.form_submit_button("Submit Order")

            if submit and name and phone and location:
                orders_sheet.append_row([
                    name, phone, location, p["id"], qty, amount,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ])
                st.success("Order submitted!")
                del st.session_state["product"]

# =====================
# ADMIN LOGIN
# =====================
elif page == "admin" and not st.session_state.admin_logged_in:
    st.title("🔐 Admin Login")

    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button("Login"):
        if u == ADMIN_USERNAME and p == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.query_params = {"page": "admin"}
            st.rerun()
        else:
            st.error("Invalid credentials")

# =====================
# ADMIN DASHBOARD
# =====================
elif page == "admin" and st.session_state.admin_logged_in:
    st.title("📊 Admin Dashboard")

    # ADD PRODUCT
    st.subheader("Add New Product")
    with st.form("add_product"):
        name = st.text_input("Name")
        price = st.number_input("Price", min_value=0)
        desc = st.text_area("Description")
        img = st.file_uploader("Upload Image", type=["jpg","png"])
        add = st.form_submit_button("Add Product")

        if add and img:
            img64 = base64.b64encode(img.read()).decode()
            image_url = f"data:image/png;base64,{img64}"
            new_id = int(products_df["id"].max()) + 1 if not products_df.empty else 1
            products_sheet.append_row([new_id, name, price, image_url, desc])
            st.success("Product added")
            st.rerun()

    # VIEW ORDERS
    st.subheader("Orders")
    orders_df = pd.DataFrame(orders_sheet.get_all_records())
    st.dataframe(orders_df)

    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.query_params = {"page": "shop"}
        st.rerun()
