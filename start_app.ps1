# Start Backend
Write-Host "Starting Backend Server..." -ForegroundColor Green
Start-Process -FilePath "uvicorn" -ArgumentList "backend.main:app --reload --port 8000" -WorkingDirectory "$PSScriptRoot" -WindowStyle Minimized

# Start Frontend
Write-Host "Starting Frontend..." -ForegroundColor Green
Set-Location "$PSScriptRoot/frontend"
# FIX: Use npm.cmd for Windows compatibility in Start-Process
Start-Process -FilePath "npm.cmd" -ArgumentList "run dev" -WindowStyle Normal

# Wait a moment for servers to spin up
Start-Sleep -Seconds 3

# Open Browser correctly
Write-Host "Opening Browser..." -ForegroundColor Cyan
Start-Process "http://localhost:5173"

Write-Host "App is running!" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
