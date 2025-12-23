import streamlit as st
from firebase import add_product, get_products, update_product_quantity
from auth import require_admin

def admin_page():
    st.title("🛠️ Admin Dashboard")

    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if not st.session_state["admin_logged_in"]:
        email = st.text_input("Admin Email")
        if st.button("Login"):
            require_admin(email)
    else:
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            name = st.text_input("Product Name")
            price = st.number_input("Price", min_value=0.0)
            quantity = st.number_input("Quantity", min_value=0)
            image_urls = st.text_area("Image URLs (comma separated)")
            submitted = st.form_submit_button("Add Product")
            if submitted:
                product = {
                    "name": name,
                    "price": price,
                    "quantity": quantity,
                    "images": [url.strip() for url in image_urls.split(",") if url.strip()]
                }
                add_product(product)
                st.success("✅ Product added!")

        st.subheader("Existing Products")
        products = get_products()
        for p in products:
            st.markdown(f"- {p['name']} (Qty: {p['quantity']})")
            new_qty = st.number_input(f"Update quantity for {p['name']}", value=p['quantity'], key=p['id'])
            if st.button(f"Update {p['name']}", key=f"upd_{p['id']}"):
                update_product_quantity(p['id'], new_qty)
                st.success(f"✅ Updated {p['name']}")
