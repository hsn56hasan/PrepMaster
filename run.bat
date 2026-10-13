@echo off
chcp 65001 >nul
title PrepMaster - Üniversite Hazırlık Platformu

echo ========================================================
echo    PrepMaster - Üniversite Hazırlık & Muafiyet Platformu
echo ========================================================
echo.
echo Sunucu baslatiliyor... Lutfen bekleyin.
echo Bilgisayarda acmak icin: http://localhost:8050
echo Telefondan / Tabletten (ayni Wi-Fi) acmak icin: http://172.16.1.211:8050
echo.

cd /d "%~dp0"

start http://localhost:8050

python -m uvicorn backend.app:app --host 0.0.0.0 --port 8050 --reload
pause
