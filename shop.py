import streamlit as st
from firebase import get_products, place_order
import uuid

def shop_page():
    st.markdown('<div class="header">RETRO JERSEY GHANA</div>', unsafe_allow_html=True)

    products = get_products()
    for i in range(0, len(products), 3):
        cols = st.columns(3)
        for j, product in enumerate(products[i:i+3]):
            col = cols[j]
            with col:
                images = product.get("images", [])
                if images:
                    st.image(images[0], use_column_width=True)

                st.markdown(f"<h3>{product['name']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p class='price'>GH₵ {product['price']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p>Available: {product.get('quantity', 'N/A')}</p>", unsafe_allow_html=True)

                if st.button("Buy Now", key=f"buy_{product['id']}"):
                    with st.form(key=f"order_form_{product['id']}"):
                        st.subheader(f"Order: {product['name']}")
                        name = st.text_input("Your Name")
                        phone = st.text_input("Phone Number")
                        location = st.text_input("Location")
                        payment = st.text_input("Payment Info / Momo Reference")
                        submitted = st.form_submit_button("Place Order")
                        if submitted:
                            order = {
                                "id": str(uuid.uuid4()),
                                "product_name": product['name'],
                                "price": product['price'],
                                "customer_name": name,
                                "phone": phone,
                                "location": location,
                                "payment": payment
                            }
                            place_order(order)
                            st.success("✅ Order placed successfully!")
