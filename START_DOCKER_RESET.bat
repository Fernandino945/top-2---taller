@echo off
REM Script alternativo si Docker tiene problemas
REM Reinicia Docker Desktop y luego levanta los servicios

echo Verificando estado de Docker...
docker ps >nul 2>&1

if %errorlevel% neq 0 (
    echo Docker no responde. Intentando reiniciar Docker Desktop...
    taskkill /IM Docker.exe /F >nul 2>&1
    timeout /t 5 /nobreak
    cd /d "%ProgramFiles%\Docker\Docker"
    start Docker.exe
    echo Esperando a que Docker se inicie...
    timeout /t 30 /nobreak
)

cd /d "d:\hito 2\iot_agro_project"

echo Reiniciando servicios...
docker-compose down
timeout /t 5
docker-compose build --no-cache
timeout /t 10
docker-compose up -d
timeout /t 15

echo.
docker-compose ps

echo.
echo Estado de servicios listado arriba.
echo Dashboard: http://localhost:8501
echo.
pause
