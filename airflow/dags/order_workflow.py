from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import requests
import logging
import random
import uuid

# Cấu hình Logger
logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)

# Các endpoint của kho hàng
WAREHOUSE_NODES = {
    'HCM': 'http://node-hcm:5000',
    'HN': 'http://node-hn:5000',
    'DN': 'http://node-dn:5000'
}

Default_Args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

def Ingest_Order(**context):
    """
    Lấy order từ conf khi trigger DAG.
    Nếu chạy local test, sẽ tạo order mẫu.
    """
    Dag_Run = context.get('dag_run')
    
    # Lấy dữ liệu order từ cấu hình khi trigger DAG
    if Dag_Run and Dag_Run.conf:
        Order = Dag_Run.conf
        Logger.info(f"Đã nhận order từ DAG run conf: {Order}")
    else:
        # Dữ liệu test khi chạy local không có conf
        Order = {
            "order_id": f"test_{uuid.uuid4().hex[:8]}",  # Generate unique order_id
            "customer_name": "Test Customer",
            "region": "HCM",
            "timestamp": datetime.now().isoformat()
        }
        Logger.info("Không có dữ liệu order đầu vào, dùng order test với ID mới")

    # Kiểm tra các trường bắt buộc
    Required_Fields = ['order_id', 'customer_name', 'region']
    Missing_Fields = [field for field in Required_Fields if field not in Order]
    
    if Missing_Fields:
        Error_Msg = f"Thiếu các trường bắt buộc: {Missing_Fields}"
        Logger.error(Error_Msg)
        raise ValueError(Error_Msg)

    Logger.info(f"Order đã nhập: {Order}")
    return Order

def Assign_Warehouse(**context):
    """
    Chọn kho phù hợp dựa trên region của order.
    Nếu kho đó không reachable, chọn ngẫu nhiên kho còn lại.
    """
    Ti = context['task_instance']
    Order = Ti.xcom_pull(task_ids='ingest_order')
    Region = Order.get('region', 'HCM')

    try:
        Health_Url = f"{WAREHOUSE_NODES[Region]}/health"
        Response = requests.get(Health_Url, timeout=3)
        if Response.status_code == 200:
            Logger.info(f"Đã gán kho: {Region}")
            return Region
        else:
            Logger.warning(f"Kiểm tra sức khỏe kho {Region} thất bại với mã {Response.status_code}")
    except requests.RequestException as E:
        Logger.error(f"Lỗi khi kiểm tra kho {Region}: {E}")

    # Fallback chọn kho ngẫu nhiên khác
    Alternatives = list(set(WAREHOUSE_NODES.keys()) - {Region})
    Chosen = random.choice(Alternatives)
    Logger.info(f"Fallback gán kho: {Chosen}")
    return Chosen

def Process_Order(**context):
    """
    Gửi order đến kho đã chọn.
    """
    Ti = context['task_instance']
    Order = Ti.xcom_pull(task_ids='ingest_order')
    Warehouse = Ti.xcom_pull(task_ids='assign_warehouse')
    Order_Url = f"{WAREHOUSE_NODES[Warehouse]}/order"

    try:
        Response = requests.post(Order_Url, json=Order, timeout=5)
        if Response.status_code == 500:
            Error_Details = Response.json().get('details', 'Unknown error')
            if 'UNIQUE constraint' in str(Error_Details):
                Logger.error(f"Order ID {Order['order_id']} đã tồn tại trong {Warehouse}")
                raise ValueError(f"Duplicate order ID: {Order['order_id']}")
        Response.raise_for_status()
        Logger.info(f"Đã gửi order thành công tới {Warehouse}: {Response.json()}")
        return Response.json()
    except requests.RequestException as E:
        Logger.error(f"Gửi order đến {Warehouse} thất bại: {E}")
        raise

# Định nghĩa DAG
with DAG(
    dag_id='order_workflow',
    default_args=Default_Args,
    description='Luồng xử lý đơn hàng phân tán',
    schedule_interval=None,  # Chạy khi trigger
    catchup=False,
    tags=['warehouse', 'order']
) as Dag:
    
    Ingest_Task = PythonOperator(
        task_id='ingest_order',
        python_callable=Ingest_Order
    )

    Assign_Task = PythonOperator(
        task_id='assign_warehouse',
        python_callable=Assign_Warehouse
    )

    Process_Task = PythonOperator(
        task_id='process_order',
        python_callable=Process_Order
    )

    Ingest_Task >> Assign_Task >> Process_Task
