# Quick Run Script for Timetable Project
# Double-click or run: .\run.ps1

Write-Host "🚀 Starting Timetable Project..." -ForegroundColor Green

# Activate virtual environment
Write-Host "`n📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Navigate to project
Write-Host "📁 Navigating to Django project..." -ForegroundColor Yellow
Set-Location "UseDjango\project_name"

# Run server
Write-Host "`n✅ Starting development server..." -ForegroundColor Green
Write-Host "📱 Open browser: http://127.0.0.1:8000/timetable/home/" -ForegroundColor Cyan
Write-Host "🛑 Press Ctrl+C to stop server`n" -ForegroundColor Red

python manage.py runserver
