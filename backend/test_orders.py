"""
Test script to verify Order endpoints are working correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_order():
    """Test creating a new order"""
    print("\n=== Testing Order Creation ===")
    
    order_data = {
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_phone": "01712345678",
        "delivery_date": "2025-11-30",
        "notes": "Please deliver in the morning",
        "items": [
            {
                "product_type": "Milk",
                "quantity": 30,
                "unit": "10L",
                "notes": ""
            },
            {
                "product_type": "Eggs",
                "quantity": 20,
                "unit": "20pcs",
                "notes": ""
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/orders", json=order_data)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Order created successfully!")
        print(f"   Order ID: {result['data']['order_id']}")
        print(f"   Customer: {result['data']['customer_name']}")
        print(f"   Total: {result['data']['total_amount']}")
        return result['data']['order_id']
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_get_orders():
    """Test getting all orders"""
    print("\n=== Testing Get All Orders ===")
    
    try:
        response = requests.get(f"{BASE_URL}/orders")
        response.raise_for_status()
        result = response.json()
        print(f"✅ Retrieved {result['count']} orders")
        for order in result['data'][:3]:  # Show first 3
            print(f"   - {order['order_id']}: {order['customer_name']} ({order['status']})")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_get_order_details(order_id):
    """Test getting order details"""
    print(f"\n=== Testing Get Order Details ({order_id}) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/orders/{order_id}")
        response.raise_for_status()
        result = response.json()
        order = result['data']
        print(f"✅ Order details retrieved!")
        print(f"   Customer: {order['customer_name']}")
        print(f"   Status: {order['status']}")
        print(f"   Items: {len(order['items'])}")
        for item in order['items']:
            print(f"     - {item['product_type']}: {item['quantity']} {item['unit']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_update_order_status(order_id):
    """Test updating order status"""
    print(f"\n=== Testing Update Order Status ({order_id}) ===")
    
    try:
        response = requests.put(
            f"{BASE_URL}/orders/{order_id}/status",
            json={"status": "Packed"}
        )
        response.raise_for_status()
        print(f"✅ Order status updated to Packed")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_filter_orders():
    """Test filtering orders"""
    print("\n=== Testing Order Filters ===")
    
    # Test status filter
    try:
        response = requests.get(f"{BASE_URL}/orders", params={"status": "Pending"})
        response.raise_for_status()
        result = response.json()
        print(f"✅ Pending orders: {result['count']}")
        
        # Test search
        response = requests.get(f"{BASE_URL}/orders", params={"search": "John"})
        response.raise_for_status()
        result = response.json()
        print(f"✅ Search 'John': {result['count']} results")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Test order statistics"""
    print("\n=== Testing Order Statistics ===")
    
    try:
        response = requests.get(f"{BASE_URL}/orders/stats/summary")
        response.raise_for_status()
        result = response.json()
        stats = result['data']
        print(f"✅ Statistics retrieved!")
        print(f"   Total Orders: {stats.get('total_orders', 0)}")
        print(f"   Pending: {stats.get('pending_orders', 0)}")
        print(f"   Delivered: {stats.get('delivered_orders', 0)}")
        print(f"   Cancelled: {stats.get('cancelled_orders', 0)}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Order System Backend API Tests")
    print("=" * 60)
    
    # Run tests
    order_id = test_create_order()
    test_get_orders()
    
    if order_id:
        test_get_order_details(order_id)
        test_update_order_status(order_id)
    
    test_filter_orders()
    test_stats()
    
    print("\n" + "=" * 60)
    print("Tests Completed!")
    print("=" * 60)
