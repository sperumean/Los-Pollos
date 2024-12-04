
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mysql.connector
from urllib.parse import parse_qs, urlparse
import cgi
import os
import mimetypes
import decimal
from decimal import Decimal


class DatabaseConnection:
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': 'W00fW00f#!?',
            'host': 'localhost',
            'database': 'walter',
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_general_ci',
            'use_unicode': True,
            'buffered': True
        }

    def connect(self):
        try:
            conn = mysql.connector.connect(**self.config)
            print("Database connection successful")
            # Set the connection charset explicitly
            cursor = conn.cursor()
            cursor.execute('SET NAMES utf8mb4')
            cursor.execute('SET CHARACTER SET utf8mb4')
            cursor.execute('SET character_set_connection=utf8mb4')
            cursor.close()
            return conn
        except Exception as e:
            print("Database connection failed:", str(e))
            raise e

class RequestHandler(BaseHTTPRequestHandler):
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', f'{content_type}; charset=utf-8')
                self.end_headers()
                self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "File not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API endpoints
        if path == '/api/products':
            self.handle_get_products()
        elif path.startswith('/api/cart/'):
            order_id = path.split('/')[-1]
            self.handle_get_cart(order_id)
        # Static file serving
        elif path == '/':
            self.serve_file('contact.html', 'text/html')
        elif path.endswith('.html'):
            file_path = path[1:]
            self.serve_file(file_path, 'text/html')
        elif path.endswith('.js'):
            self.serve_file(path[1:], 'text/javascript')
        elif path.endswith('.css'):
            self.serve_file(path[1:], 'text/css')
        elif path.endswith('.png'):
            self.serve_file(path[1:], 'image/png')
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            self.serve_file(path[1:], 'image/jpeg')
        else:
            self.send_error(404)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()

        if self.path == '/api/contact':
            self.handle_contact_form()
        elif self.path == '/api/cart/add':
            self.handle_cart_add()
        elif self.path == '/api/cart/remove':
            self.handle_cart_remove()
        elif self.path == '/api/cart/update':
            self.handle_cart_update()
        elif self.path == '/api/cart/checkout':
            self.handle_cart_checkout()
        else:
            self.send_error(404)

    def handle_get_products(self):
        try:
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT p.*, GROUP_CONCAT(
                    JSON_OBJECT(
                        'id', a.addon_id,
                        'name', a.name,
                        'price', a.price
                    )
                ) as addons
                FROM products p
                LEFT JOIN add_ons a ON p.product_id = a.product_id
                GROUP BY p.product_id
            """)
            
            products = cursor.fetchall()
            
            response = {
                'status': 'success',
                'products': products
            }
            
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            
        finally:
            if 'conn' in locals():
                conn.close()
                
        self.wfile.write(json.dumps(response).encode())



    def handle_cart_remove(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        cart_data = json.loads(post_data.decode('utf-8'))
        
        try:
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            # Remove item and its add-ons
            cursor.execute("""
                DELETE oia 
                FROM order_item_addons oia
                JOIN order_items oi ON oia.order_item_id = oi.order_item_id
                WHERE oi.order_id = %s AND oi.product_id = %s
            """, (cart_data['order_id'], cart_data['product_id']))

            cursor.execute("""
                DELETE FROM order_items 
                WHERE order_id = %s AND product_id = %s
            """, (cart_data['order_id'], cart_data['product_id']))
            
            conn.commit()
            
            response = {
                'status': 'success',
                'message': 'Item removed from cart'
            }
            
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            
        finally:
            if 'conn' in locals():
                conn.close()
                
        self.wfile.write(json.dumps(response).encode())

    def handle_cart_update(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        cart_data = json.loads(post_data.decode('utf-8'))
        
        try:
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE order_items 
                SET quantity = %s 
                WHERE order_id = %s AND product_id = %s
            """, (
                cart_data['quantity'],
                cart_data['order_id'],
                cart_data['product_id']
            ))
            
            conn.commit()
            
            response = {
                'status': 'success',
                'message': 'Cart updated successfully'
            }
            
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            
        finally:
            if 'conn' in locals():
                conn.close()
                
        self.wfile.write(json.dumps(response).encode())

    def handle_cart_checkout(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        checkout_data = json.loads(post_data.decode('utf-8'))
        
        try:
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()

            # Create customer record
            cursor.execute("""
                INSERT INTO customers 
                (first_name, last_name, email, address)
                VALUES (%s, %s, %s, %s)
            """, (
                checkout_data['first_name'],
                checkout_data['last_name'],
                checkout_data['email'],
                checkout_data['address']
            ))
            
            customer_id = cursor.lastrowid

            # Update order with customer info and totals
            cursor.execute("""
                UPDATE orders 
                SET customer_id = %s,
                    subtotal = %s,
                    tax = %s,
                    total = %s,
                    status = 'completed'
                WHERE order_id = %s
            """, (
                customer_id,
                checkout_data['subtotal'],
                checkout_data['tax'],
                checkout_data['total'],
                checkout_data['order_id']
            ))
            
            conn.commit()
            
            response = {
                'status': 'success',
                'message': 'Order placed successfully',
                'order_id': checkout_data['order_id']
            }
            
        except Exception as e:
            response = {
                'status': 'error',
                'message': str(e)
            }
            
        finally:
            if 'conn' in locals():
                conn.close()
                
        self.wfile.write(json.dumps(response).encode())




    def handle_cart_add(self): 
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        cart_data = json.loads(post_data.decode('utf-8'))
        
        try:
            print("\nReceived cart data:", cart_data)  # Debug print
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor(buffered=True)

            conn.start_transaction()

            try:
                # Check if order exists
                if cart_data.get('order_id'):
                    cursor.execute("""
                        SELECT order_id FROM orders WHERE order_id = %s
                    """, (cart_data['order_id'],))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO orders (order_id, status) 
                            VALUES (%s, 'pending')
                        """, (cart_data['order_id'],))
                else:
                    cursor.execute("""
                        INSERT INTO orders (status) VALUES ('pending')
                    """)
                    cart_data['order_id'] = cursor.lastrowid

                # Get correct product price from database
                cursor.execute("""
                    SELECT base_price FROM products WHERE product_id = %s
                """, (cart_data['product_id'],))
                product_price = cursor.fetchone()[0]
                print(f"Product base price: {product_price}")  # Debug print

                # Check if item already exists in cart
                cursor.execute("""
                    SELECT order_item_id 
                    FROM order_items 
                    WHERE order_id = %s AND product_id = %s
                """, (cart_data['order_id'], cart_data['product_id']))
                
                existing_item = cursor.fetchone()
                
                if existing_item:
                    print(f"Updating existing item: {existing_item[0]}")
                    cursor.execute("""
                        UPDATE order_items 
                        SET quantity = %s, 
                            unit_price = %s 
                        WHERE order_id = %s 
                        AND product_id = %s
                    """, (
                        cart_data['quantity'],
                        product_price,  # Use price from database
                        cart_data['order_id'],
                        cart_data['product_id']
                    ))
                    
                    order_item_id = existing_item[0]
                    
                    # Remove existing addons
                    cursor.execute("""
                        DELETE FROM order_item_addons 
                        WHERE order_item_id = %s
                    """, (order_item_id,))
                else:
                    print("Creating new order item")
                    cursor.execute("""
                        INSERT INTO order_items 
                        (order_id, product_id, quantity, unit_price)
                        VALUES (%s, %s, %s, %s)
                    """, (
                        cart_data['order_id'],
                        cart_data['product_id'],
                        cart_data['quantity'],
                        product_price  # Use price from database
                    ))
                    order_item_id = cursor.lastrowid

                # Add new addons
                if 'addons' in cart_data and cart_data['quantity'] > 0:
                    for addon in cart_data['addons']:
                        cursor.execute("""
                            INSERT INTO order_item_addons 
                            (order_item_id, addon_id)
                            VALUES (%s, %s)
                        """, (order_item_id, addon['id']))

                conn.commit()
                print("Transaction committed successfully")
                
                response = {
                    'status': 'success',
                    'message': 'Item added to cart',
                    'order_id': cart_data['order_id']
                }
                
            except Exception as e:
                conn.rollback()
                raise e
                
        except Exception as e:
            print("Error in handle_cart_add:", str(e))
            response = {
                'status': 'error',
                'message': str(e)
            }
            
        finally:
            if 'conn' in locals():
                conn.close()
                
        self.wfile.write(json.dumps(response).encode())

    def handle_get_cart(self, order_id):
        try:
            print(f"\nFetching cart data for order_id: {order_id}")
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor(dictionary=True, buffered=True)

            # First verify the order exists
            cursor.execute("""
                SELECT order_id, status 
                FROM orders 
                WHERE order_id = %s
            """, (order_id,))
            
            order = cursor.fetchone()
            if not order:
                print(f"Order {order_id} not found")
                self.send_error(404, f"Order {order_id} not found")
                return

            print(f"Found order: {order}")

            # Get order items with product information
            cursor.execute("""
                SELECT 
                    oi.order_item_id,
                    oi.quantity,
                    oi.unit_price,
                    p.name,
                    p.product_id,
                    p.base_price
                FROM order_items oi
                JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s AND oi.quantity > 0
            """, (order_id,))
            
            items = cursor.fetchall()
            print(f"Found {len(items)} items in cart")

            cart_items = []
            subtotal = 0

            for item in items:
                print(f"Processing item: {item}")
                # Calculate item base cost
                item_subtotal = float(item['unit_price']) * item['quantity']
                
                # Get addons for this item
                cursor.execute("""
                    SELECT 
                        a.addon_id as id,
                        a.name,
                        a.price
                    FROM order_item_addons oia
                    JOIN add_ons a ON oia.addon_id = a.addon_id
                    WHERE oia.order_item_id = %s
                """, (item['order_item_id'],))
                
                addons = cursor.fetchall()
                print(f"Found {len(addons)} addons for item {item['order_item_id']}")

                # Calculate addons cost
                addon_list = []
                for addon in addons:
                    addon_price = float(addon['price'])
                    item_subtotal += addon_price * item['quantity']
                    addon_list.append({
                        'id': addon['id'],
                        'name': addon['name'],
                        'price': addon_price
                    })

                cart_items.append({
                    'order_item_id': item['order_item_id'],
                    'name': item['name'],
                    'quantity': item['quantity'],
                    'unit_price': float(item['unit_price']),
                    'addons': addon_list,
                    'item_total': item_subtotal
                })

                subtotal += item_subtotal

            tax = round(subtotal * 0.1, 2)  # 10% tax, rounded to 2 decimal places
            total = round(subtotal + tax, 2)

            response = {
                'status': 'success',
                'cart_items': cart_items,
                'subtotal': subtotal,
                'tax': tax,
                'total': total
            }
            
            print("Successfully prepared cart response:", response)
            
            # Send the response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
            
        except Exception as e:
            print("Error in handle_get_cart:", str(e))
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {
                'status': 'error',
                'message': str(e)
            }
            self.wfile.write(json.dumps(error_response).encode())
            
        finally:
            if 'conn' in locals():
                conn.close()


    def handle_contact_form(self):
        print("\n=== Contact Form Submission ===")
        try:
            # Parse form data
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],
                }
            )
            
            # Validate required fields
            required_fields = ['firstname', 'lastname', 'email', 'Service', 'country']
            data = {}
            for field in required_fields:
                value = form.getvalue(field)
                if not value:
                    raise ValueError(f"Missing required field: {field}")
                data[field] = value
            
            # Add optional subject field
            data['subject'] = form.getvalue('subject', '')
            
            print("Form Data:", data)
            
            # Database connection
            db = DatabaseConnection()
            conn = db.connect()
            cursor = conn.cursor()
            
            print("Database connected successfully")
            
            # Prepare and execute query
            query = """
                INSERT INTO contact_submissions 
                (first_name, last_name, email, service, country, subject)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (
                data['firstname'],
                data['lastname'],
                data['email'],
                data['Service'],
                data['country'],
                data['subject']
            )
            
            print("Executing query with values:", values)
            
            cursor.execute(query, values)
            conn.commit()
            
            submission_id = cursor.lastrowid
            print(f"Submission successful. ID: {submission_id}")
            
            response = {
                'status': 'success',
                'message': 'Form submitted successfully',
                'submission_id': submission_id
            }
            
        except Exception as e:
            print("Error occurred:", str(e))
            response = {
                'status': 'error',
                'message': str(e)
            }
        
        finally:
            if 'conn' in locals():
                conn.close()
                print("Database connection closed")
                
        self.wfile.write(json.dumps(response).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
