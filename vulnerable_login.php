<?php
// vulnerable_login.php - For SQL Injection Testing
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

include 'db_config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $username = $input['username'] ?? '';
    $password = $input['password'] ?? '';
    
    // INTENTIONALLY VULNERABLE SQL QUERY - FOR TESTING ONLY!
    $query = "SELECT * FROM users WHERE username='$username' AND password='$password'";
    
    try {
        $result = mysqli_query($conn, $query);
        
        $response = [
            'query' => $query,
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
                $response['message'] = 'Invalid credentials';
            }
        } else {
            $response['message'] = 'SQL Error: ' . mysqli_error($conn);
        }
        
        echo json_encode($response);
    } catch (Exception $e) {
        echo json_encode([
            'query' => $query,
            'success' => false,
            'message' => 'Error: ' . $e->getMessage()
        ]);
    }
}
?>

<?php
// vulnerable_search.php - For SQL Injection Testing
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

include 'db_config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $search = $input['search'] ?? '';
    
    // INTENTIONALLY VULNERABLE SQL QUERY
    $query = "SELECT * FROM products WHERE id='$search' OR name LIKE '%$search%'";
    
    try {
        $result = mysqli_query($conn, $query);
        
        $response = [
            'query' => $query,
            'success' => false,
            'message' => '',
            'data' => []
        ];
        
        if ($result) {
            $response['success'] = true;
            $response['data'] = mysqli_fetch_all($result, MYSQLI_ASSOC);
            $response['message'] = 'Query executed successfully';
        } else {
            $response['message'] = 'SQL Error: ' . mysqli_error($conn);
        }
        
        echo json_encode($response);
    } catch (Exception $e) {
        echo json_encode([
            'query' => $query,
            'success' => false,
            'message' => 'Error: ' . $e->getMessage()
        ]);
    }
}
?>

<?php
// vulnerable_user_lookup.php - For UNION-based SQL Injection
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

include 'db_config.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $userId = $input['userId'] ?? '';
    
    // INTENTIONALLY VULNERABLE SQL QUERY
    $query = "SELECT username, email, role FROM users WHERE id=$userId";
    
    try {
        $result = mysqli_query($conn, $query);
        
        $response = [
            'query' => $query,
            'success' => false,
            'message' => '',
            'data' => []
        ];
        
        if ($result) {
            $response['success'] = true;
            $response['data'] = mysqli_fetch_all($result, MYSQLI_ASSOC);
            $response['message'] = 'User lookup successful';
        } else {
            $response['message'] = 'SQL Error: ' . mysqli_error($conn);
        }
        
        echo json_encode($response);
    } catch (Exception $e) {
        echo json_encode([
            'query' => $query,
            'success' => false,
            'message' => 'Error: ' . $e->getMessage()
        ]);
    }
}
?>

<?php
// xss_test_endpoint.php - For XSS Testing
header('Content-Type: text/html');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $input = $_GET['input'] ?? '';
    
    // INTENTIONALLY VULNERABLE - Direct output without sanitization
    echo "<div>You entered: $input</div>";
    echo "<div>Reflection test: $input</div>";
    
} elseif ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = json_decode(file_get_contents('php://input'), true);
    $userInput = $input['userInput'] ?? '';
    
    // INTENTIONALLY VULNERABLE - Direct JSON output
    echo json_encode([
        'success' => true,
        'message' => 'Input processed: ' . $userInput,
        'reflected' => $userInput
    ]);
}
?>
