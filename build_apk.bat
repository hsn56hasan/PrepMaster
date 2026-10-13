@echo off
chcp 65001 >nul
title PrepMaster Mobile - Android APK Derleyici

echo ========================================================
echo    PrepMaster Mobile - Android APK Derleyici
echo ========================================================
echo.

set PATH=C:\Projeler\flutter-sdk\flutter\bin;%PATH%
set ANDROID_HOME=C:\Projeler\android-sdk

cd /d "%~dp0mobile"

echo 1) Debug APK Derle (Hızlı test, telefona direkt yuklenebilir)
echo 2) Release APK Derle (Optimize edilmiş son sürüm)
echo.
set /p choice="Seciminizi yapin [1, 2] (Varsayilan 1): "

if "%choice%"=="2" goto BUILD_RELEASE
goto BUILD_DEBUG

:BUILD_DEBUG
echo Debug APK derleniyor... Lutfen bekleyin...
call flutter build apk --debug
if %errorlevel% neq 0 (
    echo [HATA] APK derlenirken bir sorun olustu.
    pause
    exit /b %errorlevel%
)
echo.
echo ========================================================
echo [BASARILI] Debug APK olusturuldu!
echo Konum: %~dp0mobile\build\app\outputs\flutter-apk\app-debug.apk
echo.
echo Bu dosyayi telefonunuza gonderip direkt kurabilirsiniz.
echo ========================================================
goto FINISH

:BUILD_RELEASE
echo Release APK derleniyor... Lutfen bekleyin...
call flutter build apk --release
if %errorlevel% neq 0 (
    echo [HATA] APK derlenirken bir sorun olustu.
    pause
    exit /b %errorlevel%
)
echo.
echo ========================================================
echo [BASARILI] Release APK olusturuldu!
echo Konum: %~dp0mobile\build\app\outputs\flutter-apk\app-release.apk
echo ========================================================
goto FINISH

:FINISH
pause
