from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatAnthropic
from langchain.tools import Tool

# Configurar cliente para tu servidor MCP
# (Necesitarías implementar esta clase)
from mcp_client import MCPClient

# Inicializar cliente MCP
mcp_client = MCPClient("http://127.0.0.1:8000/mcp")

# Obtener herramientas disponibles
tools = mcp_client.get_tools()

# Configurar Claude
claude = ChatAnthropic(model="claude-3-opus-20240229")

# Inicializar agente
agent = initialize_agent(
    tools=tools,
    llm=claude,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True
)

# Interactuar con el agente
agent.run("Busca información sobre la tarjeta gráfica RTX 4090")