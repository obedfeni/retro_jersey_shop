import streamlit as st

def require_admin(email_input):
    admin_email = "obedfeni23@gmail.com"  # your admin email
    if email_input == admin_email:
        st.session_state["admin_logged_in"] = True
        return True
    else:
        st.error("❌ Not authorized")
        return False
