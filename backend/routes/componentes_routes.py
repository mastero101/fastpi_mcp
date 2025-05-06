from fastapi import APIRouter, HTTPException, Depends, Body, status, Query # Añadir Query
from typing import List, Dict, Any, Optional # Añadir Optional
from pydantic import BaseModel, Field, field_validator # Añadir BaseModel y Field
import mysql.connector # Para tipado de la conexión

# Importamos la función para crear la conexión y las funciones del controlador
from backend.db.connection import create_db_connection
from backend.controllers.componentes_controller import (
    get_all_componentes_logic,
    get_componente_by_id_logic,
    update_componente_logic,
    delete_componente_logic,
    create_componente_logic,
    search_componentes_by_name_logic # <--- Añadir esta importación
)

router = APIRouter(
    prefix="/componentes",  # Prefijo para todas las rutas en este router
    tags=["Componentes"]    # Etiqueta para la documentación de Swagger UI
)

# Modelo Pydantic para la creación de componentes (sin ID)
class ComponenteCreate(BaseModel):
    tipo: str
    modelo: str
    precio: float = Field(..., gt=0) # Precio debe ser mayor que 0
    tienda: str
    url: Optional[str] = None
    consumo: Optional[int] = Field(default=None, ge=0) # Consumo no puede ser negativo
    socket: Optional[str] = None
    rams: Optional[str] = None
    potencia: Optional[int] = Field(default=None, ge=0) # Potencia no puede ser negativa
    img: Optional[str] = None

    @field_validator('consumo', 'potencia', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v == "":
            return None
        return v

    class Config:
        anystr_strip_whitespace = True # Limpia espacios en blanco de los strings


# Modelo Pydantic para la actualización de componentes (todos los campos opcionales)
class ComponenteUpdate(BaseModel):
    tipo: Optional[str] = None
    modelo: Optional[str] = None
    precio: Optional[float] = Field(default=None, gt=0)
    tienda: Optional[str] = None
    url: Optional[str] = None
    consumo: Optional[int] = Field(default=None, ge=0)
    socket: Optional[str] = None
    rams: Optional[str] = None
    potencia: Optional[int] = Field(default=None, ge=0)
    img: Optional[str] = None

    @field_validator('consumo', 'potencia', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v == "":
            return None
        return v

    class Config:
        anystr_strip_whitespace = True

# Función de dependencia para obtener y cerrar la conexión a la BD
async def get_db_conn():
    conn = create_db_connection()
    if conn is None or not conn.is_connected():
        raise HTTPException(status_code=503, detail="No se pudo conectar a la base de datos.")
    try:
        yield conn
    finally:
        if conn and conn.is_connected():
            conn.close()
            print("Conexión a MariaDB cerrada desde get_db_conn")


@router.get("/", response_model=List[Dict[str, Any]])
async def get_componentes_route(conn: mysql.connector.MySQLConnection = Depends(get_db_conn)):
    return get_all_componentes_logic(conn)

@router.get("/{componente_id}", response_model=Dict[str, Any])
async def get_componente_route(componente_id: int, conn: mysql.connector.MySQLConnection = Depends(get_db_conn)):
    return get_componente_by_id_logic(conn, componente_id)

@router.get("/buscar/", response_model=List[Dict[str, Any]], tags=["Componentes"])
async def buscar_componente_por_nombre(
    query: str = Query(..., description="Término de búsqueda para el nombre o modelo del componente", min_length=1),
    conn: mysql.connector.MySQLConnection = Depends(get_db_conn)
):
    """
    Busca componentes por su nombre o modelo.
    El término de búsqueda se pasa como el parámetro 'query'.
    """
    # La función search_componentes_by_name_logic espera un parámetro 'nombre'.
    # Mapeamos el parámetro 'query' de la ruta al parámetro 'nombre' del controlador.
    resultados = search_componentes_by_name_logic(conn, nombre=query)
    if not resultados:
        # Aunque la lógica del controlador puede devolver una lista vacía (lo cual es correcto),
        # podrías querer que la API devuelva 404 si no hay resultados,
        # o simplemente una lista vacía (actualmente devuelve lista vacía).
        # Por consistencia con otras búsquedas, devolver una lista vacía está bien.
        pass
    return resultados

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_componente_route(
    componente_data: ComponenteCreate, # Usa el modelo Pydantic para validación
    conn: mysql.connector.MySQLConnection = Depends(get_db_conn)
):
    """
    Crea un nuevo componente.
    El ID será generado automáticamente por la base de datos.
    """
    # Convertir el modelo Pydantic a un diccionario para el controlador
    # exclude_unset=True es importante si quieres que los valores no enviados no se pasen como None
    # pero para la creación, usualmente queremos pasar todos los valores definidos (o sus defaults).
    return create_componente_logic(conn, componente_data.model_dump(exclude_none=True))


@router.put("/{componente_id}", response_model=Dict[str, Any])
async def update_componente_route(
    componente_id: int,
    componente_data: ComponenteUpdate, # Usa el modelo Pydantic para validación de actualización
    conn: mysql.connector.MySQLConnection = Depends(get_db_conn)
):
    """
    Actualiza un componente existente por su ID.
    Solo los campos proporcionados en el cuerpo de la solicitud serán actualizados.
    """
    # .model_dump(exclude_unset=True) asegura que solo los campos enviados en el JSON
    # se pasen al controlador. Si un campo no se envía, no se incluirá en el dict.
    # Si se envía explícitamente como null, se pasará como None.
    update_data = componente_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar. El cuerpo de la solicitud está vacío o solo contiene campos no configurados.")
    return update_componente_logic(conn, componente_id, update_data)

@router.delete("/{componente_id}", status_code=status.HTTP_200_OK)
async def delete_componente_route(
    componente_id: int,
    conn: mysql.connector.MySQLConnection = Depends(get_db_conn)
):
    """
    Elimina un componente por su ID.
    """
    result = delete_componente_logic(conn, componente_id)
    return result # Devuelve el mensaje de éxito del controlador