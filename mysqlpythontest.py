import mysql.connector

try:
    print("Connecting to the database...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="W00fW00f#!?",  # Replace with your MariaDB password
        database="walter"
    )
    
    if conn.is_connected():
        print("Connected to the database successfully.")

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contact_submissions LIMIT 1;")
    
    result = cursor.fetchone()
    if result:
        print("Query successful, data retrieved:", result)
    else:
        print("Query executed, but no data was found in the table.")

    cursor.close()
    conn.close()
    print("Database connection closed.")
except mysql.connector.Error as e:
    print(f"Database connection failed: {e}")
