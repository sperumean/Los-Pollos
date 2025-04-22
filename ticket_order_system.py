import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime
import json

class PollosHermanosManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Los Pollos Hermanos Management System")
        self.root.geometry("1000x700")
        
        # Set up error logging and status bar
        self.setup_status_bar()
        
        try:
            # Database connection with UTF-8 charset
            self.connect_to_database()
            
            # Create notebook for tabs
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill="both", expand=True, padx=10, pady=(10, 30))  # Leave space for status bar
            
            # Create tabs
            self.orders_tab = ttk.Frame(self.notebook)
            self.tickets_tab = ttk.Frame(self.notebook)
            
            self.notebook.add(self.orders_tab, text="Orders")
            self.notebook.add(self.tickets_tab, text="Support Tickets")
            
            # Initialize UI components
            self.create_orders_tab()
            self.create_tickets_tab()
            
            # Refresh data
            self.refresh_order_list()
            self.refresh_ticket_list()
            
            # Update status
            self.update_status("System ready")
        except Exception as e:
            self.update_status(f"Error initializing system: {str(e)}", "error")
            messagebox.showerror("Initialization Error", f"Failed to initialize system: {str(e)}")
    
    def setup_status_bar(self):
        """Create a status bar at the bottom of the window"""
        self.status_bar = ttk.Label(
            self.root, 
            text="Initializing...", 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def update_status(self, message, status_type="info"):
        """Update the status bar with a message"""
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=message)
            
            # Set color based on message type
            if status_type == "error":
                self.status_bar.config(foreground="red")
            elif status_type == "success":
                self.status_bar.config(foreground="green")
            elif status_type == "warning":
                self.status_bar.config(foreground="orange")
            else:
                self.status_bar.config(foreground="black")
                
            # Force update the display
            self.root.update_idletasks()

    def connect_to_database(self):
        try:
            # Close any existing connection
            if hasattr(self, 'conn') and hasattr(self.conn, 'is_connected') and self.conn.is_connected():
                try:
                    self.cursor.close()
                    self.conn.close()
                    print("Closed existing database connection")
                except Exception as close_error:
                    print(f"Error closing existing connection: {close_error}")
            
            # Create new connection
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="W00fW00f#!?",
                database="walter",
                charset='utf8mb4',
                collation='utf8mb4_general_ci',
                use_pure=True,  # Use pure Python implementation for better error handling
                autocommit=True,  # Enable autocommit mode
                get_warnings=True,  # Get warnings from MySQL
                raise_on_warnings=False,  # Don't raise exceptions for warnings
                connection_timeout=10,  # 10 second timeout
                buffered=True  # Use buffered cursors by default
            )
            
            # Create cursor
            self.cursor = self.conn.cursor(buffered=True, dictionary=False)
            
            # Test connection with a simple query
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
            
            print("Connected to database successfully")
            if hasattr(self, 'update_status'):
                self.update_status("Connected to database", "success")
                
            return True
        except mysql.connector.Error as e:
            error_msg = f"Could not connect to database: {str(e)}"
            print(error_msg)
            
            if hasattr(self, 'update_status'):
                self.update_status(error_msg, "error")
                
            messagebox.showerror("Database Error", error_msg)
            
            # Don't exit, let the caller handle the error
            return False
            
    def ensure_connection(self):
        """Check if database connection is active and reconnect if necessary"""
        try:
            # First check if connection exists and is connected
            if not hasattr(self, 'conn'):
                print("No database connection exists. Creating new connection...")
                return self.connect_to_database()
                
            # Check if connection is still active with a simple query
            try:
                # Try a simple query to check connection
                self.cursor.execute("SELECT 1")
                self.cursor.fetchone()
                return True
            except (mysql.connector.Error, AttributeError) as query_error:
                print(f"Connection test failed: {query_error}")
                
                # Try to check connection status directly
                try:
                    if not self.conn.is_connected():
                        print("Database connection lost. Reconnecting...")
                        return self.connect_to_database()
                except Exception as conn_check_error:
                    print(f"Error checking connection status: {conn_check_error}")
                    
                # If we got here, we need to reconnect
                print("Attempting to reconnect to database...")
                return self.connect_to_database()
                
        except Exception as e:
            print(f"Error ensuring database connection: {e}")
            
            # Final attempt to reconnect
            try:
                print("Making final attempt to reconnect...")
                return self.connect_to_database()
            except Exception as final_error:
                print(f"Final reconnection attempt failed: {final_error}")
                
                if hasattr(self, 'update_status'):
                    self.update_status("Database connection lost", "error")
                    
                messagebox.showerror("Database Error", "Lost connection to database and failed to reconnect")
                return False


    def delete_order(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an order to delete")
            return
            
        order_id = self.orders_tree.item(selected_item[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Order #{order_id}?\nThis cannot be undone."):
            return
            
        try:
            # First ensure we have a good connection
            if not self.ensure_connection():
                return
                
            # Check and reset transaction state if needed
            try:
                if hasattr(self.conn, 'in_transaction') and self.conn.in_transaction:
                    self.update_status("Resolving existing transaction...", "warning")
                    if not self.reset_transaction_state():
                        raise Exception("Failed to reset transaction state")
            except Exception as reset_error:
                self.update_status(f"Error resetting transaction: {reset_error}", "error")
                messagebox.showerror("Transaction Error", "Could not prepare for deletion. Try restarting the application.")
                return
                
            # Begin new transaction
            self.conn.start_transaction()
            self.update_status(f"Deleting order #{order_id}...", "info")
            
            # Delete add-ons first
            self.cursor.execute("""
                DELETE oia FROM order_item_addons oia
                JOIN order_items oi ON oia.order_item_id = oi.order_item_id
                WHERE oi.order_id = %s
            """, (order_id,))
            
            # Delete order items
            self.cursor.execute("""
                DELETE FROM order_items WHERE order_id = %s
            """, (order_id,))
            
            # Delete order
            self.cursor.execute("""
                DELETE FROM orders WHERE order_id = %s
            """, (order_id,))
            
            # Commit transaction
            self.conn.commit()
            
            self.update_status(f"Order #{order_id} deleted successfully", "success")
            messagebox.showinfo("Success", f"Order #{order_id} has been deleted")
            self.refresh_order_list()
            
        except Exception as e:
            # Make sure we attempt to rollback
            try:
                if hasattr(self.conn, 'in_transaction') and self.conn.in_transaction:
                    self.conn.rollback()
                    self.update_status("Transaction rolled back", "warning")
            except Exception as rollback_error:
                self.update_status(f"Error rolling back: {rollback_error}", "error")
                
            error_msg = f"Failed to delete order: {str(e)}"
            self.update_status(error_msg, "error")
            messagebox.showerror("Error", error_msg)
            
            # Try to recover database connection if it was lost
            self.reset_transaction_state()


    
    def update_order_status(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an order to update")
            return
            
        order_id = self.orders_tree.item(selected_item[0])['values'][0]
        
        # Create update window
        update_window = tk.Toplevel(self.root)
        update_window.title(f"Update Order #{order_id} Status")
        update_window.geometry("300x150")
        
        ttk.Label(update_window, text="New Status:").pack(pady=(20, 5))
        
        status_combo = ttk.Combobox(update_window, values=["pending", "completed", "delivered", "cancelled"])
        status_combo.pack(pady=5, padx=20, fill="x")
    
        def save_status():
            new_status = status_combo.get()
            if not new_status:
                messagebox.showwarning("Warning", "Please select a status")
                return
                
            try:
                # Ensure connection
                if not self.ensure_connection():
                    messagebox.showerror("Error", "Database connection lost")
                    update_window.destroy()
                    return
                    
                self.cursor.execute("""
                    UPDATE orders SET status = %s WHERE order_id = %s
                """, (new_status, order_id))
                self.conn.commit()
                
                self.update_status(f"Order #{order_id} status updated to {new_status}", "success")
                messagebox.showinfo("Success", f"Order status updated to {new_status}")
                update_window.destroy()
                self.refresh_order_list()
            except Exception as e:
                self.update_status(f"Error updating status: {e}", "error")
                messagebox.showerror("Error", f"Failed to update status: {str(e)}")
        
        ttk.Button(update_window, text="Save", command=save_status).pack(pady=20)
    def create_orders_tab(self):
        # Split frame
        left_frame = ttk.Frame(self.orders_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(self.orders_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, expand=False)
        
        # Order List Tree
        self.orders_tree = ttk.Treeview(
            left_frame, 
            columns=("ID", "Customer", "Date", "Total", "Status"),
            show="headings"
        )
        
        # Define column headings
        self.orders_tree.heading("ID", text="Order ID")
        self.orders_tree.heading("Customer", text="Customer")
        self.orders_tree.heading("Date", text="Order Date")
        self.orders_tree.heading("Total", text="Total")
        self.orders_tree.heading("Status", text="Status")
        
        # Configure column widths
        self.orders_tree.column("ID", width=70)
        self.orders_tree.column("Customer", width=150)
        self.orders_tree.column("Date", width=150)
        self.orders_tree.column("Total", width=100)
        self.orders_tree.column("Status", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        ttk.Button(right_frame, text="View Order Details", command=self.view_order_details).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Update Status", command=self.update_order_status).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Delete Order", command=self.delete_order).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Refresh List", command=self.refresh_order_list).pack(pady=5, fill=tk.X)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(right_frame, text="Filter Orders")
        filter_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(filter_frame, text="Status:").pack(pady=5)
        self.status_filter = ttk.Combobox(filter_frame, values=["All", "pending", "completed", "delivered", "cancelled"])
        self.status_filter.current(0)
        self.status_filter.pack(pady=5, fill=tk.X)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_order_filter).pack(pady=5, fill=tk.X)
        
        # Bind double click
        self.orders_tree.bind("<Double-1>", lambda event: self.view_order_details())

    def create_tickets_tab(self):
        # Split frame
        left_frame = ttk.Frame(self.tickets_tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(self.tickets_tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5, expand=False)
        
        # Ticket List Tree
        self.tickets_tree = ttk.Treeview(
            left_frame, 
            columns=("ID", "Name", "Email", "Service", "Subject", "Date"),
            show="headings"
        )
        
        # Define column headings
        self.tickets_tree.heading("ID", text="ID")
        self.tickets_tree.heading("Name", text="Name")
        self.tickets_tree.heading("Email", text="Email")
        self.tickets_tree.heading("Service", text="Service")
        self.tickets_tree.heading("Subject", text="Subject")
        self.tickets_tree.heading("Date", text="Date")
        
        # Configure column widths
        self.tickets_tree.column("ID", width=50)
        self.tickets_tree.column("Name", width=120)
        self.tickets_tree.column("Email", width=150)
        self.tickets_tree.column("Service", width=100)
        self.tickets_tree.column("Subject", width=150)
        self.tickets_tree.column("Date", width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tickets_tree.yview)
        self.tickets_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.tickets_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        ttk.Button(right_frame, text="View Ticket Details", command=self.view_ticket_details).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="New Ticket", command=self.open_new_ticket_window).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Delete Selected", command=self.delete_selected_ticket).pack(pady=5, fill=tk.X)
        ttk.Button(right_frame, text="Refresh List", command=self.refresh_ticket_list).pack(pady=5, fill=tk.X)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(right_frame, text="Filter Tickets")
        filter_frame.pack(pady=10, fill=tk.X)
        
        ttk.Label(filter_frame, text="Service:").pack(pady=5)
        self.service_filter = ttk.Combobox(filter_frame, values=["All", "Customer Service", "Technical Support", "Billing"])
        self.service_filter.current(0)
        self.service_filter.pack(pady=5, fill=tk.X)
        
        ttk.Button(filter_frame, text="Apply Filter", command=self.apply_ticket_filter).pack(pady=5, fill=tk.X)

    def refresh_order_list(self):
        # Clear existing items
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        # Ensure database connection
        if not self.ensure_connection():
            return
            
        try:
            # Get filter value
            status_filter = self.status_filter.get()
            
            if status_filter == "All":
                # Fetch all orders with JOIN to customers
                self.cursor.execute("""
                    SELECT o.order_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                           o.order_date, o.total, o.status
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.customer_id
                    ORDER BY o.order_date DESC
                """)
            else:
                # Fetch filtered orders
                self.cursor.execute("""
                    SELECT o.order_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                           o.order_date, o.total, o.status
                    FROM orders o
                    LEFT JOIN customers c ON o.customer_id = c.customer_id
                    WHERE o.status = %s
                    ORDER BY o.order_date DESC
                """, (status_filter,))
            
            orders = self.cursor.fetchall()
            
            # Display orders
            for order in orders:
                order_id, customer_name, order_date, total, status = order
                
                # Handle NULL values
                if customer_name is None or customer_name.strip() == ' ':
                    customer_name = "Guest"
                
                # Format total with dollar sign
                total_display = f"${total:.2f}" if total is not None else "N/A"
                
                # Format date to be readable
                date_display = order_date.strftime("%Y-%m-%d %H:%M") if order_date is not None else "N/A"
                
                self.orders_tree.insert("", tk.END, values=(order_id, customer_name, date_display, total_display, status))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def refresh_ticket_list(self):
        # Clear existing items
        for item in self.tickets_tree.get_children():
            self.tickets_tree.delete(item)
            
        # Ensure database connection
        if not self.ensure_connection():
            return
        
        try:
            # Get filter value
            service_filter = self.service_filter.get()
            
            if service_filter == "All":
                # Fetch all tickets
                self.cursor.execute("""
                    SELECT * FROM contact_submissions 
                    ORDER BY submission_date DESC
                """)
            else:
                # Fetch filtered tickets
                self.cursor.execute("""
                    SELECT * FROM contact_submissions 
                    WHERE service = %s
                    ORDER BY submission_date DESC
                """, (service_filter,))
            
            tickets = self.cursor.fetchall()
            
            # Display tickets
            for ticket in tickets:
                submission_id = ticket[0]
                full_name = f"{ticket[1]} {ticket[2]}"
                email = ticket[3]
                service = ticket[4]
                subject = ticket[6] if ticket[6] is not None else "No subject"
                
                # Format date
                date_display = ticket[7].strftime("%Y-%m-%d %H:%M") if ticket[7] is not None else "N/A"
                
                self.tickets_tree.insert("", tk.END, values=(submission_id, full_name, email, service, subject, date_display))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tickets: {str(e)}")

    def view_order_details(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an order to view")
            return
            
        order_id = self.orders_tree.item(selected_item[0])['values'][0]
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Order #{order_id} Details")
        details_window.geometry("700x500")
        
        # Create a loading indicator
        loading_frame = ttk.Frame(details_window)
        loading_frame.pack(fill="both", expand=True)
        ttk.Label(loading_frame, text="Loading order details...", font=("", 12)).pack(pady=50)
        progress = ttk.Progressbar(loading_frame, mode="indeterminate")
        progress.pack(fill="x", padx=50, pady=10)
        progress.start()
        
        # Update the window to show the loading indicator
        details_window.update()
        
        # Ensure database connection
        if not self.ensure_connection():
            loading_frame.destroy()
            ttk.Label(details_window, text="Database connection error", foreground="red", font=("", 14, "bold")).pack(pady=50)
            ttk.Button(details_window, text="Close", command=details_window.destroy).pack()
            return
            
        try:
            self.update_status(f"Loading details for Order #{order_id}", "info")
            
            # Get order info - use explicit column selection instead of *
            self.cursor.execute("""
                SELECT o.order_id, o.order_date, o.subtotal, o.tax, o.total, o.status, 
                       CONCAT(IFNULL(c.first_name, ''), ' ', IFNULL(c.last_name, '')) AS customer_name,
                       c.email, c.address
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_id = %s
            """, (order_id,))
            
            order_info = self.cursor.fetchone()
            
            if not order_info:
                loading_frame.destroy()
                ttk.Label(details_window, text=f"Order #{order_id} not found", foreground="red", font=("", 14, "bold")).pack(pady=50)
                ttk.Button(details_window, text="Close", command=details_window.destroy).pack()
                self.update_status(f"Order #{order_id} not found", "warning")
                return
                
            # Get order items with product information
            self.cursor.execute("""
                SELECT oi.order_item_id, p.name, oi.quantity, oi.unit_price,
                       (oi.quantity * oi.unit_price) AS item_subtotal,
                       p.product_id
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            
            order_items = self.cursor.fetchall()
            
            # Remove the loading indicator
            loading_frame.destroy()
            
            # Create frames
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            info_frame = ttk.LabelFrame(main_frame, text="Order Information")
            info_frame.pack(fill="x", expand=False, padx=5, pady=5)
            
            items_frame = ttk.LabelFrame(main_frame, text="Order Items")
            items_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Extract order information with safe handling
            try:
                # Customer info
                customer_name = order_info[6] if order_info[6] is not None else "Guest Customer"
                customer_email = order_info[7] if order_info[7] is not None else "N/A"
                customer_address = order_info[8] if order_info[8] is not None else "N/A"
                
                # Order info with safe date handling
                order_date = None
                try:
                    if order_info[1] is not None:
                        if hasattr(order_info[1], 'strftime'):
                            order_date = order_info[1].strftime("%Y-%m-%d %H:%M")
                        else:
                            order_date = str(order_info[1])
                    else:
                        order_date = "N/A"
                except Exception as e:
                    print(f"Error formatting date: {e}")
                    order_date = "N/A"
                    
                status = order_info[5] if order_info[5] is not None else "N/A"
                
                # Handle numeric values with error protection
                try:
                    subtotal = float(order_info[2]) if order_info[2] is not None else 0
                except (ValueError, TypeError):
                    subtotal = 0
                    
                try:
                    tax = float(order_info[3]) if order_info[3] is not None else 0
                except (ValueError, TypeError):
                    tax = 0
                    
                try:
                    total = float(order_info[4]) if order_info[4] is not None else 0
                except (ValueError, TypeError):
                    total = 0
                
                # Display order info
                ttk.Label(info_frame, text=f"Order ID: {order_id}").grid(row=0, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Date: {order_date}").grid(row=0, column=1, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Status: {status}").grid(row=1, column=0, sticky="w", padx=5, pady=2)
                
                ttk.Label(info_frame, text=f"Customer: {customer_name}").grid(row=2, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Email: {customer_email}").grid(row=2, column=1, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Address: {customer_address}").grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
                
                # Format money values with error protection
                try:
                    subtotal_str = f"${float(subtotal):.2f}"
                except (ValueError, TypeError):
                    subtotal_str = "$0.00" if subtotal is None else f"${float(subtotal):.2f}"
                    
                try:
                    tax_str = f"${float(tax):.2f}"
                except (ValueError, TypeError):
                    tax_str = "$0.00" if tax is None else f"${float(tax):.2f}"
                    
                try:
                    total_str = f"${float(total):.2f}"
                except (ValueError, TypeError):
                    total_str = "$0.00" if total is None else f"${float(total):.2f}"
                
                ttk.Label(info_frame, text=f"Subtotal: {subtotal_str}").grid(row=4, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Tax: {tax_str}").grid(row=4, column=1, sticky="w", padx=5, pady=2)
                ttk.Label(info_frame, text=f"Total: {total_str}", font=("", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)
                
            except Exception as info_error:
                print(f"Error displaying order info: {info_error}")
                ttk.Label(info_frame, text=f"Error displaying order information: {str(info_error)}", 
                        foreground="red").grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
            
            # Create items treeview
            items_tree_frame = ttk.Frame(items_frame)
            items_tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            items_tree = ttk.Treeview(
                items_tree_frame,
                columns=("ID", "Product", "Quantity", "Unit Price", "Subtotal"),
                show="headings"
            )
            
            items_tree.heading("ID", text="Item ID")
            items_tree.heading("Product", text="Product")
            items_tree.heading("Quantity", text="Qty")
            items_tree.heading("Unit Price", text="Unit Price")
            items_tree.heading("Subtotal", text="Subtotal")
            
            items_tree.column("ID", width=50)
            items_tree.column("Product", width=200)
            items_tree.column("Quantity", width=50)
            items_tree.column("Unit Price", width=100)
            items_tree.column("Subtotal", width=100)
            
            # Add scrollbar
            items_scrollbar = ttk.Scrollbar(items_tree_frame, orient=tk.VERTICAL, command=items_tree.yview)
            items_tree.configure(yscrollcommand=items_scrollbar.set)
            
            # Pack
            items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert items
            for item in order_items:
                try:
                    item_id = item[0]
                    product_name = item[1] if item[1] is not None else f"Unknown Product (ID: {item[5]})"
                    quantity = item[2] if item[2] is not None else 0
                    
                    # Handle unit price formatting
                    try:
                        unit_price = float(item[3]) if item[3] is not None else 0
                        unit_price_str = f"${unit_price:.2f}"
                    except (ValueError, TypeError):
                        unit_price_str = f"${float(item[3]):.2f}" if item[3] is not None else "$0.00"
                    
                    # Handle subtotal formatting
                    try:
                        item_subtotal = float(item[4]) if item[4] is not None else 0
                        item_subtotal_str = f"${item_subtotal:.2f}"
                    except (ValueError, TypeError):
                        item_subtotal_str = f"${float(item[4]):.2f}" if item[4] is not None else "$0.00"
                    
                    items_tree.insert("", tk.END, values=(
                        item_id,
                        product_name,
                        quantity,
                        unit_price_str,
                        item_subtotal_str
                    ))
                except Exception as item_error:
                    print(f"Error displaying item: {item_error}")
                    # Add a placeholder row for the error
                    items_tree.insert("", tk.END, values=(
                        "Error",
                        f"Error displaying item: {str(item_error)}",
                        "", "", ""
                    ))
                
            # Addons section
            addons_frame = ttk.LabelFrame(main_frame, text="Item Add-ons")
            addons_frame.pack(fill="x", expand=False, padx=5, pady=5)
            
            # Get addons for items
            addon_info = {}
            for item in order_items:
                try:
                    item_id = item[0]
                    self.cursor.execute("""
                        SELECT oia.order_item_id, a.name, a.price
                        FROM order_item_addons oia
                        JOIN add_ons a ON oia.addon_id = a.addon_id
                        WHERE oia.order_item_id = %s
                    """, (item_id,))
                    
                    addons = self.cursor.fetchall()
                    if addons:
                        addon_info[item_id] = addons
                except Exception as addon_query_error:
                    print(f"Error querying add-ons for item {item_id}: {addon_query_error}")
            
            # If addons exist, display them
            if addon_info:
                addons_canvas = tk.Canvas(addons_frame, height=100)
                addons_canvas.pack(fill="x", expand=False, padx=5, pady=5)
                
                addons_scrollframe = ttk.Frame(addons_canvas)
                addons_scrollbar = ttk.Scrollbar(addons_frame, orient="vertical", command=addons_canvas.yview)
                addons_canvas.configure(yscrollcommand=addons_scrollbar.set)
                
                addons_scrollbar.pack(side="right", fill="y")
                addons_canvas.pack(side="left", fill="both", expand=True)
                addons_canvas.create_window((0, 0), window=addons_scrollframe, anchor="nw", tags="addons_scrollframe")
                
                row = 0
                for item_id, addons in addon_info.items():
                    try:
                        # Get item name
                        for item in order_items:
                            if item[0] == item_id:
                                item_name = item[1]
                                break
                        else:
                            item_name = f"Item #{item_id}"
                        
                        # Display addons
                        ttk.Label(addons_scrollframe, text=f"{item_name} Add-ons:", font=("", 9, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
                        row += 1
                        
                        for addon in addons:
                            addon_name = addon[1] if addon[1] is not None else "Unknown Add-on"
                            
                            # Safe addon price formatting
                            try:
                                addon_price = float(addon[2]) if addon[2] is not None else 0
                                addon_price_str = f"${addon_price:.2f}"
                            except (ValueError, TypeError):
                                addon_price_str = f"${float(addon[2]):.2f}" if addon[2] is not None else "$0.00"
                                
                            ttk.Label(addons_scrollframe, text=f"• {addon_name} ({addon_price_str})").grid(row=row, column=0, sticky="w", padx=20, pady=1)
                            row += 1
                    except Exception as addon_display_error:
                        print(f"Error displaying add-ons for item {item_id}: {addon_display_error}")
                        ttk.Label(addons_scrollframe, text=f"Error displaying add-ons: {str(addon_display_error)}", foreground="red").grid(row=row, column=0, sticky="w", padx=5, pady=2)
                        row += 1
                
                # Update the scrollregion when the frame changes size
                def update_scrollregion(event):
                    addons_canvas.configure(scrollregion=addons_canvas.bbox("all"))
                
                addons_scrollframe.bind("<Configure>", update_scrollregion)
            else:
                ttk.Label(addons_frame, text="No add-ons for this order").pack(padx=5, pady=5)
            
            # Buttons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", padx=5, pady=10)
            
            ttk.Button(buttons_frame, text="Close", command=details_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Status update combobox
            status_var = tk.StringVar(value=status)
            ttk.Label(buttons_frame, text="Update Status:").pack(side=tk.LEFT, padx=5)
            status_combo = ttk.Combobox(buttons_frame, textvariable=status_var, 
                                      values=["pending", "completed", "delivered", "cancelled"])
            status_combo.pack(side=tk.LEFT, padx=5)
            
            def update_status():
                new_status = status_var.get()
                if not new_status:
                    messagebox.showwarning("Warning", "Please select a status")
                    return
                    
                try:
                    if not self.ensure_connection():
                        messagebox.showerror("Error", "Database connection lost")
                        details_window.destroy()
                        return
                        
                    self.cursor.execute("""
                        UPDATE orders SET status = %s WHERE order_id = %s
                    """, (new_status, order_id))
                    self.conn.commit()
                    
                    self.update_status(f"Order #{order_id} status updated to {new_status}", "success")
                    messagebox.showinfo("Success", f"Order status updated to {new_status}")
                    self.refresh_order_list()
                    
                    # Update status label in the window too
                    for widget in info_frame.grid_slaves():
                        if int(widget.grid_info()["row"]) == 1 and int(widget.grid_info()["column"]) == 0:
                            widget.config(text=f"Status: {new_status}")
                            break
                            
                except Exception as e:
                    self.update_status(f"Error updating status: {e}", "error")
                    messagebox.showerror("Error", f"Failed to update status: {str(e)}")
            
            ttk.Button(buttons_frame, text="Update", command=update_status).pack(side=tk.LEFT, padx=5)
            
            # Update status
            self.update_status(f"Viewing Order #{order_id}", "info")
            
        except Exception as e:
            # Remove the loading indicator
            loading_frame.destroy()
            
            error_msg = f"Failed to load order details: {str(e)}"
            self.update_status(error_msg, "error")
            
            # Display error in the window
            error_frame = ttk.Frame(details_window)
            error_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ttk.Label(error_frame, text="Error Loading Order Details", 
                     font=("", 14, "bold"), foreground="red").pack(pady=(20, 10))
            ttk.Label(error_frame, text=error_msg, wraplength=500).pack(pady=10)
            ttk.Button(error_frame, text="Close", command=details_window.destroy).pack(pady=20)
            
            # Try to recover database connection
            self.reset_transaction_state()


    def apply_order_filter(self):
        self.refresh_order_list()
        
    def apply_ticket_filter(self):
        self.refresh_ticket_list()
            
    def open_new_ticket_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Support Ticket")
        new_window.geometry("400x500")

        # Form fields
        ttk.Label(new_window, text="First Name:").pack(pady=5)
        first_name_entry = ttk.Entry(new_window)
        first_name_entry.pack(pady=5, fill="x", padx=20)

        ttk.Label(new_window, text="Last Name:").pack(pady=5)
        last_name_entry = ttk.Entry(new_window)
        last_name_entry.pack(pady=5, fill="x", padx=20)

        ttk.Label(new_window, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(new_window)
        email_entry.pack(pady=5, fill="x", padx=20)

        ttk.Label(new_window, text="Service:").pack(pady=5)
        service_combo = ttk.Combobox(new_window, values=["Customer Service", "Technical Support", "Billing"])
        service_combo.pack(pady=5, fill="x", padx=20)

        ttk.Label(new_window, text="Country:").pack(pady=5)
        country_entry = ttk.Entry(new_window)
        country_entry.pack(pady=5, fill="x", padx=20)

        ttk.Label(new_window, text="Subject:").pack(pady=5)
        subject_entry = ttk.Entry(new_window)
        subject_entry.pack(pady=5, fill="x", padx=20)

        def submit_ticket():
            # Validate fields
            if not first_name_entry.get() or not last_name_entry.get() or not email_entry.get() or not service_combo.get():
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
                
            try:
                # Ensure connection
                if not self.ensure_connection():
                    messagebox.showerror("Error", "Database connection lost")
                    new_window.destroy()
                    return
                    
                query = """INSERT INTO contact_submissions 
                          (first_name, last_name, email, service, country, subject, submission_date) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                values = (
                    first_name_entry.get(),
                    last_name_entry.get(),
                    email_entry.get(),
                    service_combo.get(),
                    country_entry.get(),
                    subject_entry.get(),
                    datetime.now()
                )
                self.cursor.execute(query, values)
                self.conn.commit()
                
                self.update_status("Ticket created successfully", "success")
                messagebox.showinfo("Success", "Ticket created successfully!")
                new_window.destroy()
                self.refresh_ticket_list()
            except Exception as e:
                self.update_status(f"Error creating ticket: {e}", "error")
                messagebox.showerror("Error", f"Failed to create ticket: {str(e)}")

        ttk.Button(new_window, text="Submit", command=submit_ticket).pack(pady=20)
        
    def delete_selected_ticket(self):
        selected_item = self.tickets_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ticket to delete")
            return

        ticket_id = self.tickets_tree.item(selected_item[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Ticket #{ticket_id}?"):
            return
            
        try:
            # Ensure connection
            if not self.ensure_connection():
                return
                
            self.cursor.execute("DELETE FROM contact_submissions WHERE submission_id = %s", (ticket_id,))
            self.conn.commit()
            
            self.update_status(f"Ticket #{ticket_id} deleted successfully", "success")
            self.refresh_ticket_list()
            messagebox.showinfo("Success", f"Ticket #{ticket_id} deleted successfully!")
        except Exception as e:
            self.update_status(f"Error deleting ticket: {e}", "error")
            messagebox.showerror("Error", f"Failed to delete ticket: {str(e)}")

    def export_data(self):
        """Export orders and tickets to JSON files"""
        try:
            # Ensure connection
            if not self.ensure_connection():
                messagebox.showerror("Error", "Database connection lost")
                return
                
            self.update_status("Exporting data...", "info")
                
            # Export orders
            self.cursor.execute("""
                SELECT o.order_id, CONCAT(c.first_name, ' ', c.last_name) AS customer_name, 
                       o.order_date, o.subtotal, o.tax, o.total, o.status,
                       c.email, c.address
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                ORDER BY o.order_date DESC
            """)
            
            orders = []
            for row in self.cursor.fetchall():
                order_id, customer_name, order_date, subtotal, tax, total, status, email, address = row
                
                # Get order items
                self.cursor.execute("""
                    SELECT oi.order_item_id, p.name, oi.quantity, oi.unit_price,
                           (oi.quantity * oi.unit_price) AS item_subtotal,
                           p.product_id
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = %s
                """, (order_id,))
                
                items = []
                for item_row in self.cursor.fetchall():
                    item_id, product_name, quantity, unit_price, item_subtotal, product_id = item_row
                    
                    # Get addons
                    self.cursor.execute("""
                        SELECT a.addon_id, a.name, a.price
                        FROM order_item_addons oia
                        JOIN add_ons a ON oia.addon_id = a.addon_id
                        WHERE oia.order_item_id = %s
                    """, (item_id,))
                    
                    addons = []
                    for addon_row in self.cursor.fetchall():
                        addon_id, addon_name, addon_price = addon_row
                        addons.append({
                            "id": addon_id,
                            "name": addon_name,
                            "price": float(addon_price) if addon_price is not None else 0
                        })
                    
                    items.append({
                        "id": item_id,
                        "product_id": product_id,
                        "name": product_name,
                        "quantity": quantity,
                        "unit_price": float(unit_price) if unit_price is not None else 0,
                        "subtotal": float(item_subtotal) if item_subtotal is not None else 0,
                        "addons": addons
                    })
                
                orders.append({
                    "id": order_id,
                    "customer": customer_name,
                    "email": email,
                    "address": address,
                    "date": order_date.isoformat() if hasattr(order_date, 'isoformat') else str(order_date),
                    "subtotal": float(subtotal) if subtotal is not None else 0,
                    "tax": float(tax) if tax is not None else 0,
                    "total": float(total) if total is not None else 0,
                    "status": status,
                    "items": items
                })
            
            # Write orders to file
            with open("exported_orders.json", "w") as f:
                json.dump(orders, f, indent=2, default=str)
            
            # Export tickets
            self.cursor.execute("""
                SELECT * FROM contact_submissions ORDER BY submission_date DESC
            """)
            
            tickets = []
            for row in self.cursor.fetchall():
                submission_id, first_name, last_name, email, service, country, subject, submission_date = row
                
                tickets.append({
                    "id": submission_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "service": service,
                    "country": country,
                    "subject": subject,
                    "date": submission_date.isoformat() if hasattr(submission_date, 'isoformat') else str(submission_date)
                })
            
            # Write tickets to file
            with open("exported_tickets.json", "w") as f:
                json.dump(tickets, f, indent=2, default=str)
                
            self.update_status("Data exported successfully!", "success")
            messagebox.showinfo("Success", "Data exported to JSON files successfully")
            
        except Exception as e:
            self.update_status(f"Error exporting data: {e}", "error")
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def reset_transaction_state(self):
        """Attempt to reset the transaction state if there's an issue"""
        try:
            if hasattr(self, 'conn') and hasattr(self.conn, 'is_connected') and self.conn.is_connected():
                try:
                    # Try to roll back any pending transaction
                    if hasattr(self.conn, 'in_transaction') and self.conn.in_transaction:
                        self.conn.rollback()
                        print("Rolled back pending transaction")
                except Exception as rollback_error:
                    print(f"Error rolling back transaction: {rollback_error}")
                    
                try:
                    # Close and reopen the connection to reset completely
                    self.cursor.close()
                    self.conn.close()
                    print("Closed connection to reset state")
                    return self.connect_to_database()
                except Exception as close_error:
                    print(f"Error closing connection: {close_error}")
                    
            # If we got here, try a complete reconnect
            return self.connect_to_database()
        except Exception as e:
            print(f"Failed to reset transaction state: {e}")
            return False
            
    def __del__(self):
        if hasattr(self, 'conn') and hasattr(self.conn, 'is_connected'):
            try:
                if self.conn.is_connected():
                    self.cursor.close()
                    self.conn.close()
                    print("Database connection closed")
            except Exception as e:
                print(f"Error during cleanup: {e}")


def main():
    root = tk.Tk()
    app = PollosHermanosManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
