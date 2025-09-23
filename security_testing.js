// security_testing.js - Connect to your PHP backend

// Tab functionality
function openTab(evt, tabName) {
    var i, tabcontent, tabs;
    tabcontent = document.getElementsByClassName("tab-content");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].classList.remove("active");
    }
    tabs = document.getElementsByClassName("tab");
    for (i = 0; i < tabs.length; i++) {
        tabs[i].classList.remove("active");
    }
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// XSS Functions (Client-side testing)
function testReflectedXSS() {
    const urlParams = new URLSearchParams(window.location.search);
    const testParam = urlParams.get('test');
    if (testParam) {
        document.getElementById('urlParam').innerHTML = testParam;
    } else {
        document.getElementById('urlParam').innerHTML = 'No test parameter found. Add ?test=<script>alert("XSS")</script> to URL';
    }
}

function displayUserInput() {
    const input = document.getElementById('userInput').value;
    document.getElementById('inputOutput').innerHTML = 'You entered: ' + input;
}

function performSearch() {
    const searchTerm = document.getElementById('searchInput').value;
    document.getElementById('searchOutput').innerHTML = 
        'Search results for: ' + searchTerm + 
        '\n\nFound items:\n- Hermanos Burger\n- Chicken Burrito\n- Curly Fries';
}

function updateDOM() {
    const input = document.getElementById('domInput').value;
    document.getElementById('domOutput').innerHTML = input;
}

function addComment() {
    const comment = document.getElementById('commentInput').value;
    const timestamp = new Date().toLocaleString();
    const currentComments = document.getElementById('commentOutput').innerHTML;
    document.getElementById('commentOutput').innerHTML = currentComments + 
        '\n[' + timestamp + '] Comment: ' + comment + '\n';
}

// SQL Injection Functions (Connected to PHP backend)
async function testLogin() {
    const username = document.getElementById('loginUser').value;
    const password = document.getElementById('loginPass').value;
    
    try {
        const response = await fetch('/vulnerable_login.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        let output = `SQL Query: ${data.query}\n\n`;
        output += `Status: ${data.success ? 'SUCCESS' : 'FAILED'}\n`;
        output += `Message: ${data.message}\n`;
        
        if (data.data && data.data.length > 0) {
            output += `\nData Retrieved:\n`;
            data.data.forEach(row => {
                output += JSON.stringify(row, null, 2) + '\n';
            });
        }
        
        document.getElementById('loginOutput').textContent = output;
        
    } catch (error) {
        document.getElementById('loginOutput').textContent = 'Error: ' + error.message;
    }
}

async function searchProducts() {
    const search = document.getElementById('productSearch').value;
    
    try {
        const response = await fetch('/vulnerable_search.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                search: search
            })
        });
        
        const data = await response.json();
        
        let output = `SQL Query: ${data.query}\n\n`;
        output += `Status: ${data.success ? 'SUCCESS' : 'FAILED'}\n`;
        output += `Message: ${data.message}\n`;
        
        if (data.data && data.data.length > 0) {
            output += `\nResults Found:\n`;
            data.data.forEach(row => {
                output += JSON.stringify(row, null, 2) + '\n';
            });
        }
        
        document.getElementById('productOutput').textContent = output;
        
    } catch (error) {
        document.getElementById('productOutput').textContent = 'Error: ' + error.message;
    }
}

async function getUserInfo() {
    const userId = document.getElementById('userIdInput').value;
    
    try {
        const response = await fetch('/vulnerable_user_lookup.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userId: userId
            })
        });
        
        const data = await response.json();
        
        let output = `SQL Query: ${data.query}\n\n`;
        output += `Status: ${data.success ? 'SUCCESS' : 'FAILED'}\n`;
        output += `Message: ${data.message}\n`;
        
        if (data.data && data.data.length > 0) {
            output += `\nUser Information:\n`;
            data.data.forEach(row => {
                output += JSON.stringify(row, null, 2) + '\n';
            });
        }
        
        document.getElementById('userInfoOutput').textContent = output;
        
    } catch (error) {
        document.getElementById('userInfoOutput').textContent = 'Error: ' + error.message;
    }
}

async function lookupOrder() {
    const orderId = document.getElementById('orderIdInput').value;
    
    // Use existing order lookup functionality if available
    try {
        const response = await fetch('/checkout_handler.php?order_id=' + encodeURIComponent(orderId));
        const data = await response.json();
        
        let output = `Order Lookup Query (simulated vulnerability)\n\n`;
        output += `Order ID: ${orderId}\n`;
        output += `Status: ${data.status}\n`;
        output += `Message: ${data.message || 'Order lookup completed'}\n`;
        
        if (data.cart_items) {
            output += `\nOrder Items:\n`;
            data.cart_items.forEach(item => {
                output += `- ${item.product_name}: $${item.unit_price}\n`;
            });
        }
        
        document.getElementById('orderOutput').textContent = output;
        
    } catch (error) {
        document.getElementById('orderOutput').textContent = 'Error: ' + error.message;
    }
}

function customSqlTest() {
    const testType = document.getElementById('sqlTestType').value;
    const payload = document.getElementById('customSqlInput').value;
    
    let result = 'Test Type: ' + testType.toUpperCase() + '\n';
    result += 'Payload: ' + payload + '\n\n';
    
    // For now, keep the simulated testing
    // You can extend this to connect to actual vulnerable endpoints
    
    switch(testType) {
        case 'basic':
            result += 'Testing for SQL syntax errors...\n';
            if (payload.includes("'") || payload.includes('"')) {
                result += 'ERROR: SQL syntax error detected!\n';
                result += 'Injection point confirmed.';
            } else {
                result += 'No syntax errors detected.';
            }
            break;
        case 'blind':
            result += 'Testing blind SQL injection...\n';
            result += 'Response time: 0.03s (normal)\n';
            result += 'Testing TRUE condition: 0.03s\n';
            result += 'Testing FALSE condition: 0.03s\n';
            result += 'No significant time difference detected.';
            break;
        case 'time':
            result += 'Testing time-based blind injection...\n';
            if (payload.includes('SLEEP') || payload.includes('WAITFOR')) {
                result += 'Time delay detected!\n';
                result += 'Response time: 5.2s (delayed)\n';
                result += 'Time-based injection confirmed!';
            } else {
                result += 'Response time: 0.03s (normal)';
            }
            break;
        case 'union':
            result += 'Testing UNION-based injection...\n';
            if (payload.includes('UNION')) {
                result += 'UNION statement detected!\n';
                result += 'Columns matched successfully.\n';
                result += 'Data extraction possible!';
            } else {
                result += 'No UNION statement detected.';
            }
            break;
    }
    
    document.getElementById('customSqlOutput').textContent = result;
}

// XSS Server-side testing
async function testServerXSS() {
    const input = document.getElementById('serverXSSInput').value;
    
    try {
        const response = await fetch('/xss_test_endpoint.php?input=' + encodeURIComponent(input));
        const htmlResponse = await response.text();
        
        document.getElementById('serverXSSOutput').innerHTML = 
            'Server Response (potentially vulnerable):\n' + htmlResponse;
        
    } catch (error) {
        document.getElementById('serverXSSOutput').textContent = 'Error: ' + error.message;
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    testReflectedXSS();
});
