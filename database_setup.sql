
-- Los Pollos Hermanos Database Setup Script
-- This script creates all necessary tables for the ordering and ticket management system

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS walter CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE walter;

-- Products table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    image_url VARCHAR(255),
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add-ons table
CREATE TABLE IF NOT EXISTS add_ons (
    addon_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    subtotal DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    total DECIMAL(10, 2),
    status ENUM('pending', 'completed', 'delivered', 'cancelled') DEFAULT 'pending',
    customer_id INT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL
);

-- Order Items table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);

-- Order Item Add-ons table
CREATE TABLE IF NOT EXISTS order_item_addons (
    order_item_addon_id INT AUTO_INCREMENT PRIMARY KEY,
    order_item_id INT NOT NULL,
    addon_id INT NOT NULL,
    FOREIGN KEY (order_item_id) REFERENCES order_items(order_item_id) ON DELETE CASCADE,
    FOREIGN KEY (addon_id) REFERENCES add_ons(addon_id) ON DELETE RESTRICT
);

-- Contact/Support Tickets table
CREATE TABLE IF NOT EXISTS contact_submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL,
    service VARCHAR(100) NOT NULL,
    country VARCHAR(100),
    subject VARCHAR(255),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample product data if table is empty
INSERT INTO products (name, description, base_price, image_url, category)
SELECT 'French/Curly Fries', 'Crispy golden fries, perfectly seasoned.', 2.50, 'los_pollos_hermanos.menu.pic.1.jpg', 'Sides'
WHERE NOT EXISTS (SELECT 1 FROM products LIMIT 1);

INSERT INTO products (name, description, base_price, image_url, category)
SELECT 'Hermanos Burger', 'Juicy beef patty with our special sauce.', 3.79, 'los_pollos_hermanos.menu.pic.2.jpeg', 'Burgers'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Hermanos Burger');

INSERT INTO products (name, description, base_price, image_url, category)
SELECT 'New Mexico Chicken Burrito', 'Tender chicken wrapped in a soft tortilla.', 3.00, 'polloshermanoschickenburrito.jfif', 'Mexican'
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'New Mexico Chicken Burrito');

-- Insert sample add-ons if table is empty
INSERT INTO add_ons (product_id, name, price)
SELECT 1, 'Combo', 3.49
WHERE NOT EXISTS (SELECT 1 FROM add_ons LIMIT 1);

INSERT INTO add_ons (product_id, name, price)
SELECT 1, 'Chilli P', 2.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Chilli P' AND product_id = 1);

INSERT INTO add_ons (product_id, name, price)
SELECT 1, 'Blue Sky', 1.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Blue Sky' AND product_id = 1);

INSERT INTO add_ons (product_id, name, price)
SELECT 2, 'Combo', 2.20
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Combo' AND product_id = 2);

INSERT INTO add_ons (product_id, name, price)
SELECT 2, 'Chilli P', 2.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Chilli P' AND product_id = 2);

INSERT INTO add_ons (product_id, name, price)
SELECT 2, 'Blue Sky', 1.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Blue Sky' AND product_id = 2);

INSERT INTO add_ons (product_id, name, price)
SELECT 3, 'Combo', 3.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Combo' AND product_id = 3);

INSERT INTO add_ons (product_id, name, price)
SELECT 3, 'Chilli P', 4.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Chilli P' AND product_id = 3);

INSERT INTO add_ons (product_id, name, price)
SELECT 3, 'Blue Sky', 6.00
WHERE NOT EXISTS (SELECT 1 FROM add_ons WHERE name = 'Blue Sky' AND product_id = 3);

-- Create indexes for better performance
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_addons_product ON add_ons(product_id);
CREATE INDEX idx_order_item_addons_item ON order_item_addons(order_item_id);
CREATE INDEX idx_order_item_addons_addon ON order_item_addons(addon_id);

-- Grant permissions (adjust as needed for your environment)
GRANT ALL PRIVILEGES ON walter.* TO 'root'@'localhost';
FLUSH PRIVILEGES;

SELECT 'Los Pollos Hermanos database setup completed successfully!' AS 'Status';
