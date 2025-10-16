# Enable SQL Server Mixed Mode Authentication
# Run this script as Administrator

Write-Host "Enabling SQL Server Mixed Mode Authentication..." -ForegroundColor Yellow

# Set LoginMode to 2 (Mixed Mode)
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL16.SQLEXPRESS\MSSQLServer" -Name "LoginMode" -Value 2

Write-Host "✅ Mixed Mode Authentication enabled!" -ForegroundColor Green
Write-Host ""
Write-Host "Now restarting SQL Server..." -ForegroundColor Yellow

# Restart SQL Server
Restart-Service -Name "MSSQL`$SQLEXPRESS" -Force

Write-Host "✅ SQL Server restarted successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now connect with SQL Server Authentication" -ForegroundColor Cyan
Write-Host "Username: ReconciliationApp" -ForegroundColor Cyan
Write-Host "Server: (local)\SQLEXPRESS" -ForegroundColor Cyan
