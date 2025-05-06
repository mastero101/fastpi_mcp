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
Trae

29 context(s) used

¡Entendido! Para habilitar la búsqueda de componentes por nombre, necesitamos actualizar principalmente el archivo de rutas para exponer un nuevo endpoint. El archivo ollama_client.py ya parece estar configurado para usar una herramienta con el nombre buscar_componente_por_nombre y un parámetro query . El archivo main.py no debería necesitar cambios ya que el enrutador de componentes ya está incluido y FastApiMCP debería descubrir automáticamente la nueva ruta.

Aquí están los cambios necesarios para g:\Proyecto Python\fastpi_mcp\backend\routes\componentes_routes.py :

1. Importar la lógica de búsqueda : Añadiremos search_componentes_by_name_logic desde el controlador.
2. Añadir la nueva ruta : Crearemos un endpoint GET, por ejemplo /componentes/buscar/ , que acepte un parámetro de consulta llamado query . La función que maneja esta ruta se llamará buscar_componente_por_nombre para que coincida con el nombre de la herramienta esperado por ollama_client.py .
Aquí tienes el código actualizado:

componentes_routes.py

Apply

Open Folder

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

from fastapi import

APIRouter, HTTPException,

Depends, Body, status, Query

# Añadir Query

from typing import List,

Dict, Any, Optional

// ... existing code ...

from backend.controllers.

componentes_controller

import (

get_all_componentes_logic

,

get_componente_by_id_logi

c,

update_componente_logic,

delete_componente_logic,

create_componente_logic,

search_componentes_by_nam

e_logic # <--- Añadir

esta importación

)

