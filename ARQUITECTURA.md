# Arquitectura del Sistema IoT Agrícola

## 📐 Diagrama General de Componentes

```
┌─────────────────────────────────────────────────────────────────┐
│                      SISTEMA IOT AGRÍCOLA                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│   SENSORES MQTT      │         │   MQTT BROKER        │
├──────────────────────┤         ├──────────────────────┤
│ 🍅 Sensor Tomate     │         │ Mosquitto 2.0        │
│    - Temp/Humedad    │ MQTT    │ Puerto: 1883         │
│    - QoS 1           │◄───────►│ Persistencia: ON     │
│                      │         │                      │
│ 🥕 Sensor Zanahoria  │         │                      │
│ 🌽 Sensor Maíz       │         │                      │
└──────────────────────┘         └──────────────────────┘
         │                                │
         │                                │
         │        ┌──────────────────────┐
         │        │  MQTT SUBSCRIBER     │
         │        ├──────────────────────┤
         │        │ Python Client        │
         │        │ QoS 1, Wildcard      │
         │        │ Pattern: campo/+/... │
         │        └──────────────────────┘
         │                │
         │                │ Inserción de datos
         │                ▼
         │        ┌──────────────────────┐
         │        │   MONGODB            │
         │        ├──────────────────────┤
         │        │ Database: agro_iot   │
         │        │ Collection: lecturas │
         │        │ Port: 27017          │
         │        │ (Volumen: mongodb_data)
         │        └──────────────────────┘
         │                │
         │                │ Consultas
         │                ▼
         │        ┌──────────────────────┐
         │        │  REST API (Flask)    │
         │        ├──────────────────────┤
         │        │ GET /zonas           │
         │        │ GET /logs            │
         │        │ GET /logs/<zona>     │
         │        │ Port: 5000           │
         │        └──────────────────────┘
         │                │
         │                │ HTTP
         │                ▼
         └───────►┌──────────────────────┐
                  │  STREAMLIT DASHBOARD │
                  ├──────────────────────┤
                  │ - Métricas           │
                  │ - Gráficos           │
                  │ - Tablas             │
                  │ - Filtros Avanzados  │
                  │ Port: 8501           │
                  └──────────────────────┘
                         │
                         │ Navegador Web
                         ▼
                  ┌──────────────────────┐
                  │   USUARIO (Local)    │
                  │ http://localhost:8501│
                  └──────────────────────┘
```

---

## 🔄 Flujo de Datos

### 1. Publicación de Datos (Sensores → MQTT)

```
┌─────────────────────────────────────────────────────────┐
│                 SENSOR_TOMATE                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Leer sensores hardware DHT22, etc.             │ │
│  │    - temperatura: 22.5°C                          │ │
│  │    - humedad: 65.3%                               │ │
│  │    - timestamp: 2024-04-18T10:30:45               │ │
│  │                                                     │ │
│  │ 2. Serializar a JSON                              │ │
│  │    {                                               │ │
│  │      "sensor_id": 1,                              │ │
│  │      "temperatura": 22.5,                         │ │
│  │      "humedad": 65.3,                             │ │
│  │      "timestamp": "2024-04-18T10:30:45"           │ │
│  │    }                                               │ │
│  │                                                     │ │
│  │ 3. Publicar a MQTT                                │ │
│  │    Topic: campo/tomate/sensores                   │ │
│  │    QoS: 1 (At least once)                         │ │
│  │    Retainada: No                                  │ │
│  │                                                     │ │
│  │ 4. Intervalo: Cada 10-30 segundos                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         │ MQTT Publish
         │ QoS 1
         ▼
┌─────────────────────────────────────────────────────────┐
│            MQTT BROKER (Mosquitto)                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Tópico: campo/tomate/sensores                     │ │
│  │ Mensaje guardado en memoria y persistencia        │ │
│  │ Busca suscriptores: campo/# y campo/+/sensores  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         │ Entrega a suscriptor
         │ (garantizada QoS 1)
         ▼
```

### 2. Almacenamiento (MQTT → BD)

