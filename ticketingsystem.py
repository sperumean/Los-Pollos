import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

class TicketSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Ticket Management System")
        self.root.geometry("800x600")

        # Database connection with MariaDB compatible charset
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",  # Replace with your MySQL username
            password="W00fW00f#!?",  # Replace with your MySQL password
            database="walter",
            charset='utf8mb4',
            collation='utf8mb4_general_ci'
        )
        self.cursor = self.conn.cursor()

        # Create main frames
        self.create_widgets()
        self.refresh_ticket_list()

    def create_widgets(self):
        # Left frame for ticket list
        left_frame = ttk.Frame(self.root)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Ticket list
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Name", "Email", "Service", "Subject", "Date"), show="headings")
        
        # Define column headings
        self.tree.heading("ID", text="ID")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Service", text="Service")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Date", text="Date")

        # Configure column widths
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=100)
        self.tree.column("Email", width=150)
        self.tree.column("Service", width=100)
        self.tree.column("Subject", width=100)
        self.tree.column("Date", width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right frame for ticket details and actions
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)

        # New Ticket Button
        ttk.Button(right_frame, text="New Ticket", command=self.open_new_ticket_window).pack(pady=5, fill=tk.X)

        # Refresh Button
        ttk.Button(right_frame, text="Refresh List", command=self.refresh_ticket_list).pack(pady=5, fill=tk.X)

        # Delete Button
        ttk.Button(right_frame, text="Delete Selected", command=self.delete_selected_ticket).pack(pady=5, fill=tk.X)

    def refresh_ticket_list(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch and display tickets
        self.cursor.execute("SELECT * FROM contact_submissions ORDER BY submission_date DESC")
        for ticket in self.cursor.fetchall():
            full_name = f"{ticket[1]} {ticket[2]}"
            self.tree.insert("", tk.END, values=(ticket[0], full_name, ticket[3], ticket[4], ticket[6], ticket[7]))

    def open_new_ticket_window(self):
        new_window = tk.Toplevel(self.root)
        new_window.title("New Ticket")
        new_window.geometry("400x500")

        # Form fields
        ttk.Label(new_window, text="First Name:").pack(pady=5)
        first_name_entry = ttk.Entry(new_window)
        first_name_entry.pack(pady=5)

        ttk.Label(new_window, text="Last Name:").pack(pady=5)
        last_name_entry = ttk.Entry(new_window)
        last_name_entry.pack(pady=5)

        ttk.Label(new_window, text="Email:").pack(pady=5)
        email_entry = ttk.Entry(new_window)
        email_entry.pack(pady=5)

        ttk.Label(new_window, text="Service:").pack(pady=5)
        service_combo = ttk.Combobox(new_window, values=["Customer Service", "Technical Support", "Billing"])
        service_combo.pack(pady=5)

        ttk.Label(new_window, text="Country:").pack(pady=5)
        country_entry = ttk.Entry(new_window)
        country_entry.pack(pady=5)

        ttk.Label(new_window, text="Subject:").pack(pady=5)
        subject_entry = ttk.Entry(new_window)
        subject_entry.pack(pady=5)

        def submit_ticket():
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
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a ticket to delete")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this ticket?"):
            ticket_id = self.tree.item(selected_item[0])['values'][0]
            try:
                self.cursor.execute("DELETE FROM contact_submissions WHERE submission_id = %s", (ticket_id,))
                self.conn.commit()
                self.refresh_ticket_list()
                messagebox.showinfo("Success", "Ticket deleted successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete ticket: {str(e)}")

    def __del__(self):
        if hasattr(self, 'conn') and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicketSystem(root)
    root.mainloop()
