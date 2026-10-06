from data import PRODUCTS, ORDERS
from datetime import date 


def get_order_status(order_id):
    """Find an order by its ID and return its details."""

    for order in ORDERS:
        if order["order_id"] == order_id:
            return order
    return {"error": f"No order found with ID {order_id}"}


def search_products(query):
    query = query.strip().lower()
    results =[]

    for product in PRODUCTS:
        tags = " ".join(product["tags"]).lower()     # ["bag","school"] -> "bag school"
        if (query in product["name"].lower()
                or query in product["description"].lower()
                or query in tags):
            results.append(product)

    if not results:                        # empty list means no matches
        return {"error": f"No products found for '{query}'"}
    return results


def list_products():
    result = []
    for product in PRODUCTS:
        result.append({
            "name": product["name"],
            "price": product["price"],
            "in_stock": product["stock"] > 0,
        })
    return result



def request_return(order_id, reason):
    """Start a return if the order meets the return rules."""
    for order in ORDERS:
        if order["order_id"] == order_id:
            if order["status"] == "Return requested":
                return {"error": f"A return is already open for order {order_id}"}

            if order["status"] != "Delivered":
                return {"error": f"Only delivered orders can be returned. This order is {order['status']}."}

            delivered = date.fromisoformat(order["delivered_on"])
            days_since = (date.today() - delivered).days
            if days_since > 30:
                return {"error": f"The 30-day return window has passed ({days_since} days since delivery)."}

            order["status"] = "Return requested"
            return {
                "success": True,
                "return_id": f"R-{order_id}",
                "refund_amount": order["total"],
                "reason": reason,
            }

    return {"error": f"No order found with ID {order_id}"}
        
        


if __name__ == "__main__":
    print(request_return("1001", "too small"))   # success
    print(request_return("1001", "too small"))   # already open
    print(request_return("1002", "changed mind")) # not delivered (Shipped)
    print(request_return("1006", "broken"))      # too old (add 1006 to data.py first)
    print(request_return("9999", "test"))        # not found
