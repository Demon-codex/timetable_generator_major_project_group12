# Setup Script - Run this ONCE before first use
# Run: .\setup.ps1

Write-Host "⚙️  Setting up Timetable Project..." -ForegroundColor Green

# Activate virtual environment
Write-Host "`n📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Navigate to project
Set-Location "UseDjango\project_name"

# Apply migrations
Write-Host "`n🗄️  Creating database tables..." -ForegroundColor Yellow
python manage.py migrate

# Create superuser
Write-Host "`n👤 Create admin account (optional - press Ctrl+C to skip):" -ForegroundColor Cyan
python manage.py createsuperuser

Write-Host "`n✅ Setup complete! Now run: .\run.ps1" -ForegroundColor Green
