import gspread
import pandas as pd
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Retro Jersey Shop")

# ---- Google Sheets Auth (via Streamlit Secrets) ----
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# ---- Load Sheets ----
products_sheet = client.open("retro_jersey_shop").worksheet("products")
orders_sheet   = client.open("retro_jersey_shop").worksheet("orders")

products_df = pd.DataFrame(products_sheet.get_all_records())

st.title("Retro Jersey Shop")
st.write("Select a jersey and place your order below.")

# ---- Display Products & Order Form ----
for _, row in products_df.iterrows():
    st.divider()
    st.image(row["image_url"], width=260)
    st.subheader(row["name"])
    st.write("Price:", row["price"])
    st.write(row["description"])

    qty = st.number_input(
        f"Quantity for {row['name']}",
        min_value=1, step=1, key=f"qty_{row['id']}"
    )

    name = st.text_input("Customer Name", key=f"name_{row['id']}")
    phone = st.text_input("Phone Number", key=f"phone_{row['id']}")
    location = st.text_input("Delivery Location", key=f"loc_{row['id']}")

    total = int(row["price"]) * qty
    st.write("Total Amount:", total)

    if st.button("Place Order", key=f"order_{row['id']}"):
        if name and phone and location:
            orders_sheet.append_row([
                name,
                phone,
                location,
                row["id"],
                qty,
                total,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            st.success("Order submitted successfully!")
            st.balloons()
        else:
            st.warning("Please fill in all fields before submitting.")

st.divider()
st.caption("Powered by Streamlit + Google Sheets")