```
┌─────────────────────────────────────────────────────────┐
│          MQTT SUBSCRIBER (Python)                       │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Suscriptor activo a: campo/+/sensores wildcard │ │
│  │                                                     │ │
│  │ 2. Recibe mensaje MQTT:                           │ │
│  │    Topic: campo/tomate/sensores                   │ │
│  │    Payload: {...datos...}                         │ │
│  │    QoS: 1                                         │ │
│  │                                                     │ │
│  │ 3. Extrae zona del topic:                         │ │
│  │    partes = topic.split("/")                      │ │
│  │    zona = partes[1]  # "tomate"                   │ │
│  │                                                     │ │
│  │ 4. Enriquece documento:                           │ │
│  │    documento = {                                  │ │
│  │      ...payload...,                              │ │
│  │      "zona": "tomate",                           │ │
│  │      "topic": topic,                             │ │
│  │      "qos": 1                                    │ │
│  │    }                                              │ │
│  │                                                     │ │
│  │ 5. Inserta en MongoDB:                            │ │
│  │    coleccion.insert_one(documento)                │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         │ Conexión PyMongo
         │ mongodb://mongodb:27017
         ▼
┌─────────────────────────────────────────────────────────┐
│              MONGODB                                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Database: agro_iot                                 │ │
│  │                                                     │ │
│  │ Collection: lecturas                              │ │
│  │  {                                                 │ │
│  │    "_id": ObjectId(...),                          │ │
│  │    "sensor_id": 1,                                │ │
│  │    "zona": "tomate",                             │ │
│  │    "temperatura": 22.5,                          │ │
│  │    "humedad": 65.3,                              │ │
│  │    "timestamp": ISODate(...),                     │ │
│  │    "topic": "campo/tomate/sensores",            │ │
│  │    "qos": 1                                      │ │
│  │  }                                                 │ │
│  └────────────────────────────────────────────────────┘ │
│  Índices:                                                │
│  - timestamp                                             │
│  - zona                                                  │
│  - sensor_id                                             │
└─────────────────────────────────────────────────────────┘
```

### 3. Consulta (API → Frontend)

```
┌─────────────────────────────────────────────────────────┐
│         STREAMLIT DASHBOARD                              │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Página carga                                    │ │
│  │                                                     │ │
│  │ 2. Ejecuta: requests.get("/zonas")                 │ │
│  │    Obtiene lista de cultivos disponibles          │ │
│  │                                                     │ │
│  │ 3. Para cada zona, ejecuta:                        │ │
│  │    requests.get("/logs/tomate")                   │ │
│  │    Obtiene últimos 20 registros                   │ │
│  │                                                     │ │
│  │ 4. Renderiza:                                      │ │
│  │    - Métricas con st.metric()                     │ │
│  │    - Gráficos con plotly                         │ │
│  │    - Tablas con st.dataframe()                    │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         │ HTTP GET
         │ (puerto 5000)
         ▼
┌─────────────────────────────────────────────────────────┐
│          FLASK REST API                                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Endpoint: GET /zonas                              │ │
│  │                                                     │ │
│  │ def get_zonas():                                  │ │
│  │   resultado = coleccion.distinct("zona")          │ │
│  │   return jsonify(resultado)                       │ │
│  │                                                     │ │
│  │ Response:                                          │ │
│  │ ["maiz", "tomate", "zanahoria"]                  │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Endpoint: GET /logs/<zona>                        │ │
│  │                                                     │ │
│  │ def get_logs(zona):                               │ │
│  │   registros = coleccion.find(                     │ │
│  │     {"zona": zona}                                │ │
│  │   ).sort("timestamp", -1).limit(20)              │ │
│  │   return jsonify(list(registros))                 │ │
│  │                                                     │ │
│  │ Response:                                          │ │
│  │ [                                                  │ │
│  │   {                                                │ │
│  │     "sensor_id": 1,                              │ │
│  │     "zona": "tomate",                            │ │
│  │     "temperatura": 22.5,                         │ │
│  │     ...                                            │ │
│  │   },                                               │ │
│  │   ...                                              │ │
│  │ ]                                                  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
         │
         │ Query MongoDB
         │ (conexión PyMongo)
         ▼
┌─────────────────────────────────────────────────────────┐
│              MONGODB (lectura)                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Consulta la colección                          │ │
│  │    db.lecturas.find({"zona": "tomate"})          │ │
│  │                                                     │ │
│  │ 2. Ordena por timestamp descendente               │ │
│  │    .sort({timestamp: -1})                         │ │
│  │                                                     │ │
│  │ 3. Limita a 20 documentos                         │ │
│  │    .limit(20)                                     │ │
│  │                                                     │ │
│  │ 4. Retorna cursor que API serializa a JSON        │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Arquitectura de Capas

```
┌──────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                  │
│  ┌──────────────────────────────────────────────────────┐│
│  │ Streamlit Dashboard (Puerto 8501)                    ││
│  │ - Interfaz Web Interactiva                          ││
│  │ - Gráficos Plotly                                    ││
│  │ - Tablas y Métricas                                 ││
│  │ - Filtros Avanzados                                 ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
                          ▲
                          │ HTTP GET
                          │
