# Proyecto FastAPI - API de Componentes de PC con MCP

Este proyecto implementa una API RESTful utilizando FastAPI para gestionar una base de datos de componentes de PC. También integra `fastapi-mcp` para exponer funcionalidades a través del protocolo MCP (Message Centric Protocol), permitiendo la interacción con agentes de IA como los basados en Langchain.

## Descripción

La API permite realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre componentes de PC almacenados en una base de datos MariaDB/MySQL. Además, incluye un cliente (`ollama_client.py` y `claude.py`) que demuestra cómo un agente de IA puede interactuar con las herramientas expuestas por el servidor MCP.

## Características Principales

*   **API de Componentes:**
    *   Listar todos los componentes.
    *   Obtener un componente por su ID.
    *   Buscar componentes por nombre/modelo.
    *   Crear nuevos componentes.
    *   Actualizar componentes existentes.
    *   Eliminar componentes.
*   **Integración con FastAPI-MCP:**
    *   Expone las funcionalidades de la API como herramientas a través de un servidor MCP (`/mcp`).
    *   Permite que clientes MCP (como agentes Langchain) invoquen estas herramientas.
*   **Cliente de Agente IA (Ejemplos):**
    *   `ollama_client.py`: Un cliente que se conecta al servidor MCP y utiliza herramientas para interactuar con un modelo Ollama.
    *   `claude.py`: Un ejemplo de cómo configurar un agente Langchain con un modelo Claude para usar las herramientas MCP.
*   **Gestión de Base de Datos:**
    *   Conexión a MariaDB/MySQL.
    *   Manejo de transacciones y errores.
*   **Validación de Datos:**
    *   Uso de Pydantic para la validación de datos de entrada y salida en las rutas de la API.
*   **Documentación Automática:**
    *   Swagger UI (`/docs`) y ReDoc (`/redoc`) generados por FastAPI.
*   **Health Check:**
    *   Endpoint `/` que muestra el estado de la API, la base de datos y los recursos del servidor.

## Tecnologías Utilizadas

*   **Backend:**
    *   Python 3.x
    *   FastAPI: Framework web moderno y rápido para construir APIs.
    *   Uvicorn: Servidor ASGI para FastAPI.
    *   Pydantic: Para validación de datos.
    *   MySQL Connector Python: Para la interacción con la base de datos MariaDB/MySQL.
    *   `python-dotenv`: Para la gestión de variables de entorno.
    *   `fastapi-mcp`: Para la integración del Message Centric Protocol.
*   **Integración IA (Ejemplos):**
    *   Langchain: Framework para construir aplicaciones con LLMs.
    *   Ollama: Para ejecutar modelos de lenguaje localmente (ejemplo en `ollama_client.py`).
    *   Anthropic (Claude): Modelo de lenguaje (ejemplo en `claude.py`).
*   **Base de Datos:**
    *   MariaDB / MySQL

## Estructura del Proyecto (Backend)

El proyecto está organizado en varios módulos y directorios:

*   `backend/`: Contiene el código fuente de la API y la lógica de negocio.
    *   `controllers/`: Módulos que contienen la lógica de negocio para cada entidad (componentes, por ejemplo).
    *   `db/`: Módulo para la gestión de la conexión a la base de datos.    
    *   `routes/`: Módulos que definen las rutas de la API.
    *   `main.py`: Punto de entrada de la aplicación FastAPI.
    *   `ollama_client.py` y `claude.py`: Ejemplos de clientes que utilizan las herramientas MCP.   
*   `README.md`: Este archivo.  
*   `requirements.txt`: Lista de dependencias Python.                           
     

(Backend)

Fold

fastpi_mcp/
├── backend/
│   ├── controllers/
│   │   └── componentes_controller.py  # Lógica de negocio para componentes
│   ├── db/
│   │   └── connection.py              # Configuración y conexión a la BD
│   ├── routes/
│   │   └── componentes_routes.py      # Definición de rutas API para componentes
│   ├── .env.example                   # Ejemplo de archivo de variables de entorno
│   ├── claude.py                      # Ejemplo de cliente Claude con Langchain y MCP
│   ├── main.py                        # Punto de entrada de la aplicación FastAPI y MCP
│   └── ollama_client.py               # Ejemplo de cliente Ollama con Langchain y MCP
└── README.md                          # Este archivo


## Configuración

1.  **Clonar el repositorio (si aplica).**
2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows: venv\Scripts\activate
    pip install -r requirements.txt # Asegúrate de tener un archivo requirements.txt
    ```
3.  **Configurar variables de entorno:**
    Crea un archivo `.env` en el directorio `backend/` basándote en `backend/.env.example` y configura los detalles de tu base de datos:
    ```env
    DB_HOST=tu_host_db
    DB_NAME=tu_nombre_db
    DB_USER=tu_usuario_db
    DB_PASS=tu_contraseña_db
    ```
4.  **Asegúrate de que tu servidor de base de datos (MariaDB/MySQL) esté en funcionamiento y la base de datos y tablas necesarias existan.**

## Cómo Ejecutar

Desde el directorio raíz del proyecto (`fastpi_mcp/`):

1.  **Para ejecutar la API FastAPI y el servidor MCP:**
    Navega al directorio `backend` si `main.py` está allí, o ejecuta desde la raíz si los imports están configurados para ello. El archivo `main.py` actual parece estar en `backend/main.py`.
    ```bash
    cd backend
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    O si estás en la raíz `fastpi_mcp` y tu `PYTHONPATH` está configurado o los imports son relativos adecuadamente:
    ```bash
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```

2.  **Acceder a la API:**
    *   Health Check y página principal: `http://127.0.0.1:8000/`
    *   Documentación Swagger UI: `http://127.0.0.1:8000/docs`
    *   Documentación ReDoc: `http://127.0.0.1:8000/redoc`
    *   Servidor MCP: `http://127.0.0.1:8000/mcp`

## Endpoints de la API

El prefijo principal para los componentes es `/componentes`.

*   `GET /componentes/`: Lista todos los componentes.
*   `GET /componentes/{componente_id}`: Obtiene un componente por su ID.
*   `GET /componentes/buscar/?query={termino_busqueda}`: Busca componentes por nombre/modelo.
*   `POST /componentes/`: Crea un nuevo componente.
*   `PUT /componentes/{componente_id}`: Actualiza un componente existente.
*   `DELETE /componentes/{componente_id}`: Elimina un componente.

## Uso del Cliente MCP (Ejemplos)

Los archivos `ollama_client.py` y `claude.py` en el directorio `backend/` muestran cómo se puede interactuar con las herramientas expuestas por el servidor MCP. Estos scripts necesitarán configuración adicional (modelos LLM, claves API si son necesarias) para funcionar.

Por ejemplo, para ejecutar el cliente de Ollama (asumiendo que tienes Ollama configurado y un modelo disponible):
```bash
# Desde el directorio backend/
python ollama_client.py
```


