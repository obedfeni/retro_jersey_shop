import streamlit as st
from firebase_admin import credentials, initialize_app, firestore

# Load Firebase service account from Streamlit secrets (already a dict)
firebase_json = dict(st.secrets["FIREBASE_KEY"])

# Convert escaped \n into real newlines in private key
firebase_json["private_key"] = firebase_json["private_key"].replace("\\n", "\n")

# Initialize Firebase app only once
if not hasattr(st.session_state, "firebase_initialized"):
    cred = credentials.Certificate(firebase_json)
    initialize_app(cred)
    st.session_state.firebase_initialized = True

# Firestore client
db = firestore.client()


# -------------------------------
# PRODUCT FUNCTIONS
# -------------------------------

def get_products():
    products_ref = db.collection("products")
    docs = products_ref.stream()
    products = []

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        products.append(data)

    return products


# -------------------------------
# ORDER FUNCTIONS
# -------------------------------

def place_order(order_data):
    orders_ref = db.collection("orders")
    orders_ref.document(order_data["id"]).set(order_data)
