# PowerShell script to start Advanced Travel Platform on Windows
Write-Host "Starting Advanced Travel Platform on Windows..." -ForegroundColor Green
Write-Host ""

# Check Node.js installation
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Node.js is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Node.js from https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Setting up environment files..." -ForegroundColor Yellow

# Setup backend environment
if (-not (Test-Path "backend\.env")) {
    Write-Host "Creating backend .env file..." -ForegroundColor Cyan
    Copy-Item "backend\.env.local" "backend\.env"
}

# Setup frontend environment
if (-not (Test-Path "frontend\.env")) {
    Write-Host "Creating frontend .env file..." -ForegroundColor Cyan
    Copy-Item "frontend\.env.local" "frontend\.env"
}

Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Cyan
Set-Location backend
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed" }
} catch {
    Write-Host "ERROR: Backend dependency installation failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Cyan
Set-Location ..\frontend
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed" }
} catch {
    Write-Host "ERROR: Frontend dependency installation failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Set-Location ..

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend will run on: http://localhost:8001" -ForegroundColor Cyan
Write-Host "Frontend will run on: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""

# Start backend server
Write-Host "Starting backend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; npm run dev"

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend server
Write-Host "Starting frontend server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "The frontend will automatically open in your browser." -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this setup script..." -ForegroundColor Yellow
Read-Host