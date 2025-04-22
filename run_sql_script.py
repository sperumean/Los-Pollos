import mysql.connector
import os

def run_sql_script(sql_file_path, db_config):
    """
    Run an SQL script file against the specified database
    
    Args:
        sql_file_path (str): Path to the SQL file
        db_config (dict): Database connection configuration
    """
    try:
        print(f"Opening SQL file: {sql_file_path}")
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()
            
        print("Connecting to database...")
        # First try to connect without specifying the database
        # (in case we need to create it)
        initial_config = db_config.copy()
        if 'database' in initial_config:
            del initial_config['database']
            
        conn = mysql.connector.connect(**initial_config)
        cursor = conn.cursor()
        
        print("Executing SQL script...")
        # Split script into individual statements
        statements = sql_script.split(';')
        
        for statement in statements:
            if statement.strip():
                try:
                    cursor.execute(statement + ';')
                    # After creating the database, try to use it
                    if "CREATE DATABASE" in statement and db_config.get('database'):
                        cursor.execute(f"USE {db_config['database']};")
                except mysql.connector.Error as err:
                    print(f"Warning: {err}")
        
        conn.commit()
        print("SQL script executed successfully!")
        cursor.close()
        conn.close()
        
    except FileNotFoundError:
        print(f"Error: SQL file not found: {sql_file_path}")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'W00fW00f#!?',
        'database': 'walter',
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    # Path to the SQL script
    sql_file_path = "database_setup.sql"
    
    # Check if file exists
    if not os.path.exists(sql_file_path):
        print(f"Error: SQL file not found: {sql_file_path}")
        file_name = input("Enter the SQL script filename: ")
        sql_file_path = file_name
    
    # Run the script
    run_sql_script(sql_file_path, db_config)
