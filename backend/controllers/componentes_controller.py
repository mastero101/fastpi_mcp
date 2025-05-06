from fastapi import HTTPException
from mysql.connector import Error
from typing import List, Dict, Any

# Nota: La conexión a la BD (conn) se pasará como argumento a estas funciones

def get_all_componentes_logic(conn):
    """Lógica para obtener todos los componentes."""
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, tipo, modelo, precio, tienda, url, consumo, socket, rams, potencia, img FROM componentes")
        componentes = cursor.fetchall()
        cursor.close()
        if not componentes:
            return []
        return componentes
    except Error as e:
        print(f"Error en el controlador al consultar componentes: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al consultar datos: {e}")

def get_componente_by_id_logic(conn, componente_id: int):
    """Lógica para obtener un componente por su ID."""
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, tipo, modelo, precio, tienda, url, consumo, socket, rams, potencia, img FROM componentes WHERE id = %s"
        cursor.execute(query, (componente_id,))
        componente = cursor.fetchone()
        cursor.close()
        if componente is None:
            raise HTTPException(status_code=404, detail="Componente no encontrado")
        return componente
    except Error as e:
        print(f"Error en el controlador al consultar componente {componente_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al consultar el dato: {e}")

def search_componentes_by_name_logic(conn, nombre: str):
    """Lógica para buscar componentes por nombre (modelo)."""
    try:
        cursor = conn.cursor(dictionary=True)
        # Usamos LIKE para búsquedas parciales, el comodín % debe ser añadido al valor
        query = "SELECT id, tipo, modelo, precio, tienda, url, consumo, socket, rams, potencia, img FROM componentes WHERE modelo LIKE %s"
        search_term = f"%{nombre}%"
        cursor.execute(query, (search_term,))
        componentes = cursor.fetchall()
        cursor.close()
        # Es normal que una búsqueda no devuelva resultados, así que no lanzamos 404 aquí.
        # La API puede devolver una lista vacía.
        return componentes
    except Error as e:
        print(f"Error en el controlador al buscar componentes por nombre '{nombre}': {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al buscar componentes: {e}")

def update_componente_logic(conn, componente_id: int, componente_data: Dict[str, Any]):
    """Lógica para actualizar un componente por su ID."""
    # Filtrar claves None para no intentar actualizar con NULL si no se provee
    fields_to_update = {k: v for k, v in componente_data.items() if v is not None}

    if not fields_to_update:
        raise HTTPException(status_code=400, detail="No hay datos para actualizar.")

    set_clause = ", ".join([f"{key} = %s" for key in fields_to_update.keys()])
    values = list(fields_to_update.values())
    values.append(componente_id)

    query = f"UPDATE componentes SET {set_clause} WHERE id = %s"

    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(values))
        conn.commit() # Importante para guardar los cambios

        if cursor.rowcount == 0:
            cursor.close()
            raise HTTPException(status_code=404, detail="Componente no encontrado para actualizar.")
        
        cursor.close()
        # Devolver el componente actualizado
        return get_componente_by_id_logic(conn, componente_id)
    except Error as e:
        conn.rollback() # Revertir cambios en caso de error
        print(f"Error en el controlador al actualizar componente {componente_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al actualizar el dato: {e}")

def delete_componente_logic(conn, componente_id: int):
    """Lógica para eliminar un componente por su ID."""
    try:
        cursor = conn.cursor()
        query = "DELETE FROM componentes WHERE id = %s"
        cursor.execute(query, (componente_id,))
        conn.commit() # Importante para guardar los cambios

        if cursor.rowcount == 0:
            cursor.close()
            raise HTTPException(status_code=404, detail="Componente no encontrado para eliminar.")
        
        cursor.close()
        return {"message": "Componente eliminado exitosamente", "id_eliminado": componente_id}
    except Error as e:
        conn.rollback() # Revertir cambios en caso de error
        print(f"Error en el controlador al eliminar componente {componente_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al eliminar el dato: {e}")


def create_componente_logic(conn, componente_data: Dict[str, Any]):
    """Lógica para crear un nuevo componente."""
    # Asegurarse de que los campos numéricos opcionales sean None si están vacíos o no presentes
    # Esto dependerá de cómo el modelo Pydantic maneje la conversión.
    # Por ahora, asumimos que componente_data ya tiene los tipos correctos del modelo Pydantic.

    column_names = ", ".join(componente_data.keys())
    value_placeholders = ", ".join(["%s"] * len(componente_data))
    values = tuple(componente_data.values())

    query = f"INSERT INTO componentes ({column_names}) VALUES ({value_placeholders})"

    try:
        cursor = conn.cursor()
        cursor.execute(query, values)
        new_componente_id = cursor.lastrowid # Obtener el ID del componente recién insertado
        conn.commit()
        cursor.close()

        if new_componente_id:
            # Devolver el componente recién creado
            return get_componente_by_id_logic(conn, new_componente_id)
        else:
            # Esto no debería ocurrir si la inserción fue exitosa y la tabla tiene autoincremento
            raise HTTPException(status_code=500, detail="No se pudo obtener el ID del nuevo componente.")
            
    except Error as e:
        conn.rollback()
        print(f"Error en el controlador al crear componente: {e}")
        # Verificar si es un error de entrada duplicada (ej. modelo único)
        if e.errno == 1062: # Código de error para entrada duplicada en MySQL/MariaDB
             raise HTTPException(status_code=409, detail=f"Error al crear componente: Entrada duplicada. {e.msg}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al crear el dato: {e}")