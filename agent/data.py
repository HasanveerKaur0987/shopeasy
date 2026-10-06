# Fake store data for ShopEasy.
# In Week 2 this moves into a SQLite database.

PRODUCTS = [
    {"id": "P1", "name": "Blue Hoodie", "price": 45.00, "stock": 12,
     "description": "Soft cotton hoodie, sizes S to XL.",
     "tags": ["clothing", "sweater", "sweatshirt", "top"]},
    {"id": "P2", "name": "Black Sneakers", "price": 80.00, "stock": 0,
     "description": "Light running shoes, sizes 7 to 12.",
     "tags": ["shoes", "footwear", "running", "trainers"]},
    {"id": "P3", "name": "Water Bottle", "price": 15.00, "stock": 40,
     "description": "1 litre steel bottle, keeps drinks cold for 24 hours.",
     "tags": ["drinks", "flask", "gym", "hydration"]},
    {"id": "P4", "name": "Backpack", "price": 60.00, "stock": 5,
     "description": "25 litre backpack with a laptop pocket.",
     "tags": ["bag", "school", "travel", "laptop bag"]},
    {"id": "P5", "name": "Wireless Earbuds", "price": 99.00, "stock": 8,
     "description": "Bluetooth earbuds with 20 hours of battery.",
     "tags": ["headphones", "audio", "music", "bluetooth"]},
]

ORDERS = [
    {"order_id": "1001", "customer": "Aisha", "items": ["Blue Hoodie"],
     "total": 45.00, "status": "Delivered", "date": "2026-09-28",
     "delivered_on": "2026-10-02"},
    {"order_id": "1002", "customer": "Ben", "items": ["Backpack", "Water Bottle"],
     "total": 75.00, "status": "Shipped", "date": "2026-10-03",
     "expected_delivery": "2026-10-08"},
    {"order_id": "1003", "customer": "Carlos", "items": ["Wireless Earbuds"],
     "total": 99.00, "status": "Processing", "date": "2026-10-05",
     "expected_delivery": "2026-10-11"},
    {"order_id": "1004", "customer": "Dana", "items": ["Black Sneakers"],
     "total": 80.00, "status": "Cancelled", "date": "2026-09-30"},
    {"order_id": "1005", "customer": "Eli", "items": ["Water Bottle"],
     "total": 15.00, "status": "Shipped", "date": "2026-10-04",
     "expected_delivery": "2026-10-09"},
    {"order_id": "1006", "customer": "Farah", "items": ["Backpack"],
     "total": 60.00, "status": "Delivered", "date": "2026-08-10",
     "delivered_on": "2026-08-15"},
]