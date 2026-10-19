from datetime import date 
from db import get_connection

def clean_order_id(order_id):
    """Keep only the digits, so '#1001.' becomes '1001'."""
    result = ""
    for ch in order_id:
        if ch.isdigit():
            result += ch
    return result

def get_order_status(order_id):
    """Find an order by its ID and return its details."""
    order_id = clean_order_id(order_id)

    conn = get_connection()
    order_info = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,),).fetchone()
    if not order_info:
        conn.close()
        return {"error": f"No order found with ID: '{order_id}'"}
    order_product = conn.execute("SELECT product_name FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
    conn.close()

    result = dict(order_info)
    result["items"] = [row["product_name"] for row in order_product]
    return result
    


def search_products(query):
    """Search products by name, description, or tags. Returns all matches."""
    query = query.strip()
    pattern = "%" + query + "%"

    conn = get_connection()
    rows = conn.execute("SELECT * FROM products WHERE name LIKE ? OR description LIKE ? OR  tags LIKE ?",
                        (pattern, pattern, pattern),
                        ).fetchall()
    conn.close()
    if not rows:
        return {"error": f"No products found for '{query}'"}
    return [dict(row) for row in rows]

    

def list_products():
    """Return all products with name, price, and stock status."""

    conn = get_connection()
    rows = conn.execute("SELECT name, price, stock FROM products").fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append({
            "name": row["name"],
            "price": row["price"],
            "in_stock": row["stock"] > 0,
        })
    return result


def request_return(order_id, reason):
    """Start a return if the order meets the return rules."""

    order_id = clean_order_id(order_id)
    conn = get_connection()

    try:
        order_info = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,),).fetchone()
        if not order_info:
            return {"error": f"No order found with ID: '{order_id}'"}

        if order_info["status"] == "Return requested":
            return {"error": f"A return is already open for order {order_id}"}
        
        if order_info["status"] != "Delivered":
            return {"error": f"Only delivered orders can be returned. This order is {order_info['status']}."}

        delivered = date.fromisoformat(order_info["delivered_on"])
        days_since = (date.today() - delivered).days
        if days_since > 30:
            return {"error": f"The 30-day return window has passed ({days_since} days since delivery)."}

        conn.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("Return requested", order_id),)
        conn.commit()

        return {
            "success": True,
            "return_id": f"R-{order_id}",
            "refund_amount": order_info["total"],
            "reason": reason,
        }

    finally:
        conn.close()



if __name__ == "__main__":
    
    print(search_products("shoes"))
    print(list_products())
    
