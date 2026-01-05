import streamlit as st
from firebase_admin import credentials, initialize_app, firestore

# Get Firebase key directly as dict (no json.loads!)
firebase_json = dict(st.secrets["FIREBASE_KEY"])

# Convert escaped newlines in private key
firebase_json["private_key"] = firebase_json["private_key"].replace("\\n", "\n")

# Initialize Firebase once
if "firebase_initialized" not in st.session_state:
    cred = credentials.Certificate(firebase_json)
    initialize_app(cred)
    st.session_state["firebase_initialized"] = True

# Firestore client
db = firestore.client()


# -------------------------------
# PRODUCTS
# -------------------------------
def get_products():
    products = []
    for doc in db.collection("products").stream():
        item = doc.to_dict()
        item["id"] = doc.id
        products.append(item)
    return products


# -------------------------------
# ORDERS
# -------------------------------
def place_order(order_data):
    db.collection("orders").document(order_data["id"]).set(order_data)
