import requests
import json
import uuid

def create_test_order(container_name, node_name):
    try:
        url = f'http://{container_name}:5000/order'
        order_data = {
            "order_id": str(uuid.uuid4()),
            "customer_name": "Test Customer",
            "region": "HCM"
        }
        
        print(f"\nCreating order on {node_name}")
        print(f"Order data: {json.dumps(order_data, indent=2)}")
        
        response = requests.post(url, json=order_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
        
        # Get all orders
        orders_response = requests.get(f'http://{container_name}:5000/orders')
        print(f"\nAll orders: {json.dumps(orders_response.json(), indent=2)}")
        
    except Exception as e:
        print(f"\nError with {node_name}:")
        print(str(e))

# Create test order on HCM node
create_test_order('node-hcm', "HCM Node")
