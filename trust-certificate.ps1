# Requires administrator privileges
# Run from PowerShell with: .\trust-certificate.ps1

# Check if running as administrator
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Please right-click on this script and select 'Run with PowerShell as Administrator'." -ForegroundColor Red
    Pause
    exit
}

# Check if the certificate exists
if (-not (Test-Path ".\server.crt")) {
    Write-Host "Certificate file (server.crt) not found in the current directory." -ForegroundColor Red
    Write-Host "Please run the setup script first to generate certificates." -ForegroundColor Red
    Pause
    exit
}

# Import the certificate into the Trusted Root Certification Authorities store
try {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2(".\server.crt")
    $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
    $store.Open("ReadWrite")
    
    # Check if certificate is already in the store
    $existingCert = $store.Certificates | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
    
    if ($existingCert) {
        Write-Host "Certificate is already trusted." -ForegroundColor Green
    } else {
        # Add certificate to the store
        $store.Add($cert)
        Write-Host "Certificate successfully added to the Trusted Root Certification Authorities store." -ForegroundColor Green
        Write-Host "Your browser should now trust the HTTPS connection to your local server." -ForegroundColor Green
    }
    
    $store.Close()
} catch {
    Write-Host "Error importing certificate: $_" -ForegroundColor Red
}

Pause
