@echo off
echo Starting Advanced Travel Platform on Windows...
echo.

echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js found: 
node --version

echo.
echo Setting up environment files...

REM Setup backend environment
if not exist "backend\.env" (
    echo Creating backend .env file...
    copy "backend\.env.local" "backend\.env"
)

REM Setup frontend environment
if not exist "frontend\.env" (
    echo Creating frontend .env file...
    copy "frontend\.env.local" "frontend\.env"
)

echo.
echo Installing dependencies...

echo Installing backend dependencies...
cd backend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Backend dependency installation failed
    pause
    exit /b 1
)

echo Installing frontend dependencies...
cd ..\frontend
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Frontend dependency installation failed
    pause
    exit /b 1
)

cd ..

echo.
echo Starting servers...
echo.
echo Backend will run on: http://localhost:8001
echo Frontend will run on: http://localhost:3000
echo.
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && npm run dev"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo The frontend will automatically open in your browser.
echo.
echo Press any key to exit this setup script...
pause >nul