import streamlit as st

ADMIN_USERNAME = "admin_user"
ADMIN_PASSWORD = "secure_pass_2026"

st.set_page_config(page_title="Admin Login", page_icon="🔐")

st.title("🔐 Admin Panel Login")

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_logged_in = True
            st.success("Login successful")
            st.rerun()
        else:
            st.error("Invalid credentials")

else:
    st.title("📊 Admin Dashboard")
    st.write("Welcome, admin!")
    st.write("Here you can manage orders, products, and settings.")
    
    if st.button("Logout"):
        st.session_state.admin_logged_in = False
        st.rerun()

