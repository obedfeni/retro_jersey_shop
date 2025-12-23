import streamlit as st
from firebase import db

def orders_page():
    st.title("📦 Orders")
    orders_ref = db.collection("orders")
    for doc in orders_ref.stream():
        order = doc.to_dict()
        st.markdown(f"""
        **Product:** {order['product_name']}
        **Customer:** {order['customer_name']}
        **Phone:** {order['phone']}
        **Location:** {order['location']}
        **Payment:** {order['payment']}
        ---""")
