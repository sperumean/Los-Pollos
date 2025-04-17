from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import mysql.connector
from urllib.parse import parse_qs, urlparse
import os
import mimetypes
import decimal
from decimal import Decimal
import email.parser

# Add this after your imports but before the class definitions
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
        
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


class FieldStorage:
    """Replacement for cgi.FieldStorage that uses urllib and email packages"""
    
    def __init__(self, environ=None, headers=None, fp=None, keep_blank_values=False):
        self.environ = environ or {}
        self.headers = headers
        self.fp = fp
        self.keep_blank_values = keep_blank_values
        self.form = {}
        self.files = {}
        self._parse_input()
    
    def _parse_input(self):
        # Get content type from headers or environ
        content_type = self.headers.get('Content-Type', '') if self.headers else ''
        if not content_type and 'CONTENT_TYPE' in self.environ:
            content_type = self.environ['CONTENT_TYPE']
        
        # Get content length
        content_length = 0
        if self.headers and 'Content-Length' in self.headers:
            try:
                content_length = int(self.headers['Content-Length'])
            except ValueError:
                content_length = 0
        elif 'CONTENT_LENGTH' in self.environ:
            try:
                content_length = int(self.environ['CONTENT_LENGTH'])
            except ValueError:
                content_length = 0
        
        # Parse form data based on content type
        if content_type.startswith('application/x-www-form-urlencoded'):
            # Handle URL-encoded form data
            if self.fp:
                data = self.fp.read(content_length).decode('utf-8')
                self.form = parse_qs(data, keep_blank_values=self.keep_blank_values)
        elif content_type.startswith('application/json'):
            # Handle JSON data
            if self.fp:
                data = self.fp.read(content_length).decode('utf-8')
                try:
                    json_data = json.loads(data)
                    # Convert JSON object to form-like structure
                    if isinstance(json_data, dict):
                        for key, value in json_data.items():
                            self.form[key] = [value] if not isinstance(value, list) else value
                except json.JSONDecodeError:
                    pass
        elif content_type.startswith('multipart/form-data'):
            # Handle multipart form data (files + form fields)
            if not self.fp:
                return
                
            # Find boundary
            boundary = None
            for part in content_type.split(';'):
                part = part.strip()
                if part.startswith('boundary='):
                    boundary = part[9:]
                    if boundary.startswith('"') and boundary.endswith('"'):
                        boundary = boundary[1:-1]
                    break
            
            if not boundary:
                return
                
            # Read and parse multipart data
            data = self.fp.read(content_length)
            
            # Parse the multipart form data
            message = email.parser.BytesParser().parsebytes(
                b'Content-Type: ' + content_type.encode() + b'\r\n\r\n' + data
            )
            
            if message.is_multipart():
                for part in message.get_payload():
                    # Get the part's Content-Disposition header
                    content_disp = part.get('Content-Disposition', '')
                    if not content_disp:
                        continue
                        
                    # Parse the Content-Disposition to get the field name
                    disposition_parts = content_disp.split(';')
                    if disposition_parts[0].strip() != 'form-data':
                        continue
                        
                    # Extract field name
                    field_name = None
                    filename = None
                    for disp_part in disposition_parts[1:]:
                        disp_part = disp_part.strip()
                        if disp_part.startswith('name='):
                            field_name = disp_part[5:]
                            if field_name.startswith('"') and field_name.endswith('"'):
                                field_name = field_name[1:-1]
                        elif disp_part.startswith('filename='):
                            filename = disp_part[9:]
                            if filename.startswith('"') and filename.endswith('"'):
                                filename = filename[1:-1]
                    
                    if not field_name:
                        continue
                        
                    # Get the part's payload
                    payload = part.get_payload(decode=True)
                    
                    # If filename is provided, treat as file upload
                    if filename:
                        content_type = part.get_content_type()
                        self.files[field_name] = {
                            'filename': filename,
                            'content_type': content_type,
                            'data': payload
                        }
                    else:
                        # Regular form field
                        value = payload.decode('utf-8')
                        if field_name in self.form:
                            if isinstance(self.form[field_name], list):
                                self.form[field_name].append(value)
                            else:
                                self.form[field_name] = [self.form[field_name], value]
                        else:
                            self.form[field_name] = [value]
        
        # Handle query string parameters for GET requests
        if 'QUERY_STRING' in self.environ:
            query_params = parse_qs(self.environ['QUERY_STRING'], 
                                    keep_blank_values=self.keep_blank_values)
            # Merge with form data, query params take precedence
            for key, values in query_params.items():
                self.form[key] = values
    
    def getvalue(self, field_name, default=None):
        """Get the value of a field"""
        if field_name in self.form:
            values = self.form[field_name]
            if values and len(values) > 0:
                return values[0]
        return default
    
    def getlist(self, field_name):
        """Get all values of a field as a list"""
        return self.form.get(field_name, [])
    
    def getfirst(self, field_name, default=None):
        """Get the first value of a field"""
        return self.getvalue(field_name, default)
    
    def keys(self):
        """Return all field names"""
        return list(self.form.keys())
    
    def __contains__(self, key):
        return key in self.form
    
    def __getitem__(self, key):
        if key in self.form:
            values = self.form[key]
            if values and len(values) > 0:
                return values[0]
        raise KeyError(key)


