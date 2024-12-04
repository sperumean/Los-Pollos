# Create updated test.php with new credentials
$content = @'
<?php
echo "<h1>Starting Database Test</h1>";
error_reporting(E_ALL);
ini_set('display_errors', 1);
echo "<h2>Before try-catch block</h2>";
try {
    echo "<p>Attempting database connection...</p>";
    $conn = new PDO("mysql:host=localhost;dbname=walter;charset=utf8mb4", "root", "W00fW00f#!?");
    echo "<h2 style='color:green;'>Database connection successful!</h2>";
    
    // Test a simple query
    $stmt = $conn->query("SELECT COUNT(*) FROM contact_submissions");
    $count = $stmt->fetchColumn();
    echo "<p>Number of records in contact_submissions: " . $count . "</p>";
} catch(PDOException $e) {
    echo "<h2 style='color:red;'>Connection failed: " . $e->getMessage() . "</h2>";
}
echo "<h2>After try-catch block</h2>";
phpinfo();
?>
'@
Set-Content -Path "C:\inetpub\wwwroot\test.php" -Value $content