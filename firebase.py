import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Read FIREBASE_KEY from secrets
key_str = st.secrets["FIREBASE_KEY"]

# Parse JSON
firebase_json = json.loads(key_str)

# Ensure private_key newlines are real
firebase_json["private_key"] = firebase_json["private_key"].encode().decode("unicode_escape")

# Initialize Firebase once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_json)
    firebase_admin.initialize_app(
        cred,
        {"storageBucket": f"{firebase_json['project_id']}.appspot.com"}
    )

db = firestore.client()
bucket = storage.bucket()
