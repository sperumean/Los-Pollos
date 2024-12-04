<?php
header('Content-Type: application/json');
error_reporting(E_ALL);
ini_set('display_errors', 1);
require_once 'db_config.php';

// Add CORS headers
header("Access-Control-Allow-Origin: https://lospolloshermanos.local");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Accept");
header("Access-Control-Allow-Credentials: true");

try {
    $database = new Database();
    $db = $database->getConnection();

    // Handle OPTIONS preflight request
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        exit(0);
    }

    // Handle POST requests for placing orders
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $data = json_decode(file_get_contents('php://input'), true);
        
        if ($data['action'] === 'place_order') {
            $orderId = $data['order_id'];
            $customerInfo = $data['customer_info'];
            $totals = $data['totals'];
            
            // Check if the customer already exists based on email
            $stmt = $db->prepare("SELECT customer_id FROM customers WHERE email = :email");
            $stmt->execute([':email' => $customerInfo['email']]);
            $customerId = $stmt->fetchColumn();

            // Insert new customer if not found
            if (!$customerId) {
                $insertCustomer = $db->prepare("INSERT INTO customers (first_name, last_name, email, address) VALUES (:first_name, :last_name, :email, :address)");
                
                // Split "name" into first and last names
                $nameParts = explode(' ', $customerInfo['name'], 2);
                $firstName = $nameParts[0];
                $lastName = isset($nameParts[1]) ? $nameParts[1] : '';

                $insertCustomer->execute([
                    ':first_name' => $firstName,
                    ':last_name' => $lastName,
                    ':email' => $customerInfo['email'],
                    ':address' => $customerInfo['address']
                ]);
                $customerId = $db->lastInsertId();
            }

            // Update the order with customer_id and totals
            $updateOrder = $db->prepare("UPDATE orders SET customer_id = :customer_id, subtotal = :subtotal, tax = :tax, total = :total, status = 'completed' WHERE order_id = :order_id");
            $updateOrder->execute([
                ':customer_id' => $customerId,
                ':subtotal' => round($totals['subtotal'], 2),
                ':tax' => round($totals['tax'], 2),
                ':total' => round($totals['total'], 2),
                ':order_id' => $orderId
            ]);

            echo json_encode(['status' => 'success', 'message' => 'Order placed successfully']);
        }
    }
    // Handle GET requests for retrieving order details
    elseif ($_SERVER['REQUEST_METHOD'] === 'GET') {
        $orderId = $_GET['order_id'] ?? null;
        if (!$orderId) {
            throw new Exception('Order ID is required');
        }

        // Get order items with product details
        $query = "SELECT oi.*, p.name AS product_name, p.base_price
                  FROM order_items oi
                  JOIN products p ON oi.product_id = p.product_id
                  WHERE oi.order_id = :order_id";

        $stmt = $db->prepare($query);
        $stmt->execute([':order_id' => $orderId]);
        $orderItems = $stmt->fetchAll(PDO::FETCH_ASSOC);

        $subtotal = 0;
        foreach ($orderItems as &$item) {
            // Fetch add-ons for each item
            $addonQuery = "SELECT oia.*, a.name AS addon_name, a.price
                           FROM order_item_addons oia
                           JOIN add_ons a ON oia.addon_id = a.addon_id
                           WHERE oia.order_item_id = :order_item_id";
            $addonStmt = $db->prepare($addonQuery);
            $addonStmt->execute([':order_item_id' => $item['order_item_id']]);
            $item['addons'] = $addonStmt->fetchAll(PDO::FETCH_ASSOC);

            // Calculate item total
            $item['unit_price'] = floatval($item['unit_price']);
            $itemTotal = $item['quantity'] * $item['unit_price'];
            foreach ($item['addons'] as $addon) {
                $itemTotal += $addon['price'] * $item['quantity'];
            }
            $item['item_total'] = $itemTotal;
            $subtotal += $itemTotal;
        }

        $tax = $subtotal * 0.10;
        $total = $subtotal + $tax;

        echo json_encode([
            'status' => 'success',
            'cart_items' => $orderItems,
            'subtotal' => round($subtotal, 2),
            'tax' => round($tax, 2),
            'total' => round($total, 2)
        ]);
    }
} catch (Exception $e) {
    error_log("Checkout handler error: " . $e->getMessage());
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>