class RequestHandler(BaseHTTPRequestHandler):
    def serve_file(self, file_path, content_type):
        try:
            # Print debugging information
            print(f"Attempting to serve file: {file_path} with content type: {content_type}")
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                alt_paths = [
                    # Try common variations of the path
                    file_path.replace('\\', '/'),
                    os.path.basename(file_path),
                    os.path.join('..', file_path),
                    os.path.join('images', os.path.basename(file_path))  # Check in images directory
                ]
                
                # Print alternative paths being checked
                print(f"Checking alternative paths: {alt_paths}")
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        print(f"Found file at alternative path: {alt_path}")
                        file_path = alt_path
                        break
                else:
                    print("File not found in any location")
                    self.send_error(404, "File not found")
                    return
            
            # Get file size for binary files
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size} bytes")
            
            with open(file_path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                
                # Special handling for video files - set proper MIME type and additional headers
                if file_path.endswith('.mp4'):
                    self.send_header('Content-Type', 'video/mp4')
                    self.send_header('Accept-Ranges', 'bytes')
                    self.send_header('Content-Length', str(file_size))
                    self.send_header('Cache-Control', 'public, max-age=86400')
                else:
                    self.send_header('Content-Type', f'{content_type}; charset=utf-8')
                
                self.end_headers()
                self.wfile.write(content)
                print(f"Successfully served file: {file_path}")
        except FileNotFoundError:
            print(f"FileNotFoundError: {file_path}")
            self.send_error(404, "File not found")
        except Exception as e:
            print(f"Error serving file {file_path}: {str(e)}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        print(f"\nHandling GET request for path: {self.path}")
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
            # Serve index.html as the default
            self.serve_file('index.html', 'text/html')
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
        elif path.endswith('.mp4'):
            # Handle video files
            print(f"Serving MP4 file: {path[1:]}")
            self.serve_file(path[1:], 'video/mp4')
        elif path.endswith('.webm'):
            self.serve_file(path[1:], 'video/webm')
        elif path.endswith('.ogg'):
            self.serve_file(path[1:], 'video/ogg')
        elif path.startswith('/api/placeholder/'):
            try:
                parts = path.split('/')
                if len(parts) >= 4:
                    width = int(parts[3])
                    height = int(parts[4]) if len(parts) > 4 else width
                    
                    # Generate a simple colored rectangle as a placeholder
                    self.send_response(200)
                    self.send_header('Content-Type', 'image/svg+xml')
                    self.end_headers()
                    
                    # Create a simple SVG placeholder
                    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
                        <rect width="{width}" height="{height}" fill="#cccccc"/>
                        <text x="{width/2}" y="{height/2}" font-family="Arial" font-size="16" fill="#666666" text-anchor="middle" alignment-baseline="middle">{width}x{height}</text>
                    </svg>'''
                    
                    self.wfile.write(svg.encode())
                    return
            except Exception as e:
                print(f"Error creating placeholder image: {str(e)}")
                self.send_error(500, f"Internal server error: {str(e)}")
                return
        else:
            print(f"Unsupported path: {path}")
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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

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
                # Check if we need to create a new order
                if cart_data.get('order_id') == 'new' or not cart_data.get('order_id'):
                    # Create a new order
                    cursor.execute("""
                        INSERT INTO orders (status) VALUES ('pending')
                    """)
                    cart_data['order_id'] = cursor.lastrowid
                    print(f"Created new order with ID: {cart_data['order_id']}")
                else:
                    # Check if existing order exists
                    cursor.execute("""
                        SELECT order_id FROM orders WHERE order_id = %s
                    """, (cart_data['order_id'],))
                    if not cursor.fetchone():
                        # Order doesn't exist, create it with the specified ID
                        cursor.execute("""
                            INSERT INTO orders (order_id, status) 
                            VALUES (%s, 'pending')
                        """, (cart_data['order_id'],))
    
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
                # Check if order exists or if a new order is needed
                if cart_data.get('order_id') == 'new' or not cart_data.get('order_id'):
                    # Create a new order
                    cursor.execute("""
                        INSERT INTO orders (status) VALUES ('pending')
                    """)
                    cart_data['order_id'] = cursor.lastrowid
                    print(f"Created new order ID: {cart_data['order_id']}")
                elif cart_data.get('order_id'):
                    # Check if existing order ID is valid
                    cursor.execute("""
                        SELECT order_id FROM orders WHERE order_id = %s
                    """, (cart_data['order_id'],))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO orders (order_id, status) 
                            VALUES (%s, 'pending')
                        """, (cart_data['order_id'],))

        
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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

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
                    'product_id': item['product_id'],  # Make sure this is included
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
            
            # Use the DecimalEncoder for proper JSON serialization
            self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())
            
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
            self.wfile.write(json.dumps(error_response, cls=DecimalEncoder).encode())
            
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_contact_form(self):
        print("\n=== Contact Form Submission ===")
        try:
            # Get content-type and content-length
            content_type = self.headers.get('Content-Type', '')
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Set up environment dict for FieldStorage
            environ = {
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
                'CONTENT_LENGTH': content_length,
            }
            
            # Read post data
            post_data = self.rfile.read(content_length)
            
            # Parse form data using our custom FieldStorage class
            if content_type == 'application/json':
                # Direct JSON parsing
                data = json.loads(post_data.decode('utf-8'))
            else:
                # URL-encoded form data parsing
                form_data = parse_qs(post_data.decode('utf-8'))
                data = {}
                for key, values in form_data.items():
                    data[key] = values[0] if values else ''
            
            # Validate required fields
            required_fields = ['firstname', 'lastname', 'email', 'Service', 'country']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Missing required field: {field}")
            
            # Add optional subject field
            data['subject'] = data.get('subject', '')
            
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
                
        self.wfile.write(json.dumps(response, cls=DecimalEncoder).encode())

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
