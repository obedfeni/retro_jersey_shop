import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import base64

# --- Page Config ---
st.set_page_config(page_title="Retro Jersey Shop", layout="wide")

# --- Load CSS ---
with open("theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Google Sheets Auth ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# --- Load Sheets ---
products_sheet = client.open("retro_jersey_shop").worksheet("products")
orders_sheet = client.open("retro_jersey_shop").worksheet("orders")
products_df = pd.DataFrame(products_sheet.get_all_records())
orders_df = pd.DataFrame(orders_sheet.get_all_records())

# ------------------------
# Navigation
# ------------------------
# Admin link is unique and private
admin_key = "my-unique-admin-link-123"  # change to your unique key
url_params = st.experimental_get_query_params()
page = "Shop"
if "admin" in url_params and url_params["admin"][0] == admin_key:
    page = "Admin Dashboard"

# ==========================
# SHOP PAGE
# ==========================
if page == "Shop":
    st.markdown("<h1 style='text-align:center;'>Retro Jersey Shop</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>High-quality retro jerseys delivered to your door!</p>", unsafe_allow_html=True)
    st.markdown("---")

    num_columns = 3
    cols = st.columns(num_columns)

    for idx, row in products_df.iterrows():
        col = cols[idx % num_columns]
        with col:
            st.markdown(f"<div class='product-card'>", unsafe_allow_html=True)
            st.image(row["image_url"], use_column_width='always')
            st.markdown(f"<h3>{row['name']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p>{row['description']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p><strong>Price: ${row['price']}</strong></p>", unsafe_allow_html=True)

            # Button to go to order page for this product
            order_button = st.button(f"Order {row['name']}", key=f"orderbtn_{row['id']}")
            if order_button:
                st.session_state["selected_product"] = row["id"]
                st.experimental_rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    # If a product was selected, show order form
    if "selected_product" in st.session_state:
        selected_product_id = st.session_state["selected_product"]
        product = products_df[products_df["id"] == selected_product_id].iloc[0]

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"<h2>Order {product['name']}</h2>", unsafe_allow_html=True)
        with st.form("order_form"):
            name = st.text_input("Your Name")
            phone = st.text_input("Phone/WhatsApp")
            location = st.text_input("Delivery Location")
            qty = st.number_input("Quantity", min_value=1, step=1)
            amount = st.number_input("Amount Paid", min_value=0)
            submit = st.form_submit_button("Place Order")

            if submit:
                if name and phone and location and qty > 0 and amount > 0:
                    orders_sheet.append_row([
                        name, phone, location, product["id"], qty, amount, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ])
                    st.success("✅ Order submitted successfully!")
                    st.balloons()
                    del st.session_state["selected_product"]
                else:
                    st.warning("⚠ Fill all fields correctly")

    # Contact info
    st.markdown("<div class='contact-info'>", unsafe_allow_html=True)
    st.markdown("<h3>Contact Us</h3>", unsafe_allow_html=True)
    st.markdown("<p>Email: retroshop@example.com</p>", unsafe_allow_html=True)
    st.markdown("<p>Phone/WhatsApp: +233541468102</p>", unsafe_allow_html=True)
    st.markdown("<p>snapchat: @retroshop</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================
# ADMIN DASHBOARD
# ==========================
if page == "Admin Dashboard":
    st.markdown("<h1 style='text-align:center;'>Admin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Manage products and view orders</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Upload new product
    st.subheader("Add New Product")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        price = st.number_input("Price", min_value=0)
        description = st.text_area("Description")
        image_file = st.file_uploader("Upload Image", type=["png","jpg","jpeg"])
        submit = st.form_submit_button("Add Product")

        if submit:
            if name and price and description and image_file:
                image_bytes = image_file.read()
                encoded_image = base64.b64encode(image_bytes).decode()
                image_url = f"data:image/png;base64,{encoded_image}"
                next_id = (products_df['id'].max() + 1) if not products_df.empty else 1
                products_sheet.append_row([next_id, name, price, image_url, description])
                st.success("✅ Product added successfully!")
            else:
                st.warning("⚠ Fill all fields and upload an image")

    # View orders
    st.subheader("Received Orders")
    orders_df = pd.DataFrame(orders_sheet.get_all_records())  # reload latest orders
    st.dataframe(orders_df)