router = APIRouter (

// ... existing code ...

async def

get_componente_route

( componente_id: int , conn:

mysql.connector.

MySQLConnection = Depends

( get_db_conn ) ) :

return

get_componente_by_id_logi

c ( conn, componente_id )

@ router.get ( "/buscar/" ,

response_model = List [ Dict

[ str , Any ] ] , tags =

[ "Componentes" ] )

async def

buscar_componente_por_nombre (

query: str = Query ( ...,

description = "Término de

búsqueda para el nombre

o modelo del

componente" ,

min_length = 1 ) ,

conn: mysql.connector.

MySQLConnection = Depends

( get_db_conn )

) :

"""

Busca componentes por su

nombre o modelo.

El término de búsqueda

se pasa como el

parámetro 'query'.

"""

# La función

search_componentes_by_nam

e_logic espera un

parámetro 'nombre'.

# Mapeamos el parámetro

'query' de la ruta al

parámetro 'nombre' del

controlador.

resultados =

search_componentes_by_nam

e_logic ( conn,

nombre = query )

if not resultados:

# Aunque la lógica

del controlador

puede devolver una

lista vacía (lo cual

es correcto),

# podrías querer que

la API devuelva 404

si no hay resultados,

# o simplemente una

lista vacía

(actualmente

devuelve lista

vacía).

# Por consistencia

con otras búsquedas,

devolver una lista

vacía está bien.

pass

return resultados

@ router.post ( "/" ,

response_model = Dict [ str ,

Any ] , status_code = status.

HTTP_201_CREATED )

async def

create_componente_route (

// ... existing code ...

Fold

Explicación de los cambios:

- Se importó Query de fastapi para una mejor definición del parámetro de consulta.
- Se añadió search_componentes_by_name_logic a la lista de importaciones desde backend.controllers.componentes_controller .
- Se ha creado una nueva ruta GET /componentes/buscar/ .
  - La función se llama buscar_componente_por_nombre para que fastapi-mcp la exponga con este nombre, coincidiendo con lo que ollama_client.py espera.
  - Acepta un parámetro de consulta query . Usamos Query(..., min_length=1) para indicar que es obligatorio y debe tener al menos un carácter.
  - Llama a search_componentes_by_name_logic pasando el valor de query como el argumento nombre que espera la función lógica.
  - Se ha añadido la etiqueta tags=["Componentes"] para que aparezca agrupada en la documentación de Swagger UI.
Con estos cambios, el endpoint /componentes/buscar/?query=termino_busqueda estará disponible y la configuración existente en `ollama_client.py` para la herramienta buscar_componente_por_nombre debería funcionar correctamente. No se necesitan cambios en `main.py` ni en `ollama_client.py` .

Alejandro Castro Mastero

Copy

Delete

Podrias crear un readme del proyecto?

Trae

26 context(s) used

Workspace

componentes_routes.py 89-89

componentes_routes.py 1-153

componentes_controller.py 1-137

main.py 1-197

componentes_routes.py 110-123

... More ( 20 +)

¡Claro! Puedo ayudarte a crear un archivo README.md para tu proyecto. Basándome en la información que tengo, aquí tienes un borrador inicial.

README.md

Apply

Open Folder

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

46

47

48

49

50

51

52

# Proyecto FastAPI - API de

Componentes de PC con MCP

Este proyecto implementa una

API RESTful utilizando

FastAPI para gestionar una

base de datos de componentes

de PC. También integra

`fastapi-mcp` para exponer

funcionalidades a través del

protocolo MCP (Message

Centric Protocol),

permitiendo la interacción

con agentes de IA como los

basados en Langchain.

## Descripción

La API permite realizar

operaciones CRUD (Crear,

Leer, Actualizar, Eliminar)

sobre componentes de PC

almacenados en una base de

datos MariaDB/MySQL. Además,

incluye un cliente

( `ollama_client.py` y

`claude.py` ) que demuestra

cómo un agente de IA puede

interactuar con las

herramientas expuestas por

el servidor MCP.

## Características

Principales

* **API de Componentes:**

* Listar todos los

componentes.

* Obtener un

componente por su ID.

* Buscar componentes

por nombre/modelo.

* Crear nuevos

componentes.

* Actualizar

componentes existentes.

* Eliminar componentes.

* **Integración con

FastAPI-MCP:**

* Expone las

funcionalidades de la

API como herramientas a

través de un servidor

MCP ( `/mcp` ).

* Permite que clientes

MCP (como agentes

Langchain) invoquen

estas herramientas.

* **Cliente de Agente IA

(Ejemplos):**

* `ollama_client.py` :

Un cliente que se

conecta al servidor MCP

y utiliza herramientas

para interactuar con un

modelo Ollama.

* `claude.py` : Un

ejemplo de cómo

configurar un agente

Langchain con un modelo

Claude para usar las

herramientas MCP.

* **Gestión de Base de

Datos:**

* Conexión a MariaDB/

MySQL.

* Manejo de

transacciones y errores.

* **Validación de Datos:**

* Uso de Pydantic para

la validación de datos

de entrada y salida en

las rutas de la API.

* **Documentación

Automática:**

* Swagger UI ( `/docs` )

y ReDoc ( `/redoc` )

generados por FastAPI.

* **Health Check:**

* Endpoint `/` que

muestra el estado de la

API, la base de datos y

los recursos del

servidor.

## Tecnologías Utilizadas

* **Backend:**

* Python 3.x

* FastAPI: Framework

web moderno y rápido

para construir APIs.

* Uvicorn: Servidor

ASGI para FastAPI.

* Pydantic: Para

validación de datos.

* MySQL Connector

Python: Para la

interacción con la base

de datos MariaDB/MySQL.

* `python-dotenv` :

Para la gestión de

variables de entorno.

* `fastapi-mcp` : Para

la integración del

Message Centric Protocol.

* **Integración IA

(Ejemplos):**

* Langchain: Framework

para construir

aplicaciones con LLMs.

* Ollama: Para

ejecutar modelos de

lenguaje localmente

(ejemplo en

`ollama_client.py` ).

* Anthropic (Claude):

Modelo de lenguaje

(ejemplo en `claude.py` ).

* **Base de Datos:**

* MariaDB / MySQL

## Estructura del Proyecto

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


