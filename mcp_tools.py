
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient


# ==========================================
# LOAD MCP TOOLS (ASYNC)
# ==========================================
async def get_mcp_tool_list():
    print(" Connecting to MCP server...")

    client = MultiServerMCPClient(
        {
            "payment": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            }
        }
    )

    tools = await client.get_tools()

    
    for tool in tools:
        print(f"   • {tool.name}")

    return tools

def load_mcp_tools():
    tools = asyncio.run(get_mcp_tool_list())
    return {tool.name: tool for tool in tools}


if __name__ == "__main__":
    tools = asyncio.run(get_mcp_tool_list())

    expected = "get_transaction_details"
    found = any(t.name == expected for t in tools)
    print(f"   {expected}: {'Available' if found else 'Missing'}")
