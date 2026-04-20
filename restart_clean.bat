@echo off
REM Script para limpiar y reiniciar el sistema IoT Agrícola

echo ========================================
echo Limpiando sistema Docker...
echo ========================================
cd /d "d:\hito 2\iot_agro_project"

REM Detener todos los servicios
docker-compose down

REM Limpiar caché de Docker
docker system prune -f --all

REM Limpiar volúmenes de Streamlit (pero mantener datos de MongoDB)
docker volume prune -f

echo.
echo ========================================
echo Reconstruyendo imágenes sin caché...
echo ========================================

REM Reconstruir sin caché
docker-compose build --no-cache

echo.
echo ========================================
echo Iniciando servicios...
echo ========================================

REM Iniciar servicios
docker-compose up -d

echo.
echo ========================================
echo Esperando a que los servicios se inicien...
echo ========================================

timeout /t 15 /nobreak

echo.
echo ========================================
echo Estado de los servicios:
echo ========================================

docker-compose ps

echo.
echo Dashboard disponible en: http://localhost:8501
echo API disponible en: http://localhost:5000/zonas
echo.
pause
