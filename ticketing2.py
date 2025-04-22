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
        
        # Database connection with UTF-8 charset
        self.connect_to_database()
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        
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

    def connect_to_database(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="W00fW00f#!?",
                database="walter",
                charset='utf8mb4',
                collation='utf8mb4_general_ci'
            )
            self.cursor = self.conn.cursor()
            print("Connected to database successfully")
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Could not connect to database: {str(e)}")
            exit(1)

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
        
        try:
            # Get order info
            self.cursor.execute("""
                SELECT o.*, CONCAT(c.first_name, ' ', c.last_name) AS customer_name,
                       c.email, c.address
                FROM orders o
                LEFT JOIN customers c ON o.customer_id = c.customer_id
                WHERE o.order_id = %s
            """, (order_id,))
            
            order_info = self.cursor.fetchone()
            
            if not order_info:
                messagebox.showerror("Error", "Order information not found")
                details_window.destroy()
                return
            
            # Get order items
            self.cursor.execute("""
                SELECT oi.order_item_id, p.name, oi.quantity, oi.unit_price,
                       (oi.quantity * oi.unit_price) AS item_subtotal
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (order_id,))
            
            order_items = self.cursor.fetchall()
            
            # Create frames
            info_frame = ttk.LabelFrame(details_window, text="Order Information")
            info_frame.pack(fill="x", expand=False, padx=10, pady=10)
            
            items_frame = ttk.LabelFrame(details_window, text="Order Items")
            items_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Order info
            order_date = order_info[1].strftime("%Y-%m-%d %H:%M") if order_info[1] is not None else "N/A"
            status = order_info[5] if order_info[5] is not None else "N/A"
            subtotal = order_info[2] if order_info[2] is not None else 0
            tax = order_info[3] if order_info[3] is not None else 0
            total = order_info[4] if order_info[4] is not None else 0
            
            # Customer info
            customer_name = order_info[6] if order_info[6] is not None else "Guest Customer"
            customer_email = order_info[7] if order_info[7] is not None else "N/A"
            customer_address = order_info[8] if order_info[8] is not None else "N/A"
            
            # Display order info
            ttk.Label(info_frame, text=f"Order ID: {order_id}").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Date: {order_date}").grid(row=0, column=1, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Status: {status}").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text=f"Customer: {customer_name}").grid(row=2, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Email: {customer_email}").grid(row=2, column=1, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Address: {customer_address}").grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=2)
            
            ttk.Label(info_frame, text=f"Subtotal: ${subtotal:.2f}").grid(row=4, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Tax: ${tax:.2f}").grid(row=4, column=1, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=f"Total: ${total:.2f}", font=("", 10, "bold")).grid(row=5, column=0, columnspan=2, sticky="w", padx=5, pady=2)
            
            # Create items treeview
            items_tree = ttk.Treeview(
                items_frame,
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
            items_scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=items_tree.yview)
            items_tree.configure(yscrollcommand=items_scrollbar.set)
            
            # Pack
            items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            items_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert items
            for item in order_items:
                item_id, product_name, quantity, unit_price, item_subtotal = item
                items_tree.insert("", tk.END, values=(
                    item_id,
                    product_name,
                    quantity,
                    f"${unit_price:.2f}",
                    f"${item_subtotal:.2f}"
                ))
                
            # Addons section
            addons_frame = ttk.LabelFrame(details_window, text="Item Add-ons")
            addons_frame.pack(fill="x", expand=False, padx=10, pady=10)
            
            # Get addons for items
            addon_info = {}
            for item in order_items:
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
            
            # If addons exist, display them
            if addon_info:
                for item_id, addons in addon_info.items():
                    # Get item name
                    for item in order_items:
                        if item[0] == item_id:
                            item_name = item[1]
                            break
                    else:
                        item_name = f"Item #{item_id}"
                    
                    # Display addons
                    ttk.Label(addons_frame, text=f"{item_name} Add-ons:", font=("", 9, "bold")).pack(anchor="w", padx=5, pady=2)
                    
                    for addon in addons:
                        addon_name = addon[1]
                        addon_price = addon[2]
                        ttk.Label(addons_frame, text=f"• {addon_name} (+${addon_price:.2f})").pack(anchor="w", padx=20, pady=1)
            else:
                ttk.Label(addons_frame, text="No add-ons for this order").pack(padx=5, pady=5)
            
            # Buttons
            buttons_frame = ttk.Frame(details_window)
            buttons_frame.pack(fill="x", padx=10, pady=10)
            
            ttk.Button(buttons_frame, text="Close", command=details_window.destroy).pack(side=tk.RIGHT, padx=5)
            
            # Status update combobox
            status_var = tk.StringVar(value=status)
            ttk.Label(buttons_frame, text="Update Status:").pack(side=tk.LEFT, padx=5)
            status_combo = ttk.Combobox(buttons_frame, textvariable=status_var, 
                                      values=["pending", "completed", "delivered", "cancelled"])
            status_combo.pack(side=tk.LEFT, padx=5)
            
            def update_status():
                new_status = status_var.get()
                try:
                    self.cursor.execute("""
                        UPDATE orders SET status = %s WHERE order_id = %s
                    """, (new_status, order_id))
                    self.conn.commit()
                    messagebox.showinfo("Success", f"Order status updated to {new_status}")
                    self.refresh_order_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update status: {str(e)}")
            
            ttk.Button(buttons_frame, text="Update", command=update_status).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order details: {str(e)}")

    def view_ticket_details(self):
        selected_item = self.tickets_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ticket to view")
            return
            
        ticket_id = self.tickets_tree.item(selected_item[0])['values'][0]
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Ticket #{ticket_id} Details")
        details_window.geometry("500x400")
        
        try:
            # Get ticket info
            self.cursor.execute("""
                SELECT * FROM contact_submissions WHERE submission_id = %s
            """, (ticket_id,))
            
            ticket = self.cursor.fetchone()
            
            if not ticket:
                messagebox.showerror("Error", "Ticket information not found")
                details_window.destroy()
                return
            
            # Display ticket details
            main_frame = ttk.Frame(details_window, padding=10)
            main_frame.pack(fill="both", expand=True)
            
            # Ticket info
            ttk.Label(main_frame, text="Ticket Information", font=("", 12, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", pady=10)
            
            ttk.Label(main_frame, text="Ticket ID:").grid(row=1, column=0, sticky="w", pady=2)
            ttk.Label(main_frame, text=ticket[0]).grid(row=1, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Submission Date:").grid(row=2, column=0, sticky="w", pady=2)
            date_str = ticket[7].strftime("%Y-%m-%d %H:%M") if ticket[7] is not None else "N/A"
            ttk.Label(main_frame, text=date_str).grid(row=2, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Customer Information", font=("", 12, "bold")).grid(row=3, column=0, columnspan=2, sticky="w", pady=(20, 10))
            
            ttk.Label(main_frame, text="Name:").grid(row=4, column=0, sticky="w", pady=2)
            full_name = f"{ticket[1]} {ticket[2]}"
            ttk.Label(main_frame, text=full_name).grid(row=4, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Email:").grid(row=5, column=0, sticky="w", pady=2)
            ttk.Label(main_frame, text=ticket[3]).grid(row=5, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Country:").grid(row=6, column=0, sticky="w", pady=2)
            country = ticket[5] if ticket[5] is not None else "N/A"
            ttk.Label(main_frame, text=country).grid(row=6, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Ticket Details", font=("", 12, "bold")).grid(row=7, column=0, columnspan=2, sticky="w", pady=(20, 10))
            
            ttk.Label(main_frame, text="Service:").grid(row=8, column=0, sticky="w", pady=2)
            service = ticket[4] if ticket[4] is not None else "N/A"
            ttk.Label(main_frame, text=service).grid(row=8, column=1, sticky="w", pady=2)
            
            ttk.Label(main_frame, text="Subject:").grid(row=9, column=0, sticky="w", pady=2)
            subject = ticket[6] if ticket[6] is not None else "No subject"
            ttk.Label(main_frame, text=subject).grid(row=9, column=1, sticky="w", pady=2)
            
            # Response section
            ttk.Label(main_frame, text="Response", font=("", 12, "bold")).grid(row=10, column=0, columnspan=2, sticky="w", pady=(20, 10))
            
            response_text = tk.Text(main_frame, height=5, width=50, wrap="word")
            response_text.grid(row=11, column=0, columnspan=2, sticky="we", pady=5)
            
            # Buttons
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.grid(row=12, column=0, columnspan=2, sticky="e", pady=20)
            
            ttk.Button(buttons_frame, text="Send Response", command=lambda: self.send_ticket_response(ticket_id, response_text.get("1.0", "end-1c"))).pack(side=tk.LEFT, padx=5)
            ttk.Button(buttons_frame, text="Close", command=details_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load ticket details: {str(e)}")

    def send_ticket_response(self, ticket_id, response):
        if not response.strip():
            messagebox.showwarning("Warning", "Please enter a response message")
            return
            
        # In a real implementation, this would send an email or notification
        # For now, we'll just show a success message
        messagebox.showinfo("Success", "Response sent successfully")

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
                self.cursor.execute("""
                    UPDATE orders SET status = %s WHERE order_id = %s
                """, (new_status, order_id))
                self.conn.commit()
                messagebox.showinfo("Success", f"Order status updated to {new_status}")
                update_window.destroy()
                self.refresh_order_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update status: {str(e)}")
        
        ttk.Button(update_window, text="Save", command=save_status).pack(pady=20)

    def delete_order(self):
        selected_item = self.orders_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an order to delete")
            return
            
        order_id = self.orders_tree.item(selected_item[0])['values'][0]
        
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Order #{order_id}?\nThis cannot be undone."):
            return
            
        try:
            # Begin transaction
            self.conn.start_transaction()
            
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
            
            messagebox.showinfo("Success", f"Order #{order_id} has been deleted")
            self.refresh_order_list()
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to delete order: {str(e)}")
            
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
                messagebox.showinfo("Success", "Ticket created successfully!")
                new_window.destroy()
                self.refresh_ticket_list()
            except Exception as e:
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
            self.cursor.execute("DELETE FROM contact_submissions WHERE submission_id = %s", (ticket_id,))
            self.conn.commit()
            self.refresh_ticket_list()
            messagebox.showinfo("Success", f"Ticket #{ticket_id} deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete ticket: {str(e)}")

    def export_data(self):
        """Export orders and tickets to JSON files"""
        try:
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
                            "price": float(addon_price)
                        })
                    
                    items.append({
                        "id": item_id,
                        "product_id": product_id,
                        "name": product_name,
                        "quantity": quantity,
                        "unit_price": float(unit_price),
                        "subtotal": float(item_subtotal),
                        "addons": addons
                    })
                
                orders.append({
                    "id": order_id,
                    "customer": customer_name,
                    "email": email,
                    "address": address,
                    "date": order_date.isoformat() if order_date else None,
                    "subtotal": float(subtotal) if subtotal else 0,
                    "tax": float(tax) if tax else 0,
                    "total": float(total) if total else 0,
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
                    "date": submission_date.isoformat() if submission_date else None
                })
            
            # Write tickets to file
            with open("exported_tickets.json", "w") as f:
                json.dump(tickets, f, indent=2, default=str)
                
            messagebox.showinfo("Success", "Data exported to JSON files successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("Database connection closed")

def main():
    root = tk.Tk()
    app = PollosHermanosManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