┌──────────────────────────────────────────────────────────┐
│                   CAPA DE INTEGRACIÓN                    │
│  ┌──────────────────────────────────────────────────────┐│
│  │ Flask REST API (Puerto 5000)                         ││
│  │ - Endpoint /zonas                                    ││
│  │ - Endpoint /logs                                     ││
│  │ - Endpoint /logs/<zona>                             ││
│  │ - Serialización JSON                                ││
│  │ - Manejo de errores HTTP                            ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
                          ▲
                          │ Conexión PyMongo
                          │
┌──────────────────────────────────────────────────────────┐
│                    CAPA DE DATOS                         │
│  ┌──────────────────────────────────────────────────────┐│
│  │ MongoDB (Puerto 27017)                               ││
│  │ - Base de datos: agro_iot                           ││
│  │ - Colección: lecturas                               ││
│  │ - Índices: timestamp, zona, sensor_id               ││
│  │ - Persistencia: Volumen Docker                      ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
                          ▲
                          │ Inserción PyMongo
                          │
┌──────────────────────────────────────────────────────────┐
│                 CAPA DE PROCESAMIENTO                    │
│  ┌──────────────────────────────────────────────────────┐│
│  │ MQTT Subscriber (Python)                             ││
│  │ - Suscripción MQTT: campo/+/sensores               ││
│  │ - QoS 1                                              ││
│  │ - Enriquecimiento de datos                          ││
│  │ - Transformación: MQTT → MongoDB                    ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
                          ▲
                          │ MQTT Subscribe
                          │
┌──────────────────────────────────────────────────────────┐
│                  CAPA DE MENSAJERÍA                      │
│  ┌──────────────────────────────────────────────────────┐│
│  │ MQTT Broker - Mosquitto (Puerto 1883)               ││
│  │ - Tema principal: campo/                            ││
│  │ - Pattern: campo/<zona>/sensores                    ││
│  │ - QoS: 0, 1, 2 soportados                          ││
│  │ - Persistencia: ON                                  ││
│  │ - Max clients: Ilimitado                            ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
                          ▲
                          │ MQTT Publish
                          │
┌──────────────────────────────────────────────────────────┐
│                   CAPA DE SENSORES                       │
│  ┌──────────────────────────────────────────────────────┐│
│  │ Sensores IoT (Paho MQTT Python)                      ││
│  │                                                       ││
│  │ 🍅 Sensor Tomate (sensor_id: 1)                     ││
│  │    - Ubicación: invernadero_1                       ││
│  │    - Pub cada 15s a campo/tomate/sensores          ││
│  │    - QoS: 1                                          ││
│  │                                                       ││
│  │ 🥕 Sensor Zanahoria (sensor_id: 2)                  ││
│  │    - Ubicación: campo_2                             ││
│  │    - Pub cada 15s a campo/zanahoria/sensores       ││
│  │    - QoS: 1                                          ││
│  │                                                       ││
│  │ 🌽 Sensor Maíz (sensor_id: 3)                       ││
│  │    - Ubicación: campo_3                             ││
│  │    - Pub cada 15s a campo/maiz/sensores            ││
│  │    - QoS: 1                                          ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

