<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Debug output
error_log("Request Method: " . $_SERVER['REQUEST_METHOD']);
error_log("POST Data: " . print_r($_POST, true));

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    require_once 'db_config.php';
    
    // Debug POST data
    error_log("Received POST data: " . print_r($_POST, true));
    
    try {
        $database = new Database();
        $db = $database->getConnection();
        
        // Collect and sanitize form data
        $firstname = htmlspecialchars($_POST['firstname'] ?? '');
        $lastname = htmlspecialchars($_POST['lastname'] ?? '');
        $email = htmlspecialchars($_POST['email'] ?? '');
        $service = htmlspecialchars($_POST['Service'] ?? '');
        $country = htmlspecialchars($_POST['country'] ?? '');
        $subject = htmlspecialchars($_POST['subject'] ?? '');

        // Debug sanitized data
        error_log("Sanitized data: " . print_r(compact('firstname', 'lastname', 'email', 'service', 'country', 'subject'), true));



        // Prepare SQL statement
        $query = "INSERT INTO contact_submissions 
                 (first_name, last_name, email, service, country, subject) 
                 VALUES 
                 (:firstname, :lastname, :email, :service, :country, :subject)";
        
        $stmt = $db->prepare($query);
        
        // Bind parameters
        $stmt->bindParam(":firstname", $firstname);
        $stmt->bindParam(":lastname", $lastname);
        $stmt->bindParam(":email", $email);
        $stmt->bindParam(":service", $service);
        $stmt->bindParam(":country", $country);
        $stmt->bindParam(":subject", $subject);
        
        // Execute query
        if (!$stmt->execute()) {
            throw new Exception("Failed to insert data into database");
        }


        // Display success message with styled HTML
        echo '<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Submission Successful</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 20px auto;
                    padding: 20px;
                    background-color: #f7f7f7;
                }
                .success-message {
                    background-color: #dff0d8;
                    border: 1px solid #d6e9c6;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }
                .details {
                    background-color: white;
                    padding: 15px;
                    border-radius: 4px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                .home-link {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 10px 20px;
                    background-color: #337ab7;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
            <div class="success-message">
                <h1>Thank You!</h1>
                <p>We have received your message and will contact you soon.</p>
            </div>
            <div class="details">
                <h2>Submission Details:</h2>
                <p><strong>Name:</strong> ' . $firstname . ' ' . $lastname . '</p>
                <p><strong>Email:</strong> ' . $email . '</p>
                <p><strong>Service:</strong> ' . $service . '</p>
                <p><strong>Country:</strong> ' . $country . '</p>
                <p><strong>Subject:</strong> ' . $subject . '</p>
            </div>
            <a href="polloshermanoswebsite.html" class="home-link">Return to Home</a>
        </body>
        </html>';


    } catch(Exception $e) {
        error_log("Error in action_page.php: " . $e->getMessage());
        echo "Error: " . $e->getMessage();
    }
} else {
    error_log("Invalid request method: " . $_SERVER["REQUEST_METHOD"]);
    echo "Invalid request method. POST required.";
}
?>