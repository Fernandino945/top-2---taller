# Manual de Usuario - Sistema IoT Agrícola

## 📋 Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación y Configuración](#instalación-y-configuración)
4. [Inicio del Sistema](#inicio-del-sistema)
5. [Interfaz del Dashboard](#interfaz-del-dashboard)
6. [Funcionalidades Principales](#funcionalidades-principales)
7. [Filtros Avanzados](#filtros-avanzados)
8. [API REST](#api-rest)
9. [Solución de Problemas](#solución-de-problemas)
10. [Mantenimiento](#mantenimiento)

---

## Introducción

El Sistema IoT Agrícola es una solución integral de monitoreo en tiempo real para cultivos. Proporciona:

- 📊 **Monitoreo en Tiempo Real**: Lectura continua de sensores de temperatura y humedad
- 🌍 **Gestión Multi-Zona**: Control de múltiples cultivos simultáneamente
- 📈 **Análisis Avanzados**: Visualizaciones estadísticas y comparativas
- 💾 **Persistencia de Datos**: Almacenamiento en MongoDB para consultas históricas
- 🔗 **Arquitectura Modular**: Componentes desacoplados y escalables

### Cultivos Soportados

- 🍅 **Tomate**: Control de temperatura y humedad para cultivos de tomate
- 🥕 **Zanahoria**: Monitoreo optimizado para raíces
- 🌽 **Maíz**: Seguimiento de desarrollo de plantas

---

## Requisitos del Sistema

### Hardware Mínimo

- **Procesador**: Intel/AMD dual-core 2.0 GHz o superior
- **RAM**: 4 GB mínimo (8 GB recomendado)
- **Almacenamiento**: 500 MB para la aplicación + datos históricos
- **Red**: Conexión Ethernet o WiFi estable
- **Sensores**: Sensores IoT compatibles con MQTT (QoS 1)

### Software Requerido

- **Docker**: 20.10 o superior
- **Docker Compose**: 1.29 o superior
- **Sistema Operativo**: Linux, Windows (con WSL2) o macOS

### Puertos Necesarios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| MQTT Broker | 1883 | Comunicación sensores |
| API REST | 5000 | Endpoint de datos |
| Dashboard | 8501 | Interface web |
| MongoDB | 27017 | Base de datos (interno) |

---

## Instalación y Configuración

### Paso 1: Clonar o Descargar el Proyecto

```bash
# Si tienes acceso al repositorio
git clone <repository-url>
cd iot_agro_project

# O descomprime el archivo ZIP
unzip iot_agro_project.zip
cd iot_agro_project
```

### Paso 2: Verificar Docker

```bash
# Verificar que Docker está instalado
docker --version
# Salida: Docker version 20.10.x or higher

# Verificar Docker Compose
docker-compose --version
# Salida: Docker Compose version 1.29.x or higher
```

### Paso 3: Configuración del Entorno (Opcional)

Crea un archivo `.env` en el directorio raíz si necesitas personalizar:

```bash
# .env
API_URL=http://localhost:5000
MQTT_BROKER=mqtt
MQTT_PORT=1883
MONGODB_URI=mongodb://mongodb:27017/agro_iot
```

### Paso 4: Verificar Estructura de Directorios

```
iot_agro_project/
├── docker-compose.yml
├── README.md
├── MANUAL_DE_USUARIO.md
├── ARQUITECTURA.md
├── backend_api/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── dashboard/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── mqtt_broker/
│   └── mosquitto.conf
├── mqtt_client/
│   ├── subscriber.py
│   ├── Dockerfile
│   └── requirements.txt
└── sensors/
    ├── sensor.py
    ├── Dockerfile
    └── requirements.txt
```

---

## Inicio del Sistema

### Opción 1: Inicio Rápido (Recomendado)

```bash
# Navega al directorio del proyecto
cd iot_agro_project

# Descarga imágenes, construye y ejecuta
docker-compose up --build

# Espera hasta ver:
# "agro_api | Running on http://0.0.0.0:5000"
# "agro_dashboard | Listening on http://0.0.0.0:8501"
```

### Opción 2: Inicio en Segundo Plano

```bash
docker-compose up -d

# Ver status de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 3: Reconstrucción Completa

```bash
# Eliminar volúmenes previos (ELIMINA DATOS)
docker-compose down -v

# Reconstruir sin cachés
docker-compose build --no-cache
docker-compose up
```

---

## Interfaz del Dashboard

### Ubicación

Accede al dashboard en: **http://localhost:8501**

### Disposición General

```
┌─────────────────────────────────────────────────────┐
│           🌾 Sistema IoT Agrícola                   │
│         Dashboard de Monitoreo Inteligente            │
├──────────┬──────────────────────────────────────────┤
│ SIDEBAR  │                                          │
├──────────┤      CONTENIDO PRINCIPAL                │
│ ⚙️ CONFIG│                                          │
│          │                                          │
│ 📅 FILTROS
│          │      TABS:                               │
│ 🔄 AUTO  │      🍅 Tomate                          │
│          │      🥕 Zanahoria                       │
└──────────┴──────────────────────────────────────────┘
```

### Componentes principales

#### 1. **Barra Lateral**

**Configuración del Sistema:**
- URL del Broker MQTT
- Patrón de Topics
- Status de Conexión
- Timestamp actual

**Opciones de Actualización:**
- Toggle de auto-actualización
- Intervalo de actualización (5-60 segundos)
- Indicador de estado

**Filtros Avanzados:**
- Rango de fechas
- Rango de temperatura
- Rango de humedad

#### 2. **Área Principal**

Contiene múltiples pestañas:

- 🍅 **Tomate**: Datos específicos del cultivo de tomate
- 🥕 **Zanahoria**: Datos específicos del cultivo de zanahoria
- 🌽 **Maíz**: Datos específicos del cultivo de maíz
- 🌍 **Análisis Global**: Vistas comparativas de todos los cultivos

---

## Funcionalidades Principales

### Pestaña Individual de Zona (Ej: Tomate)

#### 📊 Métricas Estadísticas

Muestra 6 tarjetas de información:

1. **Temperatura Promedio**: Media con mínimo
   - Rango: 0°C a 50°C
   - Delta muestra: Temperatura mínima

2. **Temperatura Máxima**: Valor pico registrado

3. **Temperatura Mínima**: Valor más bajo registrado

4. **Humedad Promedio**: Media porcentual
   - Rango: 0% a 100%
   - Delta muestra: Rango de variación

5. **Desviación Estándar de Temperatura**: Variabilidad (°C)

6. **Total de Lecturas**: Cantidad de registros capturados

#### 📈 Visualizaciones Detalladas

**Tab 1: Serie Temporal** (Gráfico principal)
- Línea roja: Temperatura a lo largo del tiempo
- Línea azul: Humedad a lo largo del tiempo (eje derecho)
- Áreas sombreadas: Relleno bajo las curvas
- Interacción: Hover para ver valores exactos

**Tab 2: Distribución**
- Histograma de Temperaturas
- Histograma de Humedad
- Muestra frecuencia de rangos de valores

**Tab 3: Correlación**
- Scatter plot: Temperatura vs Humedad
- Línea roja punteada: Tendencia
- Código de color: Gradiente de temperatura

**Tab 4: Boxplot**
- Análisis de dispersión
- Muestra: Mediana, cuartiles, outliers

#### 📋 Tabla de Datos

- **Últimos 20 registros** por zona
- Ordenados por timestamp (más reciente primero)
- Columnas:
  - `sensor_id`: Identificador único del sensor
  - `zona`: Cultivo donde está ubicado
  - `temperatura`: Valor en °C
  - `humedad`: Valor en %
  - `timestamp`: Fecha y hora de lectura
  - `topic`: Topic MQTT utilizado
  - `qos`: Nivel de Calidad de Servicio

### Pestaña Análisis Global

#### 📊 Métricas Globales

6 métricas consolidadas:

1. **Temperatura Promedio Global**: Promedio de todos los sensores
2. **Humedad Promedio Global**: Promedio de todos los sensores
3. **Total de Lecturas**: Registros en el rango seleccionado
4. **Sensores Activos**: Cantidad de sensores publicando
5. **Cultivos Monitoreados**: Número de zonas con datos
6. **QoS Promedio**: Calidad de servicio

#### 📈 Análisis Comparativo

**Tab 1: Comparativa Temporal**
- Líneas superpuestas de todos los cultivos
- Cada cultivo con color propio:
  - 🍅 Tomate: Rojo (#EF553B)
  - 🥕 Zanahoria: Naranja (#FFA629)
  - 🌽 Maíz: Dorado (#FFD700)
- Vista general de comportamiento

**Tab 2: Promedios por Zona**
- Gráfico de barras: Temperatura por cultivo
- Gráfico de barras: Humedad por cultivo
- Visualización comparativa rápida

**Tab 3: Estadísticas Generales**
- Tabla descriptiva para temperatura:
  - Count, mean, std, min, 25%, 50%, 75%, max
- Tabla descriptiva para humedad:
  - Mismos parámetros

#### 📋 Datos Completos

- **Últimos 50 registros** de todas las zonas
- Consolidado de sensores
- Formato igual a tabla individual

---

## Filtros Avanzados

### Acceso

1. Abre la barra lateral (esquina superior izquierda)
2. Expande la sección "📅 Filtros Avanzados"

### Parámetros de Filtro

#### Rango de Fechas

```
Fecha inicio: [Selector de fecha]
Fecha fin:    [Selector de fecha]
```

- **Uso**: Limita los datos a un período específico
- **Ejemplo**: Mostrar solo datos de últimos 7 días
- **Efecto**: Aplica a todas las gráficas y métricas

#### Rango de Temperatura

```
Temp. mín (°C): [Número]
Temp. máx (°C): [Número]
```

- **Rango válido**: 0°C a 50°C
- **Uso**: Filtrar lecturas dentro de un rango
- **Ejemplo**: Solo datos entre 15°C y 25°C
- **Efecto**: Excluye lecturas fuera del rango

#### Rango de Humedad

```
Humedad mín (%): [Número]
Humedad máx (%): [Número]
```

- **Rango válido**: 0% a 100%
- **Uso**: Filtrar por niveles de humedad
- **Ejemplo**: Solo datos entre 40% y 80%
- **Efecto**: Excluye lecturas fuera del rango

### Ejemplo Práctico

**Escenario**: Analizar comportamiento de temperatura en tomate los últimos 3 días entre 10°C y 28°C

**Pasos**:
1. En Filtros Avanzados, establece:
   - Fecha inicio: (Hace 3 días)
   - Fecha fin: (Hoy)
   - Temp. mín: 10
   - Temp. máx: 28
   - (Deja humedad sin filtro: 0-100)

2. La interfaz se actualiza automáticamente
3. Verás solo registros que cumplen todos los criterios

---

## API REST

### Endpoints Disponibles

#### 1. Obtener Zonas Disponibles

```http
GET /zonas
```

**Response (200 OK):**
```json
["maiz", "tomate", "zanahoria"]
```

**Uso**: Listar cultivos con datos disponibles

**Curl:**
```bash
curl http://localhost:5000/zonas
```

**PowerShell:**
```powershell
Invoke-WebRequest http://localhost:5000/zonas | ConvertFrom-Json
```

---

#### 2. Obtener Todos los Logs

```http
GET /logs
```

**Response (200 OK):**
```json
[
  {
    "sensor_id": 1,
    "zona": "tomate",
    "temperatura": 24.5,
    "humedad": 65.3,
    "timestamp": "2024-04-18T10:30:45.123456",
    "topic": "campo/tomate/sensores",
    "qos": 1,
    "_id": "ObjectId(...)"
  },
  ...
]
```

**Parámetros**: Ninguno
**Límite**: Últimos 20 registros

**Curl:**
```bash
curl http://localhost:5000/logs | jq
```

---

#### 3. Obtener Logs de Zona Específica

```http
GET /logs/<zona>
```

**Path Parameters:**
- `<zona>`: Nombre del cultivo (tomate, zanahoria, maiz)

**Response (200 OK):**
```json
[
  {
    "sensor_id": 2,
    "zona": "zanahoria",
    "temperatura": 18.2,
    "humedad": 72.1,
    "timestamp": "2024-04-18T10:30:45.123456",
    "topic": "campo/zanahoria/sensores",
    "qos": 1
  },
  ...
]
```

**Ejemplos:**
```bash
# Logs de tomate
curl http://localhost:5000/logs/tomate

# Logs de zanahoria
curl http://localhost:5000/logs/zanahoria

# Logs de maíz
curl http://localhost:5000/logs/maiz
```

**PowerShell:**
```powershell
$tomate = Invoke-WebRequest http://localhost:5000/logs/tomate | ConvertFrom-Json
$tomate | ForEach-Object { Write-Host "$_.zona: T=$_.temperatura°C, H=$_.humedad%" }
```

---

### Integración con Sistemas Externos

#### Ejemplo: Python

```python
import requests

# Obtener zonas
response = requests.get("http://localhost:5000/zonas")
zonas = response.json()

# Obtener logs de una zona
response = requests.get("http://localhost:5000/logs/tomate")
data = response.json()

# Procesar datos
for record in data:
    print(f"{record['zona']}: {record['temperatura']}°C, {record['humedad']}%")
```

#### Ejemplo: Node.js

```javascript
const fetch = require('node-fetch');

async function getData() {
  // Obtener zonas
  const zonas = await fetch('http://localhost:5000/zonas')
    .then(res => res.json());
  
  // Obtener logs
  const logs = await fetch('http://localhost:5000/logs')
    .then(res => res.json());
  
  return { zonas, logs };
}
```

---

## Solución de Problemas

### Problema 1: Dashboard no accesible

**Síntomas**: "Connection refused" al acceder a http://localhost:8501

**Soluciones**:

1. Verificar que el contenedor está ejecutándose:
```bash
docker-compose ps
# Buscar: agro_dashboard ... Up
```

2. Ver logs del dashboard:
```bash
docker-compose logs dashboard
# Buscar errores de inicio
```

3. Reiniciar el servicio:
```bash
docker-compose restart dashboard
```

4. Verificar puerto:
```bash
# Windows/Bash
netstat -an | grep 8501

# Linux
lsof -i :8501
```

---

### Problema 2: Sin datos en el dashboard

**Síntomas**: "No hay zonas disponibles" o tablas vacías

**Causa probable**: Los sensores no están publicando datos

**Soluciones**:

1. Verificar estado de sensores:
```bash
docker-compose ps | grep sensor
# Todos deben estar "Up"
```

2. Ver logs del MQTT broker:
```bash
docker-compose logs mqtt
# Buscar: "Connected clients" o "Received PUBLISH"
```

3. Ver logs del subscriber:
```bash
docker-compose logs subscriber
# Verificar que se reciben mensajes
```

4. Ver logs de la API:
```bash
docker-compose logs api
# Verificar que MongoDB está conectada
```

---

### Problema 3: Sensor muestra datos antiguos

**Síntomas**: Timestamps muy antiguos en tabla

**Causas**:

1. Reloj del sistema desincronizado
2. Sensores no se reinician correctamente
3. Datos históricos sin limpiar

**Soluciones**:

```bash
# Limpiar datos (CUIDADO: elimina historial)
docker-compose down -v  # -v elimina volúmenes
docker-compose up --build
```

---

### Problema 4: API retorna error 500

**Síntomas**: Respuesta HTTP 500 en endpoint

**Soluciones**:

1. Verificar conexión a MongoDB:
```bash
docker-compose logs api | grep "MongoDB"
docker-compose logs mongodb
```

2. Verificar datos en MongoDB:
```bash
docker-compose exec mongodb mongosh agro_iot
> db.lecturas.count()  # Debe ser > 0
```

3. Reiniciar API:
```bash
docker-compose restart api
```

---

### Problema 5: Filtros no funcionan

**Síntomas**: Cambios en filtros no producen efecto

**Soluciones**:

1. Refrescar página:
   - Ctrl+F5 (Windows)
   - Cmd+Shift+R (Mac)

2. Limpiar cachés de Streamlit:
```bash
rm -rf ~/.streamlit
# Reiniciar dashboard
docker-compose restart dashboard
```

3. Verificar que hay datos en el rango:
```bash
curl http://localhost:5000/logs | jq length
# Debe ser > 0
```

---

## Mantenimiento

### Limpieza Regular

#### Limpieza de datos diaria

Los datos se retienen indefinidamente. Para mantener la base de datos manejable:

```bash
# Conectar a MongoDB
docker-compose exec mongodb mongosh agro_iot

# Ver tamaño de colección
> db.lecturas.stats()

# Eliminar datos más antiguos de 30 días
> db.lecturas.deleteMany({
    timestamp: { 
      $lt: new Date(Date.now() - 30*24*60*60*1000) 
    }
  })
```

#### Limpieza de logs de Docker

```bash
# Ver uso de espacio
docker system df

# Limpiar logs viejo (7 días)
# Editar /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}

# Reiniciar Docker
sudo systemctl restart docker
```

### Respaldo de Datos

#### Exportar datos a JSON

```bash
# Conectar a MongoDB
docker-compose exec mongodb mongosh agro_iot

# Exportar collection
> db.lecturas.find().toArray()
```

#### Backup automático

```bash
#!/bin/bash
# backup.sh
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker-compose exec mongodb mongodump --db agro_iot --out backup_$TIMESTAMP
tar czf backup_$TIMESTAMP.tar.gz backup_$TIMESTAMP/
rm -rf backup_$TIMESTAMP/
```

### Actualizaciones

#### Actualizar imágenes

```bash
# Descargar versiones nuevas
docker-compose pull

# Reconstruir
docker-compose build --pull

# Aplicar cambios
docker-compose up -d
```

### Monitoreo Continuo

#### Verificación de salud

```bash
#!/bin/bash
# health-check.sh

# Verificar servicios
docker-compose ps | grep -v "Up" && echo "⚠️ Servicios caídos"

# Verificar API
curl -s http://localhost:5000/zonas > /dev/null && echo "✓ API OK" || echo "✗ API FAILED"

# Verificar Dashboard
curl -s http://localhost:8501/_stcore/health > /dev/null && echo "✓ Dashboard OK" || echo "✗ Dashboard FAILED"

# Verificar MongoDB
docker-compose exec mongodb mongosh agro_iot --eval "db.adminCommand('ping')" > /dev/null 2>&1 && echo "✓ MongoDB OK" || echo "✗ MongoDB FAILED"
```

---

## Soporte y Contacto

Para problemas adicionales:

1. Revisa los logs: `docker-compose logs -f`
2. Verifica la arquitectura: Ver [ARQUITECTURA.md](ARQUITECTURA.md)
3. Consulta el [README.md](README.md) para detalles técnicos

---

**Última actualización**: Abril 2024
**Versión**: 1.0.0
