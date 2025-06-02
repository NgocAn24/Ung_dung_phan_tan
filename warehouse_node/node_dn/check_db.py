import sqlite3
import os

# Database file path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'orders_dn.db')

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table info
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='order';")
table_info = cursor.fetchone()

print("Table Schema:")
print(table_info[0] if table_info else "Table not found")

# Close connection
conn.close()
