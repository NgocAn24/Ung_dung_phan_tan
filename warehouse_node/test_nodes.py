import requests
import json

def test_node_health(node_name):
    try:
        # Use Docker service names and internal port
        url = f'http://{node_name}:5000/health'
        print(f"\nTrying {url}")
        response = requests.get(url, timeout=5)
        print(f"{node_name} Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"\n{node_name} Error:")
        print(str(e))

# Test all nodes
print("Testing warehouse nodes health...")
test_node_health("node-hcm")
test_node_health("node-hn")
test_node_health("node-dn")
