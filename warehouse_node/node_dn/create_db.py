import sqlite3
import os
from datetime import datetime

# Ensure instance directory exists
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_dir, exist_ok=True)

# Database file path
db_path = os.path.join(instance_dir, 'orders_dn.db')

# Remove existing database if it exists
if os.path.exists(db_path):
    os.remove(db_path)

# Create new database and table
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the order table
cursor.execute('''
CREATE TABLE "order" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(50) NOT NULL UNIQUE,
    customer_name VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print(f"Database created successfully at {db_path}")
