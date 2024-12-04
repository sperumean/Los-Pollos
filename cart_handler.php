<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Include database configuration
require_once 'db_config.php';  // Added this line

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header("Access-Control-Allow-Origin: https://lospolloshermanos.local");
    header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
    header("Access-Control-Allow-Headers: Content-Type, Accept");
    header("Access-Control-Allow-Credentials: true");
    exit(0);
}

header("Access-Control-Allow-Origin: https://lospolloshermanos.local");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type, Accept");
header("Access-Control-Allow-Credentials: true");
header("Content-Type: application/json");

try {
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        throw new Exception('Only POST method is allowed');
    }

    $rawInput = file_get_contents('php://input');
    if (!$rawInput) {
        throw new Exception('No input data received');
    }

    $data = json_decode($rawInput, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        throw new Exception('Invalid JSON input: ' . json_last_error_msg());
    }

    $database = new Database();
    $db = $database->getConnection();
    
    if (!isset($data['action'])) {
        throw new Exception('Action is required');
    }

    if ($data['action'] === 'add') {
        // Check if a new order needs to be created
        if ($data['order_id'] === 'new' || !$data['order_id']) {
            $orderQuery = "INSERT INTO orders (status, order_date) VALUES ('pending', NOW())";
            $db->exec($orderQuery);
            $data['order_id'] = $db->lastInsertId();
        }

        // Validate product_id
        if (!isset($data['product_id'])) {
            throw new Exception('Product ID is required');
        }

        // Fetch base price from products table
        $priceQuery = "SELECT base_price FROM products WHERE product_id = :product_id";
        $priceStmt = $db->prepare($priceQuery);
        $priceStmt->execute([':product_id' => $data['product_id']]);
        $productPrice = $priceStmt->fetchColumn();

        if ($productPrice === false) {
            throw new Exception('Product not found');
        }

        // Check if the item already exists
        $checkItemQuery = "SELECT order_item_id, quantity FROM order_items 
                          WHERE order_id = :order_id AND product_id = :product_id";
        $checkItemStmt = $db->prepare($checkItemQuery);
        $checkItemStmt->execute([
            ':order_id' => $data['order_id'],
            ':product_id' => $data['product_id']
        ]);
        $existingItem = $checkItemStmt->fetch(PDO::FETCH_ASSOC);

        if ($existingItem) {
            // Update existing item
            $updateQuery = "UPDATE order_items 
                          SET unit_price = :unit_price,
                              quantity = :quantity
                          WHERE order_item_id = :order_item_id";
            $updateStmt = $db->prepare($updateQuery);
            $updateStmt->execute([
                ':unit_price' => $productPrice,
                ':quantity' => $data['quantity'],
                ':order_item_id' => $existingItem['order_item_id']
            ]);
            $orderItemId = $existingItem['order_item_id'];
        } else {
            // Insert new item
            $insertQuery = "INSERT INTO order_items 
                          (order_id, product_id, quantity, unit_price) 
                          VALUES (:order_id, :product_id, :quantity, :unit_price)";
            
            $stmt = $db->prepare($insertQuery);
            $stmt->execute([
                ':order_id' => $data['order_id'],
                ':product_id' => $data['product_id'],
                ':quantity' => $data['quantity'],
                ':unit_price' => $productPrice
            ]);
            $orderItemId = $db->lastInsertId();
        }

        // Handle add-ons
        if (!empty($data['addons'])) {
            // Delete existing add-ons
            $deleteAddonsQuery = "DELETE FROM order_item_addons 
                                WHERE order_item_id = :order_item_id";
            $deleteStmt = $db->prepare($deleteAddonsQuery);
            $deleteStmt->execute([':order_item_id' => $orderItemId]);

            // Insert new add-ons
            foreach ($data['addons'] as $addon) {
                $addonQuery = "INSERT INTO order_item_addons 
                             (order_item_id, addon_id)
                             VALUES (:order_item_id, :addon_id)";
                $addonStmt = $db->prepare($addonQuery);
                $addonStmt->execute([
                    ':order_item_id' => $orderItemId,
                    ':addon_id' => $addon['id']
                ]);
            }
        }

        echo json_encode(['status' => 'success', 'order_id' => $data['order_id']]);
    }
    elseif ($data['action'] === 'remove') {
        if (!isset($data['order_id']) || !isset($data['product_id'])) {
            throw new Exception('Order ID and Product ID are required for removal');
        }

        $query = "DELETE FROM order_items 
                  WHERE order_id = :order_id AND product_id = :product_id";
        
        $stmt = $db->prepare($query);
        $stmt->execute([
            ':order_id' => $data['order_id'],
            ':product_id' => $data['product_id']
        ]);

        echo json_encode(['status' => 'success']);
    }
    elseif ($data['action'] === 'clear_cart') {
        if (!isset($data['order_id'])) {
            throw new Exception('Order ID is required to clear the cart');
        }

        $db->beginTransaction();
        try {
            $deleteOrderAddonsQuery = "DELETE FROM order_item_addons 
                                     WHERE order_item_id IN (SELECT order_item_id FROM order_items WHERE order_id = :order_id)";
            $deleteOrderAddonsStmt = $db->prepare($deleteOrderAddonsQuery);
            $deleteOrderAddonsStmt->execute([':order_id' => $data['order_id']]);

            $deleteOrderItemsQuery = "DELETE FROM order_items WHERE order_id = :order_id";
            $deleteOrderItemsStmt = $db->prepare($deleteOrderItemsQuery);
            $deleteOrderItemsStmt->execute([':order_id' => $data['order_id']]);

            $db->commit();
            echo json_encode(['status' => 'success', 'message' => 'Cart cleared successfully']);
        } catch (Exception $e) {
            $db->rollBack();
            throw $e;
        }
    } else {
        throw new Exception('Invalid action');
    }
} catch (Exception $e) {
    error_log("Cart handler error: " . $e->getMessage());
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>