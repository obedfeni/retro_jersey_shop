import streamlit as st
from shop import shop_page
from admin import admin_page
from orders import orders_page

# Load CSS
with open("theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.sidebar.title("Menu")
page = st.sidebar.radio("Go to", ["Shop", "Admin", "Orders"])

if page == "Shop":
    shop_page()
elif page == "Admin":
    admin_page()
elif page == "Orders":
    orders_page()
