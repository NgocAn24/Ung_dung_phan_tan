# Hệ Thống Quản Lý Đơn Hàng Phân Tán

Một hệ thống quản lý đơn hàng phân tán được xây dựng bằng **Apache Airflow** để điều phối luồng công việc và **Flask** cho các API node kho. Hệ thống minh họa các khái niệm tính toán phân tán bao gồm khả năng chịu lỗi, chia vùng dữ liệu (sharding) và cân bằng tải.

## Kiến Trúc Hệ Thống

```
                            [ Khách hàng ]
                                 |
                                 v
                     [ Cổng API / Giao diện người dùng ]
                                 |
                                 v
                    +-----------------------------+
                    |  Apache Airflow Scheduler   |
                    +-----------------------------+
                                 |
              +-----------------+-----------------+
              |                 |                 |
     [Node Kho HCM]     [Node Kho Hà Nội]    [Node Kho Đà Nẵng]
         Flask API          Flask API            Flask API
            |                  |                     |
      SQLite/Postgres     SQLite/Postgres       SQLite/Postgres
```

## Tính Năng

- **Xử lý phân tán**: Đơn hàng được phân phối đến nhiều node kho khác nhau
- **Khả năng chịu lỗi**: Hệ thống vẫn hoạt động khi một node bị lỗi
- **Chia vùng theo khu vực**: Đơn hàng được gán cho kho dựa trên khu vực
- **Cân bằng tải**: Đơn hàng có thể được chuyển đến các node ít bận hơn
- **Giám sát sức khỏe**: Mỗi node cung cấp các chỉ số sức khỏe
- **Kiểm thử tải**: Có công cụ kiểm thử hiệu năng với tải cao

## Thành Phần

1. **Airflow DAG**
   - Điều phối luồng xử lý đơn hàng
   - Phân công node xử lý và xử lý khi có lỗi
   - Theo dõi trạng thái xử lý đơn hàng

2. **Node Kho**
   - API Flask để xử lý đơn hàng
   - CSDL SQLite hoặc Postgres để lưu trữ đơn hàng
   - Endpoint kiểm tra sức khỏe
   - Xử lý đơn hàng theo khu vực

3. **Kiểm thử tải (Stress Test)**
   - Mô phỏng gửi nhiều đơn hàng cùng lúc
   - Xử lý song song yêu cầu
   - Thu thập chỉ số hiệu năng

## Hướng Dẫn Cài Đặt

### Yêu Cầu

- Docker và Docker Compose
- Python 3.9 trở lên
- Các container có thể giao tiếp qua mạng

### Cài Đặt

1. **Clone repository**
   ```bash
   git clone <địa-chỉ-repo>
   cd distributed_order_system
   ```

2. **Khởi động Airflow**
   ```bash
   cd airflow
   docker-compose up -d
   ```
   Truy cập giao diện Airflow tại: http://localhost:8080 (Tài khoản mặc định: `airflow/airflow`)

3. **Khởi động các Node Kho**
   ```bash
   cd ../warehouse_node
   docker-compose up -d
   ```
   Ba node sẽ được khởi động:
   - Node HCM: http://localhost:5001
   - Node HN: http://localhost:5002
   - Node Đà Nẵng: http://localhost:5003

4. **Chạy kiểm thử tải**
   ```bash
   cd ../stress_test
   python simulate_orders.py --orders 1000 --concurrency 10
   ```

## API Node Kho

### 1. Kiểm tra sức khỏe
```
GET /health
```

### 2. Tạo đơn hàng
```
POST /order
{
  "order_id": "uuid",
  "customer_name": "tên khách hàng",
  "region": "khu vực"
}
```

### 3. Danh sách đơn hàng
```
GET /orders
```

### 4. Chi tiết đơn hàng
```
GET /order/<order_id>
```

## Giám Sát

1. **Bảng điều khiển Airflow**
   - Theo dõi DAG đang chạy
   - Xem kết quả thành công/thất bại
   - Xem log toàn hệ thống

2. **Sức khỏe các node**
   - Mỗi node có endpoint `/health`
   - Theo dõi tải xử lý đơn hàng
   - Kiểm tra trạng thái hoạt động

## Xử Lý Lỗi

- Đơn hàng lỗi sẽ được tự động thử lại
- Nếu một node bị lỗi, đơn hàng sẽ được chuyển sang node còn hoạt động
- Tất cả lỗi đều được ghi log để debug

## Kiểm Thử Hiệu Năng

Sử dụng script stress test với các tùy chọn khác nhau:

```bash
python simulate_orders.py --orders 1000 --concurrency 10 --endpoint http://localhost:8080
```


