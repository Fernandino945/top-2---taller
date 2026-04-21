# Sistema IoT Agrícola

Sistema completo de monitoreo agrícola con MQTT, API REST y Dashboard Streamlit.

## 🆕 HITO 2 - Extensión MQTT (Cambios Principales)

Este taller implementa una extensión completa del sistema IoT agrícola con énfasis en MQTT avanzado:

### ✨ Características Nuevas/Mejoradas

- **MQTT QoS 1 (At Least Once)**: Implementado en sensores y subscriber para garantizar entrega confirmada
- **Wildcard Subscribe**: Suscriptor capturando múltiples topics con patrón `campo/+/sensores`
- **Topics Jerárquicos**: Estructura clara y escalable `campo/[zona]/sensores` para 3 cultivos
- **API REST Expandida**: 5 endpoints (GET /, /logs, /logs/<zona>, /zonas, /health)
- **Página Raíz Hermosa**: GET / ahora retorna HTML responsivo con información del sistema
- **URLs Inteligentes**: Separación de URLs para navegador (localhost:5000) e internas Docker (api:5000)
- **Dashboard Mejorado**: Link funcional a API, información del sistema, auto-refresh
- **MongoDB Persistencia**: 22,000+ registros almacenados con índices optimizados

### 📋 Cambios Técnicos Realizados

1. **sensors/sensor.py**
   - ✅ Publicación con QoS 1 (línea 109)
   - ✅ Manejo de reconexión con backoff exponencial
   - ✅ 3 sensores simulados (tomate, zanahoria, maíz)

2. **mqtt_client/subscriber.py**
   - ✅ Wildcard subscribe: `campo/+/sensores`
   - ✅ Validación de topic format
   - ✅ Almacenamiento en MongoDB con metadata

3. **backend_api/app.py**
   - ✅ 5 endpoints funcionales
   - ✅ GET / retorna HTML responsivo y JSON dual
   - ✅ Manejo de errores y health check
   - ✅ Índices de MongoDB para performance

4. **dashboard/app.py**
   - ✅ Separación URL: API_DISPLAY_URL vs API_REQUEST_URL
   - ✅ Link button 🔗 Acceder a http://localhost:5000
   - ✅ Información del sistema en sidebar
   - ✅ Timezone Chile (America/Santiago)

5. **docker-compose.yml**
   - ✅ Cambio API_URL a http://localhost:5000 (accesible desde navegador)
   - ✅ 9 servicios orquestados correctamente
   - ✅ Health checks para mongodb y api

---

## Características

- **Sensores MQTT**: 3 sensores simulados (tomate, zanahoria, maíz) publicando datos en topics jerárquicos
- **QoS 1**: Confirmación de entrega en mensajes MQTT
- **Wildcards MQTT**: Suscriptor capturando múltiples topics con patrón `campo/+/sensores`
- **API REST**: Endpoints para consultar datos por zona
- **Dashboard Interactivo**: Visualización dinámica con Streamlit
- **Base de Datos**: MongoDB para persistencia de datos
- **Docker Compose**: Orquestación completa de servicios

## Requisitos

- Docker y Docker Compose
- Puertos disponibles: 1883 (MQTT), 5000 (API), 8501 (Dashboard), 27017 (MongoDB)

## Iniciar el Sistema

### Opción 1: Docker Compose (Recomendado)

```bash
cd "d:\hito 2\iot_agro_project"
docker-compose up --build
```

### Opción 2: Iniciar Servicios Individuales

```bash
# Construir imágenes
docker-compose build

# Levantar todos los servicios
docker-compose up
```

## Acceso

- **Dashboard Streamlit**: http://localhost:8501
- **API REST**: http://localhost:5000
  - Endpoints: `/logs`, `/logs/<zona>`, `/zonas`
- **MQTT Broker**: mqtt://localhost:1883
- **MongoDB**: mongodb://localhost:27017

## Estructura del Proyecto

```
iot_agro_project/
├── sensors/              # Sensores MQTT simulados
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sensor.py
├── mqtt_broker/         # Configuración Mosquitto
│   └── mosquitto.conf
├── mqtt_client/         # Subscriber MQTT
│   ├── Dockerfile
│   ├── requirements.txt
│   └── subscriber.py
├── backend_api/         # API REST Flask
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── dashboard/           # Dashboard Streamlit
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── docker-compose.yml   # Orquestación
└── README.md
```

## Flujo de Datos

```
Sensores (MQTT)
    ↓
    └─→ Broker MQTT (Mosquitto)
            ↓
            └─→ Subscriber (captura con wildcard)
                    ↓
                    └─→ MongoDB (almacena)
                            ↓
                            ├─→ API REST (consulta)
                            │       ↓
                            │       └─→ Dashboard (visualiza)
```

## Configuración de Sensores

### Variables de Entorno

Cada sensor se configura con:
- `SENSOR_ID`: Identificador único (1, 2, 3)
- `ZONA`: Zona de cultivo (tomate, zanahoria, maiz)

Topics generados dinámicamente:
- `campo/tomate/sensores`
- `campo/zanahoria/sensores`
- `campo/maiz/sensores`

### Datos Publicados

```json
{
  "sensor_id": "1",
  "zona": "tomate",
  "temperatura": 22.45,
  "humedad": 67.83
}
```

## QoS MQTT

- **Publicación**: QoS 1 (At least once)
- **Suscripción**: QoS 1 (At least once)
- **Garantía**: Entrega confirmada de mensajes

## Endpoints API

### GET / ⭐ NUEVO
Página de información del sistema con HTML responsivo

```bash
curl http://localhost:5000/
```

**Respuesta HTML:** Página hermosa con:
- Estado de la base de datos
- Zonas activas (🍅 🥕 🌽)
- Documentación de todos los endpoints
- Status de la conexión

