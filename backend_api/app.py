#!/usr/bin/env python3
"""
Flask REST API for Agricultural IoT System
Endpoints:
  GET /logs - All zones latest 20 readings
  GET /logs/<zona> - Specific zone latest 20 readings
  GET /zonas - List of unique zones
"""

import os
from flask import Flask, jsonify, render_template_string, request
from pymongo import MongoClient, DESCENDING
from datetime import datetime


app = Flask(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/")
MONGODB_DB = "agro_iot"
MONGODB_COLLECTION = "lecturas"

# MongoDB client
mongo_client = None
coleccion = None


def init_mongodb():
    """Initialize MongoDB connection"""
    global mongo_client, coleccion
    max_retries = 5
    for intento in range(max_retries):
        try:
            mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            mongo_client.admin.command('ping')
            db = mongo_client[MONGODB_DB]
            coleccion = db[MONGODB_COLLECTION]
            
            # Create indexes for better query performance and to prevent duplicates
            try:
                # Index on timestamp for sorting
                coleccion.create_index("timestamp")
                # Index on zona for filtering
                coleccion.create_index("zona")
                # Compound index for efficient queries
                coleccion.create_index([("zona", 1), ("timestamp", -1)])
                print(f"[API] Índices de MongoDB creados/validados")
            except Exception as idx_error:
                print(f"[API] Aviso al crear índices: {idx_error}")
            
            print(f"[API] MongoDB conectado: {MONGODB_URI}")
            return True
        except Exception as e:
            print(f"[API] Intento {intento + 1}/{max_retries} - Error: {e}")
            if intento < max_retries - 1:
                import time
                time.sleep(2)
    return False


@app.route('/', methods=['GET'])
def index():
    """API root endpoint - Information and available endpoints"""
    try:
        available_zones = []
        db_status = "disconnected"
        
        if coleccion is not None:
            try:
                available_zones = sorted(list(coleccion.distinct("zona")))
                db_status = "connected"
            except Exception as e:
                print(f"[API] Error obteniendo zonas: {e}")
                db_status = "error"
        
        # Check if requesting JSON (API call) or HTML (browser)
        if request.headers.get('Accept', '').startswith('application/json'):
            return jsonify({
                "system": "IoT Agricultural Monitoring System",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "database_status": db_status,
                "endpoints": {
                    "GET /": "This information page",
                    "GET /zonas": "List all available crop zones",
                    "GET /logs": "Latest 20 readings from all zones",
                    "GET /logs/<zona>": "Latest 20 readings from specific zone",
                    "GET /health": "Health check endpoint"
                },
                "available_zones": available_zones
            }), 200
        
        # HTML Response
        html_template = """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>IoT Agrícola - API</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }
                
                .container {
                    max-width: 900px;
                    width: 100%;
                    background: rgba(255, 255, 255, 0.95);
                    border-radius: 15px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }
                
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }
                
                .header h1 {
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }
                
                .header p {
                    font-size: 1.2em;
                    opacity: 0.9;
                }
                
                .content {
                    padding: 40px 30px;
                }
                
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }
                
                .info-card {
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    border-radius: 8px;
                    transition: transform 0.3s ease;
                }
                
                .info-card:hover {
                    transform: translateY(-5px);
                }
                
                .info-card h3 {
                    color: #667eea;
                    margin-bottom: 10px;
                    font-size: 0.9em;
                    text-transform: uppercase;
                }
                
                .info-card p {
                    color: #333;
                    font-size: 1.3em;
                    font-weight: bold;
                }
                
                .status {
                    display: inline-block;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    font-weight: bold;
                }
                
                .status.connected {
                    background: #d4edda;
                    color: #155724;
                }
                
                .status.disconnected {
                    background: #f8d7da;
                    color: #721c24;
                }
                
                .zones-section {
                    margin-bottom: 40px;
                }
                
                .zones-section h2 {
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                }
                
                .zones-list {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                }
                
                .zone-badge {
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9em;
                }
                
                .endpoints-section {
                    margin-bottom: 30px;
                }
                
                .endpoints-section h2 {
                    color: #333;
                    margin-bottom: 20px;
                    font-size: 1.3em;
                }
                
                .endpoint {
                    background: #f8f9fa;
                    border-left: 4px solid #764ba2;
                    padding: 15px 20px;
                    margin-bottom: 10px;
                    border-radius: 8px;
                    font-family: 'Courier New', monospace;
                }
                
                .endpoint-method {
                    display: inline-block;
                    background: #764ba2;
                    color: white;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    margin-right: 10px;
                    font-size: 0.85em;
                }
                
                .endpoint-path {
                    color: #667eea;
                    font-weight: bold;
                }
                
                .endpoint-desc {
                    display: block;
                    color: #666;
                    font-family: 'Segoe UI', sans-serif;
                    margin-top: 5px;
                    font-size: 0.9em;
                }
                
                .footer {
                    background: #f8f9fa;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                    border-top: 1px solid #dee2e6;
                }
                
                .timestamp {
                    color: #999;
                    font-size: 0.85em;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌾 Sistema IoT Agrícola</h1>
                    <p>REST API - Monitoreo de Cultivos</p>
                </div>
                
                <div class="content">
                    <div class="info-grid">
                        <div class="info-card">
                            <h3>📊 Estado del Sistema</h3>
                            <p><span class="status {{ 'connected' if db_status == 'connected' else 'disconnected' }}">{{ db_status.upper() }}</span></p>
                        </div>
                        <div class="info-card">
                            <h3>🗄️ Base de Datos</h3>
                            <p>MongoDB</p>
                        </div>
                        <div class="info-card">
                            <h3>📈 Versión API</h3>
                            <p>1.0.0</p>
                        </div>
                    </div>
                    
                    {% if available_zones %}
                    <div class="zones-section">
                        <h2>🌱 Zonas Activas</h2>
                        <div class="zones-list">
                            {% if 'tomate' in available_zones %}<div class="zone-badge">🍅 Tomate</div>{% endif %}
                            {% if 'zanahoria' in available_zones %}<div class="zone-badge">🥕 Zanahoria</div>{% endif %}
                            {% if 'maiz' in available_zones %}<div class="zone-badge">🌽 Maíz</div>{% endif %}
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="endpoints-section">
                        <h2>📡 Endpoints Disponibles</h2>
                        
                        <div class="endpoint">
                            <span class="endpoint-method">GET</span>
                            <span class="endpoint-path">/</span>
                            <span class="endpoint-desc">Página de información del sistema (esta página)</span>
                        </div>
                        
                        <div class="endpoint">
                            <span class="endpoint-method">GET</span>
                            <span class="endpoint-path">/zonas</span>
                            <span class="endpoint-desc">Lista de zonas disponibles (JSON)</span>
                        </div>
                        
                        <div class="endpoint">
                            <span class="endpoint-method">GET</span>
                            <span class="endpoint-path">/logs</span>
                            <span class="endpoint-desc">Últimas 20 lecturas de todas las zonas (JSON)</span>
                        </div>
                        
                        <div class="endpoint">
                            <span class="endpoint-method">GET</span>
                            <span class="endpoint-path">/logs/&lt;zona&gt;</span>
                            <span class="endpoint-desc">Últimas 20 lecturas de una zona específica (JSON)</span>
                        </div>
                        
                        <div class="endpoint">
                            <span class="endpoint-method">GET</span>
                            <span class="endpoint-path">/health</span>
                            <span class="endpoint-desc">Health check del servidor (JSON)</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Hora del Sistema: <strong>{{ current_time }}</strong></p>
                    <p class="timestamp">Última actualización: {{ last_update }}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return render_template_string(
            html_template,
            db_status=db_status,
            available_zones=available_zones,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            last_update=datetime.now().isoformat()
        )
    except Exception as e:
        print(f"[API] Error en endpoint raíz: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/logs', methods=['GET'])
def logs():
    """Get latest 20 readings from all zones"""
    try:
        if coleccion is None:
            return jsonify({"error": "Database not connected"}), 503
        
        docs = list(
            coleccion.find({}, {"_id": 0})
            .sort("timestamp", DESCENDING)
            .limit(20)
        )
        return jsonify(docs), 200
    except Exception as e:
        print(f"[API] Error en /logs: {e}")
        return jsonify({"error": str(e), "details": "Internal server error"}), 500


@app.route('/logs/<zona>', methods=['GET'])
def logs_por_zona(zona):
    """Get latest 20 readings from specific zone"""
    try:
        if coleccion is None:
            return jsonify({"error": "Database not connected"}), 503
        
        if not zona or zona.strip() == "":
            return jsonify({"error": "Zona parameter cannot be empty"}), 400
        
        docs = list(
            coleccion.find({"zona": zona}, {"_id": 0})
            .sort("timestamp", DESCENDING)
            .limit(20)
        )
        
        if not docs:
            return jsonify({"message": f"No data found for zona: {zona}", "data": []}), 200
        
        return jsonify(docs), 200
    except Exception as e:
        print(f"[API] Error en /logs/{zona}: {e}")
        return jsonify({"error": str(e), "details": "Internal server error"}), 500


@app.route('/zonas', methods=['GET'])
def zonas():
    """Get list of unique zones with data"""
    try:
        if coleccion is None:
            return jsonify({"error": "Database not connected"}), 503
        
        resultado = coleccion.distinct("zona")
        
        if not resultado:
            return jsonify({"message": "No zones found", "data": []}), 200
        
        return jsonify(sorted(resultado)), 200
    except Exception as e:
        print(f"[API] Error en /zonas: {e}")
        return jsonify({"error": str(e), "details": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    # Initialize MongoDB connection
    if not init_mongodb():
        print("[API] Error: No se pudo conectar a MongoDB")
        exit(1)

    # Run Flask app
    app.run(host="0.0.0.0", port=5000, debug=False)
