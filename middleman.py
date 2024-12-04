import mysql.connector
import json
from decimal import Decimal
import re
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Connect to the MySQL database
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="W00fW00f#!?",
    database="WALTER",
    charset="utf8mb4",
    collation="utf8mb4_general_ci"
)

cursor = db_connection.cursor(dictionary=True)

# Query to fetch all goods
cursor.execute("SELECT * FROM Goods")



goods = cursor.fetchall()

# Query to fetch all suppliers
cursor.execute("SELECT * FROM Suppliers")
suppliers = cursor.fetchall()

# Function to convert Decimal to float
def convert_decimal(data):
    if isinstance(data, list):
        return [convert_decimal(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_decimal(value) for key, value in data.items()}
    elif isinstance(data, Decimal):
        return float(data)
    else:
        return data

# Convert Decimal values to float
goods = convert_decimal(goods)
suppliers = convert_decimal(suppliers)

# Combine data into a single dictionary
data = {
    "goods": goods,
    "suppliers": suppliers
}

# Convert data to a JSON string
json_data = json.dumps(data, indent=2)

# Path to fetchGoods.js
fetchgoods_path = os.path.join(current_dir, 'fetchGoods.js')

# Read the current content of fetchGoods.js
with open(fetchgoods_path, 'r') as js_file:
    js_content = js_file.read()

# Create the new content for the data variable
new_data_content = f"const data = {json_data};"

# Replace the existing data variable in the JavaScript file
updated_js_content = re.sub(
    r'const data = \{[\s\S]*?\};',
    new_data_content,
    js_content,
    flags=re.DOTALL
)

# Write the updated content back to fetchGoods.js
with open(fetchgoods_path, 'w') as js_file:
    js_file.write(updated_js_content)

# Close the database connection
cursor.close()
db_connection.close()

print(f"fetchGoods.js has been updated with the latest data at: {fetchgoods_path}")
