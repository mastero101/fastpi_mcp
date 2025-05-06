from langchain.agents import AgentType, initialize_agent
# from langchain.llms import Ollama # Deprecated
from langchain_community.llms import Ollama # Updated import
from langchain.tools import Tool
import requests
import json
import re
import time
from urllib.parse import urljoin # Import urljoin at the top
import uuid # Necesario para generar IDs de solicitud únicos

class MCPClient:
    def __init__(self, mcp_url):
        self.mcp_url = mcp_url
        self.session_id = None
        self.messages_url = None
        # Inicializar conexión con el servidor MCP
        self._connect()
        if not self.session_id:
            print("ADVERTENCIA: No se pudo establecer la sesión MCP. Las herramientas podrían no funcionar como se espera o usar datos de marcador de posición.")
    
    def _connect(self):
        try:
            print(f"Intentando conectar a: {self.mcp_url}")
            # Conectarse al endpoint MCP principal para obtener el session_id
            # Usamos stream=True para manejar la respuesta SSE
            # y un timeout para no esperar indefinidamente si algo va mal
            with requests.get(self.mcp_url, stream=True, timeout=10) as response:
                print(f"Respuesta recibida del servidor MCP, estado: {response.status_code}")
                response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
                
                # Leemos las primeras líneas de la respuesta del stream
                # para obtener la URL de mensajes con el session_id
                for line_bytes in response.iter_lines():
                    line = line_bytes.decode('utf-8').strip()
                    # print(f"Línea recibida del stream: {line}") # Debugging line
                    if line.startswith('data:'):
                        self.messages_url = line.replace('data:', '').strip()
                        # Asegurarnos de que la URL es completa si es relativa
                        if self.messages_url.startswith('/'):
                            self.messages_url = urljoin(self.mcp_url, self.messages_url)
                        
                        session_match = re.search(r'session_id=([^&]+)', self.messages_url)
                        if session_match:
                            self.session_id = session_match.group(1)
                            print(f"Conexión establecida con el servidor MCP. Session ID: {self.session_id}")
                            print(f"URL de mensajes: {self.messages_url}")
                            return # Salimos después de obtener la información necesaria
                        else:
                            print("No se pudo extraer el session_id de la URL de mensajes.")
                            return
                print("No se encontró la línea 'data:' con la URL de mensajes en la respuesta del servidor MCP después de iterar las líneas.")

        except requests.exceptions.Timeout:
            print(f"Error de red al conectar con el servidor MCP: Timeout después de 10 segundos esperando respuesta de {self.mcp_url}")
        except requests.exceptions.RequestException as e:
            print(f"Error de red al conectar con el servidor MCP: {str(e)}")
        except Exception as e:
            print(f"Error inesperado al conectar con el servidor MCP: {type(e).__name__} - {str(e)}")
    
    def get_tools(self):
        # En una implementación real, consultaríamos al servidor MCP
        # para obtener la lista de herramientas disponibles
        # El nombre de la herramienta DEBE coincidir con el expuesto por fastapi-mcp.
        # Revisa la documentación de fastapi-mcp o experimenta.
        
        return [
            Tool(
                name="listar_todos_los_componentes",
                func=self._listar_componentes,
                description="DEBES usar esta herramienta para obtener una lista completa de todos los componentes de PC cuando el usuario pida una lista general o explorar opciones. No necesita parámetros. La salida es una lista de componentes en formato JSON."
            ),
            Tool(
                name="buscar_componente_por_nombre",
                func=self._buscar_componente,
                description="DEBES usar esta herramienta para encontrar componentes específicos por su nombre o modelo. Proporciona el nombre o modelo como el parámetro 'query'. La salida es una lista de componentes coincidentes en formato JSON, incluyendo sus IDs. Necesitas el ID para obtener detalles completos."
            ),
            Tool(
                name="obtener_detalles_componente_por_id",
                func=self._obtener_componente_por_id,
                description="DEBES usar esta herramienta para obtener todos los detalles de un componente específico, incluyendo su precio, una vez que tengas su 'component_id' (obtenido de 'buscar_componente_por_nombre' o 'listar_todos_los_componentes'). El parámetro 'component_id' debe ser el ID numérico del componente. La salida son los detalles completos del componente en formato JSON."
            )
        ]
    
    def _send_mcp_request(self, tool_name, tool_input):
        if not self.session_id or not self.messages_url:
            print("MCPClient: No hay sesión activa para enviar la solicitud.")
            return {"error": "No session"}

        request_id = str(uuid.uuid4())
        payload = {
            "type": "tool_call",
            "id": request_id,
            "tool_name": tool_name,
            "tool_input": tool_input
        }
        
        print(f"Enviando solicitud MCP a {self.messages_url}: {json.dumps(payload)}")
        
        try:
            # El servidor MCP espera un stream de mensajes, pero para una llamada de herramienta simple,
            # enviamos una solicitud y esperamos una respuesta.
            # La biblioteca fastapi-mcp podría tener un manejo específico para esto.
            # Por ahora, intentaremos un POST simple y leeremos la respuesta.
            # NOTA: La comunicación MCP real es a través de Server-Sent Events (SSE).
            # Un cliente MCP completo manejaría un stream bidireccional.
            # Esta es una simplificación para probar la llamada a la herramienta.
            
            # Para fastapi-mcp, la solicitud se envía al endpoint de mensajes
            # y la respuesta se recibe como un evento SSE.
            # Necesitamos escuchar ese stream.
            
            headers = {'Accept': 'text/event-stream'}
            with requests.post(self.messages_url, json=payload, stream=True, headers=headers, timeout=20) as response:
                response.raise_for_status()
                print(f"Respuesta del servidor MCP (estado {response.status_code}) para la llamada a herramienta.")
                
                for line_bytes in response.iter_lines():
                    line = line_bytes.decode('utf-8').strip()
                    if not line: # Ignorar líneas de keep-alive vacías
                        continue
                    print(f"Línea de respuesta MCP: {line}")
                    if line.startswith('data:'):
                        data_str = line.replace('data:', '').strip()
                        try:
                            message = json.loads(data_str)
                            if message.get("type") == "tool_result" and message.get("request_id") == request_id:
                                print(f"Resultado de herramienta recibido: {message.get('tool_output')}")
                                return message.get("tool_output")
                            elif message.get("type") == "error":
                                print(f"Error de herramienta recibido: {message.get('message')}")
                                return {"error": message.get("message")}
                        except json.JSONDecodeError:
                            print(f"Error al decodificar JSON de la respuesta MCP: {data_str}")
                            return {"error": "Invalid JSON response from MCP server"}
                
                return {"error": "No tool_result message received for the request_id"}

        except requests.exceptions.Timeout:
            print(f"Timeout al enviar solicitud MCP para {tool_name}")
            return {"error": f"Timeout for tool {tool_name}"}
        except requests.exceptions.RequestException as e:
            print(f"Error de red al enviar solicitud MCP para {tool_name}: {e}")
            return {"error": f"Network error for tool {tool_name}: {e}"}
        except Exception as e:
            print(f"Error inesperado al enviar solicitud MCP para {tool_name}: {type(e).__name__} - {e}")
            return {"error": f"Unexpected error for tool {tool_name}: {e}"}

    def _listar_componentes(self, query=""): # Langchain a veces pasa un string vacío como query
        print(f"MCPClient._listar_componentes llamado con query: '{query}' (será ignorado)")
        # Para una herramienta que no toma argumentos, tool_input es un diccionario vacío.
        tool_output = self._send_mcp_request(tool_name="listar_todos_los_componentes", tool_input={})
        
        # El agente Langchain espera un string como resultado de la herramienta.
        if isinstance(tool_output, dict) and "error" in tool_output:
            return f"Error de la herramienta: {tool_output['error']}"
        elif tool_output is None:
            return "Error: No se recibió respuesta de la herramienta."
        return json.dumps(tool_output) # Convertir la salida (lista de componentes) a un string JSON

    def _buscar_componente(self, query: str):
        if not self.session_id or not self.messages_url:
            print("MCPClient: No hay sesión activa para buscar_componente.")
            return "Error: No se pudo conectar al servidor de herramientas."
        print(f"MCPClient._buscar_componente llamado con query: '{query}'")
        # Asume que la herramienta se llama 'buscar_componente_por_nombre' y espera {'query': 'valor'}
        tool_output = self._send_mcp_request(tool_name="buscar_componente_por_nombre", tool_input={"query": query})
        
        if isinstance(tool_output, dict) and "error" in tool_output:
            return f"Error de la herramienta: {tool_output['error']}"
        elif tool_output is None:
            return "Error: No se recibió respuesta de la herramienta."
        return json.dumps(tool_output)

    def _obtener_componente_por_id(self, component_id: str): # Langchain pasa los argumentos como strings
        if not self.session_id or not self.messages_url:
            print("MCPClient: No hay sesión activa para obtener_componente_por_id.")
            return "Error: No se pudo conectar al servidor de herramientas."
        print(f"MCPClient._obtener_componente_por_id llamado con ID: '{component_id}'")
        # Asume que la herramienta se llama 'obtener_detalles_componente_por_id' y espera {'component_id': valor}
        # El servidor FastAPI podría esperar un int, pero el protocolo MCP podría manejar la conversión
        # o la herramienta en el servidor debe estar preparada para un string.
        # Por seguridad, intentamos convertir a int si es posible, o el servidor debe manejarlo.
        try:
            tool_input_id = int(component_id)
        except ValueError:
            # Si no es un entero, podría ser un error o el servidor lo maneja como string
            print(f"Advertencia: component_id '{component_id}' no es un entero. Enviando como string.")
            tool_input_id = component_id

        tool_output = self._send_mcp_request(tool_name="obtener_detalles_componente_por_id", tool_input={"component_id": tool_input_id})
        
        if isinstance(tool_output, dict) and "error" in tool_output:
            return f"Error de la herramienta: {tool_output['error']}"
        elif tool_output is None:
            return "Error: No se recibió respuesta de la herramienta."
        return json.dumps(tool_output)