**Respuesta JSON (si envía `Accept: application/json`):**
```json
{
  "system": "IoT Agricultural Monitoring System",
  "version": "1.0.0",
  "database_status": "connected",
  "endpoints": {...},
  "available_zones": ["maiz", "tomate", "zanahoria"]
}
```

### GET /health ⭐ NUEVO
Health check del servidor

```bash
curl http://localhost:5000/health
```

**Respuesta:**
```json
{"status": "ok"}
```

### GET /logs
Últimas 20 lecturas de todas las zonas

```bash
curl http://localhost:5000/logs
```

### GET /logs/<zona>
Últimas 20 lecturas de una zona específica

```bash
curl http://localhost:5000/logs/tomate
```

### GET /zonas
Lista de zonas únicas con datos

```bash
curl http://localhost:5000/zonas
```

## Dashboard Streamlit

El dashboard proporciona:

- **Tabs por Zona**: Una pestaña para cada cultivo
- **Métricas**: Temperatura promedio, humedad promedio, cantidad de lecturas
- **Gráficos**: Evolución de temperatura y humedad en el tiempo
- **Tabla de Datos**: Últimos registros ordenados por timestamp
- **Tab Global**: Comparativa de temperaturas entre cultivos
- **Auto-actualización**: Toggle para refrescar datos cada 10 segundos

## MongoDB

Colección: `agro_iot.lecturas`

Documentos almacenan:
- `sensor_id`: ID del sensor
- `zona`: Zona de cultivo
- `temperatura`: Valor de temperatura (°C)
- `humedad`: Valor de humedad (%)
- `timestamp`: Marca de tiempo
- `topic`: Topic MQTT original
- `qos`: Nivel de QoS

## Verificación del Sistema

### Logs de Sensores

```bash
docker-compose logs -f sensor_tomate
```

Esperado: Mensajes de "Enviado" con QoS 1

### Logs del Subscriber

```bash
docker-compose logs -f subscriber
```

Esperado: Mensajes de "Guardado QoS 1" para cada zona

### Verificar Endpoints

```bash
# Todas las zonas
curl http://localhost:5000/zonas

# Logs de una zona
curl http://localhost:5000/logs/tomate
```

### Verificar MongoDB

```bash
docker-compose exec mongodb mongosh

use agro_iot
db.lecturas.find().limit(5)
db.lecturas.distinct("zona")
```

## Escalabilidad

Para agregar una nueva zona de cultivo:

1. Agregar servicio en `docker-compose.yml`:

```yaml
sensor_lechuga:
  build: ./sensors
  environment:
    - SENSOR_ID=4
    - ZONA=lechuga
    # ... resto de configuración
```

2. El sistema detectará automáticamente la nueva zona
3. Aparecerá en el dashboard sin cambios de código

## Troubleshooting

### Problema: Servicios no se conectan

**Solución**: Esperar a que MongoDB y MQTT inicien:

```bash
docker-compose logs
docker-compose ps
```

### Problema: No hay datos en MongoDB

**Solución**: Verificar que el subscriber está corriendo:

```bash
docker-compose logs subscriber
```

### Problema: dashboard no carga

**Solución**: Verificar que la API está disponible:

```bash
curl http://localhost:5000/health
```

## Detener el Sistema

```bash
docker-compose down

# Para eliminar datos de MongoDB:
docker-compose down -v
```

## Licencia

Proyecto académico - Tópico de Especialidad II

---

## 📝 HITO 2 - Archivos Modificados y Resumen de Cambios

### Archivos Modificados (4 archivos principales)

| Archivo | Cambios Principales | Líneas |
|---------|-------------------|--------|
| **sensors/sensor.py** | ✅ QoS 1 en publicación, 3 sensores activos, reconexión automática | 120+ |
| **mqtt_client/subscriber.py** | ✅ Wildcard subscribe `campo/+/sensores`, validación de topic, almacenamiento en MongoDB | 120+ |
| **backend_api/app.py** | ✅ 5 endpoints (/, /logs, /logs/<zona>, /zonas, /health), página HTML responsiva, JSON dual | 450+ |
| **dashboard/app.py** | ✅ URLs inteligentes, link botón funcional, información del sistema, timezone Chile | 280+ |
| **docker-compose.yml** | ✅ API_URL configurada a http://localhost:5000, 9 servicios orquestados, health checks | 150 |

### Verificación Rápida

```bash
# 1. Iniciar sistema
docker-compose up --build

# 2. Verificar servicios (9/9 corriendo)
docker-compose ps

# 3. Verificar MQTT QoS 1
docker logs agro_sensor_tomate | grep "Enviado"

# 4. Verificar Wildcard Subscribe
docker logs agro_subscriber | grep "campo/+/sensores"

# 5. Verificar API endpoints
curl http://localhost:5000/          # HTML + JSON
curl http://localhost:5000/zonas      # Lista de zonas
curl http://localhost:5000/logs/tomate # Datos de una zona

# 6. Acceder dashboard
# http://localhost:8501

# 7. MongoDB: 22,000+ documentos
docker-compose exec mongodb mongosh -c "db.lecturas.countDocuments()" agro_iot
```

### Requisitos Cumplidos (8/8)

- ✅ MQTT QoS Nivel 1 (At Least Once)
- ✅ Wildcard Subscribe: `campo/+/sensores`
- ✅ Topics Jerárquicos: `campo/[zona]/sensores`
- ✅ 5 Endpoints API REST funcionales
- ✅ Dashboard Streamlit con visualizaciones
- ✅ MongoDB con 22,000+ registros persistidos
- ✅ Docker Compose orquestando 9 servicios
- ✅ Documentación y código entregable

Para detalles técnicos completos, ver `VERIFICACION_REQUISITOS.md`