---

## 🐳 Topología Docker

```
┌────────────────────────────────────────────────────────┐
│                  Docker Compose Network                │
│               (agro_network - bridge)                  │
│                                                        │
│  ┌──────────────┐    ┌──────────────┐                │
│  │  agro_mqtt   │    │ agro_sensor  │                │
│  │   mosquitto  │◄──►│    tomate    │                │
│  │  :1883       │    │  (Python)    │                │
│  └──────────────┘    └──────────────┘                │
│         ▲                     
│         │                 ┌──────────────┐            │
│         │                 │ agro_sensor  │            │
│         │            ◄───►│    zanahoria │            │
│         │                 │  (Python)    │            │
│         │                 └──────────────┘            │
│         │
│         │                 ┌──────────────┐            │
│         │                 │  agro_sensor │            │
│         └────────────────►│     maiz     │            │
│                          │  (Python)    │            │
│                          └──────────────┘            │
│                                                        │
│  ┌──────────────────┐                                 │
│  │  agro_subscriber │                                 │
│  │   (Python)       │                                 │
│  │  - MQTT Sub      │◄────────┐                      │
│  │  - MongoDB Pub   │         │                      │
│  └──────────────────┘         │                      │
│         │                      │                      │
│         │ conn: mongodb:27017  │                      │
│         │                      │                      │
│  ┌──────▼──┐          ┌────────┴────┐               │
│  │   api   │          │  mongodb    │               │
│  │ Flask   │          │  :27017     │               │
│  │ :5000   │          │ [lecturas]  │               │
│  └────┬────┘          └─────────────┘               │
│       │                                              │
│       │                                              │
│  ┌────▼──────────┐                                  │
│  │   dashboard   │                                  │
│  │  Streamlit    │                                  │
│  │  :8501        │                                  │
│  └───────────────┘                                  │
│                                                        │
└────────────────────────────────────────────────────────┘
         ▲
         │ http://localhost:8501
         │
    ┌────┴─────────┐
    │   USUARIO    │
    │   Navegador  │
    │   Local      │
    └──────────────┘
```

### Servicios y Puertos

| Servicio | Contenedor | Puerto Interno | Puerto Externo | Protocolo | Rol |
|----------|-----------|----------------|----------------|-----------|-----|
| MQTT Broker | agro_mqtt | 1883 | 1883 | MQTT | Mensajería |
| Sensor Tomate | agro_sensor_tomate | - | - | MQTT | Ingesta |
| Sensor Zanahoria | agro_sensor_zanahoria | - | - | MQTT | Ingesta |
| Sensor Maíz | agro_sensor_maiz | - | - | MQTT | Ingesta |
| Subscriber | agro_subscriber | - | - | MQTT+MongoDB | Procesamiento |
| MongoDB | agro_mongodb | 27017 | 27017 | MongoDB | Almacenamiento |
| API REST | agro_api | 5000 | 5000 | HTTP | Integración |
| Dashboard | agro_dashboard | 8501 | 8501 | HTTP | Presentación |

---

## 🔌 Esquema de Tópicos MQTT

### Estructura Jerárquica

```
campo/                          (Nivel raíz)
├── tomate/
│   └── sensores               (Topic de publicación)
├── zanahoria/
│   └── sensores
├── maiz/
│   └── sensores
└── (otros cultivos en futuro)
```

### Expresiones de Suscripción

```
campo/+/sensores              (Wildcard: captura todas las zonas)
campo/tomate/#                (Captura todo bajo tomate)
campo/tomate/sensores         (Específico: solo tomate)
field/#                       (Captura todo - NO RECOMENDADO)
```

### Formato de Payload MQTT

```json
{
  "sensor_id": 1,
  "temperatura": 22.5,
  "humedad": 65.3,
  "timestamp": "2024-04-18T10:30:45.123456"
}
```

