import firebase_admin
from firebase_admin import credentials, firestore, storage

# --------------------------
# Initialize Firebase SAFELY
# --------------------------

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(
        cred,
        {"storageBucket": "jerseyshopgh.appspot.com"}
    )

db = firestore.client()
bucket = storage.bucket()

# --------------------------
# Firebase functions
# --------------------------

def get_products():
    products = []
    for doc in db.collection("products").stream():
        data = doc.to_dict()
        data["id"] = doc.id
        products.append(data)
    return products

def add_product(product):
    db.collection("products").add(product)

def place_order(order):
    db.collection("orders").add(order)

def update_product_quantity(product_id, new_quantity):
    db.collection("products").document(product_id).update({
        "quantity": new_quantity
    })
