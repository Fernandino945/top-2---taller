@echo off
REM Script para reiniciar el sistema IoT Agrícola
REM Ejecutar como administrador si es necesario

cd /d "d:\hito 2\iot_agro_project"

echo Deteniendo servicios...
docker-compose down

echo.
echo Esperando 5 segundos...
timeout /t 5 /nobreak

echo.
echo Limpiando imagenes problematicas...
docker system prune -f

echo.
echo Reconstruyendo imagenes...
docker-compose build --no-cache

echo.
echo Iniciando servicios...
docker-compose up -d

echo.
echo Esperando a que se inicien completamente...
timeout /t 15 /nobreak

echo.
echo Estado actual:
docker-compose ps

echo.
echo Dashboard en: http://localhost:8501
echo API en: http://localhost:5000/zonas
echo.
pause
