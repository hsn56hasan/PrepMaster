@echo off
chcp 65001 >nul
title PrepMaster Mobile - Flutter Uygulama Baslatici

echo ========================================================
echo    PrepMaster Mobile - Flutter Uygulama Baslatıcı
echo ========================================================
echo.

set PATH=C:\Projeler\flutter-sdk\flutter\bin;%PATH%
set ANDROID_HOME=C:\Projeler\android-sdk

cd /d "%~dp0mobile"

echo Bagli Cihazlar Kontrol Ediliyor:
call flutter devices
echo.
echo ========================================================
echo 1) Bagli Cihazda Calistir (Otomatik Secim)
echo 2) Windows Masaustu Olarak Calistir (flutter run -d windows)
echo 3) Web / Chrome Olarak Calistir (flutter run -d chrome)
echo ========================================================
echo.
set /p choice="Seciminizi yapin [1, 2, 3] (Varsayilan 1): "

if "%choice%"=="2" goto RUN_WIN
if "%choice%"=="3" goto RUN_CHROME
goto RUN_DEFAULT

:RUN_DEFAULT
echo Uygulama baslatiliyor...
call flutter run
goto END

:RUN_WIN
echo Windows masaustu uygulamasi baslatiliyor...
call flutter run -d windows
goto END

:RUN_CHROME
echo Web uzerinde baslatiliyor...
call flutter run -d chrome
goto END

:END
pause
