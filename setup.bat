@echo off
echo Walter's Website HTTPS Setup
echo ===========================
echo.

:: Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrator privileges.
    echo Please right-click on this batch file and select "Run as administrator".
    pause
    exit /b 1
)

:: Check if OpenSSL is installed
where openssl >nul 2>&1
if %errorlevel% neq 0 (
    echo OpenSSL is not installed or not in your PATH.
    echo.
    echo Options:
    echo 1. Install OpenSSL using Chocolatey (requires Chocolatey)
    echo 2. Install OpenSSL manually (will open browser)
    echo 3. Exit and install OpenSSL yourself
    echo.
    set /p option="Select an option (1-3): "
    
    if "%option%"=="1" (
        echo Installing OpenSSL using Chocolatey...
        choco install openssl
        if %errorlevel% neq 0 (
            echo Chocolatey not installed or installation failed.
            echo Please install OpenSSL manually.
            start https://slproweb.com/products/Win32OpenSSL.html
            pause
            exit /b 1
        )
    ) else if "%option%"=="2" (
        echo Opening browser to OpenSSL download page...
        start https://slproweb.com/products/Win32OpenSSL.html
        echo Please install OpenSSL, add it to your PATH, and run this script again.
        pause
        exit /b 1
    ) else (
        echo Exiting...
        pause
        exit /b 1
    )
)

:: Generate certificates
echo Generating self-signed certificates...
openssl genrsa -out server.key 2048
if %errorlevel% neq 0 (
    echo Failed to generate private key.
    pause
    exit /b 1
)

openssl req -new -key server.key -out server.csr -subj "/C=US/ST=State/L=City/O=Walter/CN=localhost"
if %errorlevel% neq 0 (
    echo Failed to generate certificate signing request.
    pause
    exit /b 1
)

openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
if %errorlevel% neq 0 (
    echo Failed to generate self-signed certificate.
    pause
    exit /b 1
)

echo Certificates generated successfully!
echo.

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python and run this script again.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Install required Python packages
echo Installing required Python packages...
pip install mysql-connector-python
if %errorlevel% neq 0 (
    echo Failed to install required Python packages.
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo Options to run the server:
echo 1. Run on standard HTTPS port (443) - requires admin rights
echo 2. Run on test port (8443) - doesn't require admin rights
echo 3. Exit
echo.
set /p run_option="Select an option (1-3): "

if "%run_option%"=="1" (
    echo Starting server on port 443...
    python secure_server.py
) else if "%run_option%"=="2" (
    echo Starting server on port 8443...
    python secure_server.py test
) else (
    echo Exiting...
)

pause
