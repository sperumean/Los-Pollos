<?php
// vulnerable_login.php - Simple SQL injection testing endpoint
// WARNING: This file is intentionally vulnerable for educational purposes only!
// Domain: lospolloshermanos.local

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

// Include your database config
include 'db_config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get the JSON input
    $input = json_decode(file_get_contents('php://input'), true);
    $username = $input['username'] ?? '';
    $password = $input['password'] ?? '';
    
    // INTENTIONALLY VULNERABLE SQL QUERY - DO NOT USE IN PRODUCTION!
    $query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
    
    // Execute the query and return results
    try {
        $result = mysqli_query($conn, $query);
        
        $response = [
            'query_executed' => $query,
            'success' => false,
            'message' => '',
            'data' => []
        ];
        
        if ($result) {
            if (mysqli_num_rows($result) > 0) {
                $response['success'] = true;
                $response['message'] = 'Login successful!';
                $response['data'] = mysqli_fetch_all($result, MYSQLI_ASSOC);
            } else {
                $response['message'] = 'No matching user found';
            }
        } else {
            $response['message'] = 'SQL Error: ' . mysqli_error($conn);
        }
        
        echo json_encode($response, JSON_PRETTY_PRINT);
        
    } catch (Exception $e) {
        echo json_encode([
            'query_executed' => $query,
            'success' => false,
            'message' => 'Error: ' . $e->getMessage()
        ], JSON_PRETTY_PRINT);
    }
}
?>
