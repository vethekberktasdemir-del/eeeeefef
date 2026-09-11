@echo off
REM HBS v2.0 - Windows EXE Builder Script

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     HBS v2.0 Advanced - Windows EXE Builder               ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Hata: Python yüklü değil!
    echo    Lütfen Python 3.8+ yükleyin.
    pause
    exit /b 1
)

echo ✓ Python bulundu
echo.

REM Install dependencies
echo 📦 Gerekli paketler yükleniyor...
pip install --upgrade pip >nul 2>&1
pip install pyinstaller matplotlib >nul 2>&1

if errorlevel 1 (
    echo ❌ Paketler yüklenemedi!
    pause
    exit /b 1
)

echo ✓ Paketler kuruldu
echo.

REM Clean old build
echo 🧹 Eski build dosyaları temizleniyor...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "HBS-v2.0.spec" del "HBS-v2.0.spec"

echo ✓ Temizlik tamamlandı
echo.

REM Build EXE
echo 🔨 EXE dosyası derleniyyor... (Bu biraz zaman alabilir)
echo.

pyinstaller --onefile ^
    --windowed ^
    --name "HBS-v2.0" ^
    --icon=icon.ico ^
    --add-data "hbs_data.db;." ^
    --distpath "./dist" ^
    --buildpath "./build" ^
    --specpath "./" ^
    hbs_advanced.py

if errorlevel 1 (
    echo.
    echo ❌ EXE derlemesi başarısız oldu!
    pause
    exit /b 1
)

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║          ✓ EXE Dosyası Başarıyla Oluşturuldu!            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.
echo 📁 Konum: dist\HBS-v2.0.exe
echo.
pause