**Tamaño**: ~80-100 bytes
**Frecuencia**: Cada 15-30 segundos por sensor
**QoS**: 1 (At Least Once)
**Retainado**: No

---

## 📊 Esquema de Base de Datos MongoDB

### Colección: `lecturas`

```javascript
{
  "_id": ObjectId("660861a1b4c9d7e1f2a3b4c5"),
  "sensor_id": 1,
  "zona": "tomate",
  "temperatura": 22.5,
  "humedad": 65.3,
  "timestamp": ISODate("2024-04-18T10:30:45.123Z"),
  "topic": "campo/tomate/sensores",
  "qos": 1
}
```

### Índices

```javascript
// Índice por timestamp (para consultas ordenadas)
db.lecturas.createIndex({ "timestamp": -1 })

// Índice por zona (para filtros por cultivo)
db.lecturas.createIndex({ "zona": 1 })

// Índice por sensor_id (para identificar sensores)
db.lecturas.createIndex({ "sensor_id": 1 })

// Índice compuesto (para búsquedas complejas)
db.lecturas.createIndex({ "zona": 1, "timestamp": -1 })
```

### Ejemplos de Consultas

```javascript
// Últimas 20 lecturas de tomate
db.lecturas.find({ "zona": "tomate" })
   .sort({ "timestamp": -1 })
   .limit(20)

// Datos de últimas 24 horas
db.lecturas.find({
  "timestamp": { 
    $gte: new Date(Date.now() - 24*60*60*1000) 
  }
})

// Temperatura promedio por zona
db.lecturas.aggregate([
  {
    $group: {
      _id: "$zona",
      temp_prom: { $avg: "$temperatura" },
      humedad_prom: { $avg: "$humedad" },
      count: { $sum: 1 }
    }
  }
])

// Estadísticas de un sensor
db.lecturas.find({ "sensor_id": 1 }).explain("executionStats")
```

---

## 🔄 Ciclo de Vida de un Dato

```
1. GENERACIÓN (Sensor)
   ┌──────────────────┐
   │ leo_temperatura() │  Lee sensor DHT22
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ crear_payload()  │  Serializa a JSON
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ tiempo_espera()  │  Aguarda 15 segundos
   └────────┬─────────┘

2. TRANSMISIÓN (Red MQTT)
            │
            ▼
   ┌──────────────────┐
   │   mqtt_publish   │  Publica a MQTT
   │  Topic: campo/.. │
   │  QoS: 1          │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ MQTT Broker      │  Broker recibe
   │ (Mosquitto)      │  Encola el mensaje
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Busca            │  Campo/+/sensores
   │ suscriptores     │  encaja el subscriber
   └────────┬─────────┘

3. PROCESAMIENTO (Subscriber)
            │
            ▼
   ┌──────────────────┐
   │  on_message()    │  Callback triggered
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  extrae_zona()   │  Obtiene zona del topic
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ enriquece_doc()  │  Añade metadata
   └────────┬─────────┘

4. ALMACENAMIENTO (MongoDB)
            │
            ▼
   ┌──────────────────┐
   │  insert_one()    │  Inserta en BD
   │  coleccion       │  (con índices)
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  lectura_ok()    │  Confirmación ACK
   └────────┬─────────┘

5. CONSULTA (API)
            │
            ▼
   ┌──────────────────┐
   │  GET /logs/<z>   │  Request HTTP
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  find(zona)      │  Query MongoDB
   │  .sort.limit()   │  Últimos 20
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  jsonify()       │  Serializa JSON
   └────────┬─────────┘

6. PRESENTACIÓN (Frontend)
            │
            ▼
   ┌──────────────────┐
   │ fetch() en JS    │  Descarga datos
   │ requests Python  │
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ DataFrame pandas │  Procesa datos
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │ Plotly graph()   │  Crea gráficos
   │ st.metric()      │  Calcula métricas
   │ st.dataframe()   │  Renderiza tabla
   └────────┬─────────┘
            │
            ▼
   ┌──────────────────┐
   │  USUARIO VISUALIZA EL DATO
   │  Toma decisiones basadas en datos
   └──────────────────┘
```

