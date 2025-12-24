# firebase.py
import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage

if not firebase_admin._apps:
    firebase_json = json.loads(st.secrets["FIREBASE_KEY"])
    cred = credentials.Certificate(firebase_json)

    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": f"{firebase_json['project_id']}.appspot.com"
        }
    )

db = firestore.client()
bucket = storage.bucket()
