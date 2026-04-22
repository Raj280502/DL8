# Script to reset database and migrations
# Run from backend directory

Write-Host "🔧 Resetting Django database and migrations..." -ForegroundColor Cyan

# Step 1: Delete database
if (Test-Path "db.sqlite3") {
    Remove-Item "db.sqlite3" -Force
    Write-Host "✅ Deleted db.sqlite3" -ForegroundColor Green
}

# Step 2: Delete migration files (keep __init__.py)
Write-Host "`n🗑️  Deleting old migrations..." -ForegroundColor Yellow

$apps = @("api", "brain")
foreach ($app in $apps) {
    $migrationsPath = Join-Path $app "migrations"
    if (Test-Path $migrationsPath) {
        Get-ChildItem $migrationsPath -Filter "*.py" | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
        Write-Host "  ✅ Cleaned $app/migrations" -ForegroundColor Green
    }
}

Write-Host "`n📝 Creating new migrations..." -ForegroundColor Cyan
python manage.py makemigrations

Write-Host "`n🔄 Running migrations..." -ForegroundColor Cyan
python manage.py migrate

Write-Host "`n👤 Creating superuser..." -ForegroundColor Cyan
Write-Host "   You'll be prompted to create an admin account." -ForegroundColor Yellow
python manage.py createsuperuser

Write-Host "`n✅ Database reset complete!" -ForegroundColor Green
Write-Host "   You can now start the server with: python manage.py runserver" -ForegroundColor Cyan