# Verificar si Ollama está en ejecución
def verificar_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            modelos = response.json().get("models", [])
            print("Modelos disponibles en Ollama:")
            for modelo in modelos:
                print(f"- {modelo['name']}")
            return True
        return False
    except:
        print("No se pudo conectar con Ollama. ¿Está en ejecución?")
        return False

# Verificar Ollama antes de continuar
if not verificar_ollama():
    print("Por favor, inicia Ollama antes de ejecutar este script.")
    print("Puedes descargarlo desde: https://ollama.ai/download")
    exit(1)

# Inicializar cliente MCP
print("Conectando con el servidor MCP...")
mcp_client = MCPClient("http://127.0.0.1:8000/mcp")

# Si la conexión falló, mcp_client.session_id será None.
# El constructor de MCPClient ya imprime una advertencia.

# Obtener herramientas disponibles
tools = mcp_client.get_tools()

# Configurar Ollama con DeepSeek
print("Inicializando modelo DeepSeek en Ollama...")
# Asegúrate de tener langchain-community instalado: pip install -U langchain-community
ollama_llm = Ollama(model="deepseek-r1:latest") # o el modelo que tengas

# Inicializar agente
print("Configurando agente LangChain...")
agent = initialize_agent(
    tools=tools,
    llm=ollama_llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Función para interactuar con el agente
def consultar_agente(consulta):
    print(f"\nConsulta: {consulta}")
    print("Procesando...")
    try:
        return agent.run(consulta)
    except Exception as e:
        return f"Error al procesar la consulta: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
    print("\n=== Cliente MCP con Ollama (DeepSeek) ===")
    print("Escribe 'salir' para terminar")
    
    while True:
        consulta = input("\n¿Qué quieres saber sobre componentes de PC? ")
        if consulta.lower() in ['salir', 'exit', 'quit']:
            break
            
        resultado = consultar_agente(consulta)
        print("\nRespuesta del Agente:")
        print(resultado)