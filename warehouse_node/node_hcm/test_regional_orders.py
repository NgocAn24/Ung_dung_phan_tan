import requests
import json
import uuid

def create_test_order(container_name, node_name, region):
    try:
        url = f'http://{container_name}:5000/order'
        order_data = {
            "order_id": str(uuid.uuid4()),
            "customer_name": f"Test Customer - {region}",
            "region": region
        }
        
        print(f"\nCreating {region} order on {node_name}")
        print(f"Order data: {json.dumps(order_data, indent=2)}")
        
        response = requests.post(url, json=order_data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"\nError with {node_name}:")
        print(str(e))

def get_node_orders(container_name, node_name):
    try:
        response = requests.get(f'http://{container_name}:5000/orders')
        print(f"\n{node_name} Orders:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"\nError getting orders from {node_name}:")
        print(str(e))

# Create orders for each region
regions = ['HCM', 'HN', 'DN']
nodes = [
    ('node-hcm', 'HCM Node'),
    ('node-hn', 'HN Node'),
    ('node-dn', 'DN Node')
]

# Create one order for each region on each node
for region in regions:
    for container_name, node_name in nodes:
        create_test_order(container_name, node_name, region)

print("\n=== Checking orders in each node ===")
for container_name, node_name in nodes:
    get_node_orders(container_name, node_name)
