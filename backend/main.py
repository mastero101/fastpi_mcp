from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import platform # Para información del SO
import psutil   # Para uso de CPU y Memoria
from fastapi_mcp import FastApiMCP # <--- Importar FastApiMCP

# Importamos la función de conexión para el health check y el router de componentes
from backend.db.connection import create_db_connection # Para el health_check
from backend.routes import componentes_routes

app = FastAPI(title="PC Parts API", version="1.0.0")

# Incluir el router de componentes
app.include_router(componentes_routes.router)

# Configurar y montar FastAPI-MCP
mcp = FastApiMCP(app) # <--- Crear una instancia de FastApiMCP con tu app FastAPI
mcp.mount()           # <--- Montar el servidor MCP en la ruta /mcp por defecto

@app.get("/", response_class=HTMLResponse, tags=["General"])
async def health_check():
    api_status = "OPERATIVA"
    db_status_message = "Desconocido"
    db_status_color = "orange"
    db_type = "MariaDB (a través de mysql.connector)"

    # Información del Servidor
    try:
        os_info = f"{platform.system()} {platform.release()}"
        cpu_usage = f"{psutil.cpu_percent(interval=0.1)}%" # Intervalo corto para no bloquear mucho
        memory_info = psutil.virtual_memory()
        memory_usage = f"{memory_info.percent}% (Usados: {memory_info.used // (1024**2)}MB / Total: {memory_info.total // (1024**2)}MB)"
    except Exception as e:
        os_info = "No disponible"
        cpu_usage = "No disponible"
        memory_usage = "No disponible"
        print(f"Error al obtener métricas del servidor: {e}")


    conn = None
    try:
        conn = create_db_connection()
        if conn and conn.is_connected():
            db_status_message = "CONECTADA"
            db_status_color = "green"
        else:
            db_status_message = "ERROR DE CONEXIÓN"
            db_status_color = "red"
    except Exception as e:
        db_status_message = f"ERROR ({type(e).__name__})"
        db_status_color = "red"
        print(f"Excepción en health_check al verificar la BD: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estado del Sistema - PC Parts API</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px; /* Añadido padding para evitar que el container toque los bordes en pantallas pequeñas */
                background-color: #f0f2f5;
                color: #333;
                display: flex;
                justify-content: center;
                align-items: flex-start; /* Cambiado a flex-start para mejor visualización si el contenido es largo */
                min-height: 100vh;
                box-sizing: border-box; /* Para que el padding no aumente el tamaño total */
            }}
            .container {{
                background-color: #ffffff;
                padding: 30px 40px;
                border-radius: 12px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                width: 90%;
                max-width: 750px; /* Un poco más ancho para la nueva info */
                text-align: left;
                margin-top: 20px; /* Espacio superior */
                margin-bottom: 20px; /* Espacio inferior */
            }}
            h1 {{
                color: #1a73e8;
                border-bottom: 3px solid #1a73e8;
                padding-bottom: 15px;
                margin-top: 0;
                font-size: 2em;
                text-align: center; /* Centrar el título principal */
            }}
            .section-title {{
                font-size: 1.5em;
                color: #333;
                margin-top: 30px;
                margin-bottom: 15px;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 10px;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: auto 1fr; /* Columna para etiqueta y columna para valor */
                gap: 10px 20px; /* Espacio entre filas y columnas */
                align-items: center;
            }}
            .info-grid strong {{
                color: #555;
                font-weight: 600; /* Un poco más de peso */
            }}
            .info-grid span {{
                text-align: right; /* Alinear valores a la derecha */
            }}
            .status-badge {{
                padding: 8px 15px;
                border-radius: 20px;
                color: white;
                font-weight: bold;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: inline-block; /* Para que el badge no ocupe todo el ancho */
            }}
            .status-ok {{ background-color: #34a853; }}
            .status-error {{ background-color: #ea4335; }}
            .status-unknown {{ background-color: #fbbc05; color: #333 !important; }}
            .info-badge {{ /* Badge genérico para otra info */
                background-color: #e0e0e0;
                color: #333;
                padding: 6px 12px;
                border-radius: 15px;
                font-size: 0.9em;
                display: inline-block;
            }}
            .links {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
            }}
            .links a {{
                color: #1a73e8;
                text-decoration: none;
                margin: 0 10px;
                font-weight: 500;
            }}
            .links a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Estado del Sistema</h1>
            
            <h2 class="section-title">API y Base de Datos</h2>
            <div class="info-grid">
                <strong>Estado de la API:</strong>
                <span class="status-badge status-ok">{api_status}</span>
                
                <strong>Estado de la Base de Datos:</strong>
                <span class="status-badge" style="background-color:{db_status_color};{'color: #333;' if db_status_color == 'orange' else ''}">{db_status_message}</span>
                
                <strong>Tipo de Base de Datos:</strong>
                <span class="info-badge">{db_type}</span>
            </div>

            <h2 class="section-title">Recursos del Servidor</h2>
            <div class="info-grid">
                <strong>Sistema Operativo:</strong>
                <span class="info-badge">{os_info}</span>

                <strong>Uso de CPU:</strong>
                <span class="info-badge">{cpu_usage}</span>

                <strong>Uso de Memoria:</strong>
                <span class="info-badge">{memory_usage}</span>
            </div>

            <div class="links">
                <p>Consulta la <a href="/docs" target="_blank">Documentación (Swagger UI)</a> o <a href="/redoc" target="_blank">ReDoc</a>.</p>
                <p>Accede al <a href="/mcp" target="_blank">Servidor MCP</a>.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)