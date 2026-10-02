# fix_venv.ps1
Write-Host "🚀 Fixing Virtual Environment..." -ForegroundColor Green
Write-Host ""

# Step 1: Delete old venv
if (Test-Path "venv") {
    Write-Host "Removing old virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force venv
}

# Step 2: Create new venv
Write-Host "Creating fresh virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Step 3: Activate it
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Step 4: Install packages
Write-Host "Installing packages..." -ForegroundColor Yellow
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install flask flask-cors flask-socketio
.\venv\Scripts\python.exe -m pip install opencv-python pillow numpy
.\venv\Scripts\python.exe -m pip install eventlet

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "To start server, run: python app.py" -ForegroundColor Cyan
Write-Host "Or for test server: python test_server.py" -ForegroundColor Cyan

# Keep window open
Read-Host "`nPress Enter to exit"