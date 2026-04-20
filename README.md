# Sistema IoT Agrícola

Sistema completo de monitoreo agrícola con MQTT, API REST y Dashboard Streamlit.

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
