import requests
import random
import uuid
import time
import concurrent.futures
import argparse
import logging
from datetime import datetime
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample data for order generation
REGIONS = ['HCM', 'HN', 'DN']
CUSTOMER_NAMES = [
    'Nguyen Van A', 'Tran Thi B', 'Le Van C', 
    'Pham Thi D', 'Hoang Van E', 'Vo Thi F'
]

def get_auth_headers(username, password):
    """Generate authentication headers for Airflow API"""
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('utf-8')
    auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
    return {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def generate_order():
    """Generate a random order"""
    return {
        'order_id': str(uuid.uuid4()),
        'customer_name': random.choice(CUSTOMER_NAMES),
        'region': random.choice(REGIONS),
        'timestamp': datetime.utcnow().isoformat()
    }

def submit_order(airflow_endpoint, auth_headers):
    """Submit a single order to Airflow"""
    order = generate_order()
    try:
        # Prepare the DAG run configuration with order data directly in conf
        # This matches what the Airflow DAG expects
        dag_run_data = {
            'conf': {
                'order_id': order['order_id'],
                'customer_name': order['customer_name'],
                'region': order['region'],
                'timestamp': order['timestamp']
            }
        }
        
        response = requests.post(
            f"{airflow_endpoint}/api/v1/dags/order_workflow/dagRuns",
            json=dag_run_data,
            headers=auth_headers,
            timeout=30
        )
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Successfully submitted order {order['order_id']} for {order['customer_name']} in {order['region']}")
            return True
        else:
            logger.error(f"Failed to submit order {order['order_id']}: HTTP {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout submitting order {order['order_id']}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error submitting order {order['order_id']}")
        return False
    except requests.RequestException as e:
        logger.error(f"Failed to submit order {order['order_id']}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error submitting order {order['order_id']}: {e}")
        return False

def test_airflow_connection(airflow_endpoint, auth_headers):
    """Test connection to Airflow"""
    try:
        response = requests.get(
            f"{airflow_endpoint}/api/v1/health",
            headers=auth_headers,
            timeout=10
        )
        if response.status_code == 200:
            logger.info("Successfully connected to Airflow")
            return True
        else:
            logger.error(f"Airflow health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Airflow: {e}")
        return False

def run_stress_test(num_orders, concurrency, airflow_endpoint, username, password):
    """Run stress test with concurrent order submissions"""
    logger.info(f"Starting stress test with {num_orders} orders and concurrency level {concurrency}")
    
    auth_headers = get_auth_headers(username, password)
    
    # Test Airflow connection first
    if not test_airflow_connection(airflow_endpoint, auth_headers):
        logger.error("Cannot connect to Airflow. Aborting stress test.")
        return
    
    start_time = time.time()
    successful_orders = 0
    failed_orders = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [
            executor.submit(submit_order, airflow_endpoint, auth_headers)
            for _ in range(num_orders)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    successful_orders += 1
                else:
                    failed_orders += 1
            except Exception as e:
                logger.error(f"Future execution error: {e}")
                failed_orders += 1

    end_time = time.time()
    duration = end_time - start_time
    
    # Print summary
    logger.info("\n=== Stress Test Results ===")
    logger.info(f"Total Orders: {num_orders}")
    logger.info(f"Successful Orders: {successful_orders}")
    logger.info(f"Failed Orders: {failed_orders}")
    logger.info(f"Success Rate: {(successful_orders/num_orders)*100:.2f}%")
    logger.info(f"Total Duration: {duration:.2f} seconds")
    if duration > 0:
        logger.info(f"Average Rate: {num_orders/duration:.2f} orders/second")
        logger.info(f"Successful Rate: {successful_orders/duration:.2f} successful orders/second")
    logger.info("============================")

def main():
    parser = argparse.ArgumentParser(description='Order Management System Stress Test')
    parser.add_argument('--orders', type=int, default=100,
                      help='Number of orders to generate (default: 100)')
    parser.add_argument('--concurrency', type=int, default=5,
                      help='Number of concurrent submissions (default: 5)')
    parser.add_argument('--endpoint', type=str, 
                      default='http://localhost:8080',
                      help='Airflow API endpoint (default: http://localhost:8080)')
    parser.add_argument('--username', type=str,
                      default='airflow',
                      help='Airflow API username (default: airflow)')
    parser.add_argument('--password', type=str,
                      default='airflow',
                      help='Airflow API password (default: airflow)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.orders <= 0:
        logger.error("Number of orders must be positive")
        return
    
    if args.concurrency <= 0:
        logger.error("Concurrency level must be positive")
        return
    
    try:
        run_stress_test(args.orders, args.concurrency, args.endpoint, args.username, args.password)
    except KeyboardInterrupt:
        logger.info("\nStress test interrupted by user")
    except Exception as e:
        logger.error(f"Stress test failed: {e}")

if __name__ == '__main__':
    main()
