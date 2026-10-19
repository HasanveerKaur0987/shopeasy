PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;



CREATE TABLE products(
    id          TEXT NOT NULL PRIMARY KEY,
    name        TEXT NOT NULL, 
    price       REAL NOT NULL,
    stock       INTEGER NOT NULL,
    description TEXT,
    tags        TEXT
);


CREATE TABLE orders(
    order_id            TEXT NOT NULL PRIMARY KEY,
    customer            TEXT NOT NULL,
    total               REAL NOT NULL,
    status              TEXT NOT NULL,
    order_date          TEXT NOT NULL,
    delivered_on        TEXT,
    expected_delivery   TEXT
);


CREATE TABLE order_items(
    order_id            TEXT NOT NULL,
    product_name        TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT,
    email TEXT NOT NULL,
    category TEXT NOT NULL,
    issue TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Open',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);