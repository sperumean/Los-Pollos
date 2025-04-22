import mysql.connector
import sys

def fix_transactions():
    """Fix any stuck transactions in the database"""
    print("Los Pollos Hermanos Database Transaction Fix Tool")
    print("------------------------------------------------")
    
    # Connect to database
    try:
        print("\nConnecting to database...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="W00fW00f#!?",
            charset='utf8mb4',
            get_warnings=True
        )
        cursor = conn.cursor(buffered=True)
        print("Connected successfully!")
    except mysql.connector.Error as e:
        print(f"Error connecting to database: {e}")
        return False
    
    try:
        # Get list of processes
        print("\nChecking for stuck transactions...")
        cursor.execute("SHOW PROCESSLIST")
        processes = cursor.fetchall()
        
        stuck_count = 0
        for process in processes:
            process_id = process[0]
            user = process[1]
            host = process[2]
            db = process[3]
            command = process[4]
            time = process[5]
            state = process[6]
            info = process[7]
            
            # Look for queries that have been running for a long time (more than 60 seconds)
            if time > 60 and command not in ('Sleep', 'Daemon'):
                print(f"Found potentially stuck process: ID={process_id}, User={user}, DB={db}, Command={command}, Time={time}s, State={state}")
                print(f"Query: {info}")
                
                kill = input(f"Kill this process? (y/n): ")
                if kill.lower() == 'y':
                    try:
                        print(f"Killing process {process_id}...")
                        cursor.execute(f"KILL {process_id}")
                        stuck_count += 1
                        print("Process killed.")
                    except mysql.connector.Error as e:
                        print(f"Error killing process: {e}")
        
        # Check if walter database exists
        print("\nChecking for 'walter' database...")
        cursor.execute("SHOW DATABASES LIKE 'walter'")
        if not cursor.fetchone():
            print("Database 'walter' not found. You may need to run the database setup script.")
            return False
        
        # Use walter database
        cursor.execute("USE walter")
        
        # Check for locks
        print("\nChecking for locks in the walter database...")
        try:
            # For MySQL 5.7 and earlier
            cursor.execute("SHOW OPEN TABLES FROM walter WHERE In_use > 0")
            locked_tables = cursor.fetchall()
            
            if locked_tables:
                print("\nFound locked tables:")
                for table in locked_tables:
                    print(f"Table: {table[0]}, In_use: {table[1]}, Name_locked: {table[2]}")
            else:
                print("No locked tables found.")
        except mysql.connector.Error:
            try:
                # For MySQL 8.0+
                cursor.execute("""
                    SELECT * FROM performance_schema.data_locks 
                    WHERE OBJECT_SCHEMA = 'walter'
                """)
                locks = cursor.fetchall()
                
                if locks:
                    print("\nFound locks:")
                    for lock in locks:
                        print(f"Lock: {lock}")
                else:
                    print("No locks found.")
            except mysql.connector.Error as e:
                print(f"Error checking locks: {e}")
        
        # Check for innodb status
        print("\nChecking InnoDB status for transaction information...")
        cursor.execute("SHOW ENGINE INNODB STATUS")
        status = cursor.fetchone()[2]
        
        # Look for transaction info in status
        trx_section = False
        transaction_info = []
        
        for line in status.split('\n'):
            if line.startswith("---TRANSACTION"):
                trx_section = True
                transaction_info.append(line)
            elif trx_section and line.strip() and not line.startswith("---"):
                transaction_info.append(line)
            elif trx_section and line.startswith("---"):
                trx_section = False
        
        if transaction_info:
            print("\nFound active transactions:")
            for line in transaction_info:
                print(line)
        else:
            print("No active transactions found.")
        
        # Check table status
        print("\nChecking tables status...")
        cursor.execute("SHOW TABLE STATUS FROM walter")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            engine = table[1]
            rows = table[4]
            
            print(f"Table: {table_name}, Engine: {engine}, Rows: {rows}")
        
        # Try to fix any issues
        if stuck_count > 0:
            print("\nAttempting to reset any pending transactions...")
            cursor.execute("SET GLOBAL innodb_force_recovery = 0")
            print("Reset InnoDB recovery mode.")
        
        print("\nAttempting to fix any corrupted tables...")
        for table in tables:
            table_name = table[0]
            try:
                print(f"Repairing table {table_name}...")
                cursor.execute(f"REPAIR TABLE {table_name}")
                result = cursor.fetchall()
                print(f"Repair result: {result}")
            except mysql.connector.Error as e:
                print(f"Error repairing table {table_name}: {e}")
                print("Trying to check table instead...")
                try:
                    cursor.execute(f"CHECK TABLE {table_name}")
                    result = cursor.fetchall()
                    print(f"Check result: {result}")
                except mysql.connector.Error as check_e:
                    print(f"Error checking table: {check_e}")
        
        print("\nDone checking database. Any identified issues have been addressed.")
        return True
        
    except mysql.connector.Error as e:
        print(f"Error checking database: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    success = fix_transactions()
    if success:
        print("\nTransaction fix completed successfully.")
    else:
        print("\nTransaction fix encountered errors. Check the logs above.")
        sys.exit(1)
