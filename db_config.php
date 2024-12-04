<?php
// db_config.php
class Database {
    private $host = "localhost";
    private $db_name = "walter";  // Using the database name from your MariaDB output
    private $username = "root";    // Replace with your actual database username
    private $password = "W00fW00f#!?";        // Replace with your actual database password
    public $conn;

    public function getConnection() {
        $this->conn = null;
        try {
            $this->conn = new PDO(
                "mysql:host=" . $this->host . ";dbname=" . $this->db_name . ";charset=utf8mb4",
                $this->username,
                $this->password
            );
            $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        } catch(PDOException $exception) {
            echo "Connection error: " . $exception->getMessage();
        }
        return $this->conn;
    }
}
?>
