# firebase.py
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Load Firebase key from Streamlit secrets
try:
    firebase_key_str = st.secrets["FIREBASE_KEY"]
except KeyError:
    st.error("FIREBASE_KEY not found in Streamlit secrets!")
    st.stop()

# Convert JSON string to dict
try:
    firebase_json = json.loads(firebase_key_str)
except json.JSONDecodeError as e:
    st.error(f"Invalid Firebase JSON: {e}")
    st.stop()

# Fix line breaks in private_key
firebase_json["private_key"] = firebase_json["private_key"].replace("\\n", "\n")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(
        cred,
        {"storageBucket": f"{firebase_json['project_id']}.appspot.com"}
    )

# Firestore and Storage clients
db = firestore.client()
bucket = storage.bucket()
