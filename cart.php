<?php
header('Content-Type: application/json');
error_reporting(E_ALL);
ini_set('display_errors', 1);
require_once 'db_config.php';

try {
    $database = new Database();
    $db = $database->getConnection();
    
    // Get the POST data
    $data = json_decode(file_get_contents('php://input'), true);
    
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        if (isset($data['action'])) {
            switch ($data['action']) {
                case 'add':
                    // Handle adding items to cart
                    $query = "INSERT INTO cart_items (order_id, product_id, quantity, price) 
                             VALUES (:order_id, :product_id, :quantity, :price)
                             ON DUPLICATE KEY UPDATE quantity = :quantity, price = :price";
                    
                    $stmt = $db->prepare($query);
                    $stmt->bindParam(':order_id', $data['order_id']);
                    $stmt->bindParam(':product_id', $data['product_id']);
                    $stmt->bindParam(':quantity', $data['quantity']);
                    $stmt->bindParam(':price', $data['price']);
                    
                    if ($stmt->execute()) {
                        // Handle addons if present
                        if (!empty($data['addons'])) {
                            foreach ($data['addons'] as $addon) {
                                $addonQuery = "INSERT INTO cart_item_addons (cart_item_id, addon_id, price)
                                             VALUES (LAST_INSERT_ID(), :addon_id, :price)";
                                $addonStmt = $db->prepare($addonQuery);
                                $addonStmt->execute([
                                    ':addon_id' => $addon['id'],
                                    ':price' => $addon['price']
                                ]);
                            }
                        }
                        echo json_encode(['status' => 'success', 'order_id' => $data['order_id']]);
                    }
                    break;

                case 'remove':
                    // Handle removing items from cart
                    $query = "DELETE FROM cart_items WHERE order_id = :order_id AND product_id = :product_id";
                    $stmt = $db->prepare($query);
                    $stmt->execute([
                        ':order_id' => $data['order_id'],
                        ':product_id' => $data['product_id']
                    ]);
                    echo json_encode(['status' => 'success']);
                    break;

                default:
                    throw new Exception('Invalid action');
            }
        }
    }
} catch (Exception $e) {
    echo json_encode([
        'status' => 'error',
        'message' => $e->getMessage()
    ]);
}
?>