---

## 🛡️ Características de Confiabilidad

### QoS MQTT (Quality of Service)

El sistema implementa **QoS 1 - At Least Once**:

```
Garantías:
✓ El mensaje se entrega AL MENOS una vez
✓ El broker almacena mensajes si el suscriptor está offline
✓ El cliente confirma la recepción (ACK)
✓ Posible entrega duplicada en caso de reconexión

Flujo QoS 1:
1. Sensor publica con QoS 1
2. Broker envía PUBACK
3. Broker entrega a subscriber
4. Subscriber envía PUBACK
5. Broker confirma entrega
```

### Persistencia de Datos

```
Sensores:      Cache en memoria (~100 últimos mensajes)
MQTT Broker:   Persistencia en disco (/mosquitto/data)
MongoDB:       Persistencia permanente en volumen Docker
Dashboard:     Cache de datos con TTL de 10 segundos
```

### Recuperación ante Fallos

```
Si MQTT Broker se cae:
1. Sensores reintentan cada 5 segundos
2. Broker recupera mensajes almacenados
3. Subscriber reinicia suscripción

Si MongoDB se cae:
1. Subscriber reintenta inserción
2. Datos en memoria se pierden (último ~100)
3. API no responde hasta recuperación

Si Dashboard se cae:
1. Usuario no puede visualizar datos
2. Pero datos siguen fluyendo de sensores a BD
```

---

## 📈 Escalabilidad

### Configuración Actual

- **Sensores**: 3 (tomate, zanahoria, maíz)
- **Frecuencia**: 1 lectura cada 15 segundos
- **Datos por día**: ~17,280 registros (3 sensores × 60×60×24/15)
- **Tamaño aproximado**: ~1.5 MB por día
- **Retención**: Indefinida (hasta limpiar manualmente)

### Para Escalar a 100 Sensores

```
Cambios necesarios:
1. Aumentar recursos de MongoDB
   - RAM: mínimo 512 MB → 2-4 GB
   - CPU: 1 core → 2-4 cores

2. Agregar índices compuestos
   db.lecturas.createIndex({ 
     "zona": 1, 
     "sensor_id": 1, 
     "timestamp": -1 
   })

3. Implementar particionamiento
   - Por zona (campo/tomate, campo/zanahoria, etc.)
   - Por tiempo (rotación de colecciones mensual)

4. Aumentar memoria Redis
   - Para cachear queries frecuentes
   - TTL de datos en caché

5. API con load balancer
   - Múltiples instancias de Flask
   - Nginx como reverse proxy

Tópicos recomendados:
campo/zona/sensor_id/sensores
Para mejor escalabilidad y monitoreo individual
```

---

## 🔐 Seguridad

### Configuración Actual (Desarrollo)

- MQTT anónimo (sin autenticación)
- Sin TLS/SSL
- API sin API keys
- MongoDB sin contraseña

### Para Producción

```
1. MQTT con Autenticación
   mqtt:
     username: agro_user
     password: ${MQTT_PASSWORD}

2. Encriptación TLS
   listeners:
     default:
       protocol: mqtt
       port: 8883
       tls-version: tlsv1.3

3. API con JWT
   @app.route("/api/<path>")
   @require_auth
   def protected():
       pass

4. MongoDB con RBAC
   db.createUser({
     user: "agro_app",
     pwd: "${MONGO_PASSWORD}",
     roles: ["readWrite"]
   })

5. Variables de entorno sensibles
   .env (gitignore)
   docker secrets (para Docker Swarm)
```

---

## 📚 Referencias

- **MQTT Protocol**: https://mqtt.org
- **Mosquitto Broker**: https://mosquitto.org
- **MongoDB**: https://www.mongodb.com
- **Flask**: https://flask.palletsprojects.com
- **Streamlit**: https://streamlit.io
- **Docker Compose**: https://docs.docker.com/compose

---

**Última actualización**: Abril 2024
**Versión**: 1.0.0
**Autor**: Sistema IoT Agrícola
