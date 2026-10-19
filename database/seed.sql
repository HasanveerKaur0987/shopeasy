PRAGMA foreign_keys = ON;

-- Products
INSERT INTO products (id, name, price, stock, description, tags) VALUES
    ('P1', 'Blue Hoodie',      45.00, 12, 'Soft cotton hoodie, sizes S to XL.',                    'clothing,sweater,sweatshirt,top'),
    ('P2', 'Black Sneakers',   80.00,  0, 'Light running shoes, sizes 7 to 12.',                   'shoes,footwear,running,trainers'),
    ('P3', 'Water Bottle',     15.00, 40, '1 litre steel bottle, keeps drinks cold for 24 hours.', 'drinks,flask,gym,hydration'),
    ('P4', 'Backpack',         60.00,  5, '25 litre backpack with a laptop pocket.',               'bag,school,travel,laptop bag'),
    ('P5', 'Wireless Earbuds', 99.00,  8, 'Bluetooth earbuds with 20 hours of battery.',           'headphones,audio,music,bluetooth');

-- Orders
INSERT INTO orders (order_id, customer, total, status, order_date, delivered_on, expected_delivery) VALUES
    ('1001', 'Aisha',  45.00, 'Delivered',  date('now', '-15 days'), date('now', '-11 days'), NULL),
    ('1002', 'Ben',    75.00, 'Shipped',    date('now', '-4 days'),  NULL,                    date('now', '+3 days')),
    ('1003', 'Carlos', 99.00, 'Processing', date('now', '-1 days'),  NULL,                    date('now', '+6 days')),
    ('1004', 'Dana',   80.00, 'Cancelled',  date('now', '-10 days'), NULL,                    NULL),
    ('1005', 'Eli',    15.00, 'Shipped',    date('now', '-3 days'),  NULL,                    date('now', '+2 days')),
    ('1006', 'Farah',  60.00, 'Delivered',  date('now', '-65 days'), date('now', '-60 days'), NULL);

-- Order items (one row per item; order 1002 has two)
INSERT INTO order_items (order_id, product_name) VALUES
    ('1001', 'Blue Hoodie'),
    ('1002', 'Backpack'),
    ('1002', 'Water Bottle'),
    ('1003', 'Wireless Earbuds'),
    ('1004', 'Black Sneakers'),
    ('1005', 'Water Bottle'),
    ('1006', 'Backpack');