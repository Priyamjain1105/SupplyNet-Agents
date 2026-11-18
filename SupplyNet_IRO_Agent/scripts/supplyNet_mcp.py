import asyncio
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

import asyncio
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

system_prompt = """
You are an intelligent Supply Chain & Logistics Research Assistant helping managers analyze routes, weather conditions, traffic disruptions, and toll costs across highway corridors.
"""


async def get_tools():
    PROJECT_ROOT = r"C:\Users\priya\Downloads\Supply-Chain-Management"
    python_exe = os.path.join(PROJECT_ROOT, "senv", "Scripts", "python.exe")
    SERVERS_DIR = os.path.join(
        PROJECT_ROOT, "SupplyNet_MCP", "scripts", "server"
    )

    # Pass PYTHONPATH to ensure child server processes locate the SupplyNet_MCP package
    sub_env = {**os.environ, "PYTHONPATH": PROJECT_ROOT}

    client = MultiServerMCPClient(
        {
            "news_server": {
                "command": python_exe,
                "args": [os.path.join(SERVERS_DIR, "news_server.py"), "--stdio"],
                "env": sub_env,
                "transport": "stdio",
            },
            "weather_server": {
                "command": python_exe,
                "args": [
                    os.path.join(SERVERS_DIR, "weather_server.py"),
                    "--stdio",
                ],
                "env": sub_env,
                "transport": "stdio",
            },
            "toll_server": {
                "command": python_exe,
                "args": [
                    os.path.join(SERVERS_DIR, "toll_rag_server.py"),
                    "--stdio",
                ],
                "env": sub_env,
                "transport": "stdio",
            },
            "osrm_server": {
                "command": python_exe,
                "args": [os.path.join(SERVERS_DIR, "osrm_server.py"), "--stdio"],
                "env": sub_env,
                "transport": "stdio",
            },
        }
    )

    tools = await client.get_tools()

    print(f"Loaded {len(tools)} tools")
    print(f"Tools available: {[tool.name for tool in tools]}")

    return tools


async def route_research(query: str):
    tools = await get_tools()

    # Use create_react_agent from langgraph.prebuilt
    agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)

    result = await agent.ainvoke({"messages": [HumanMessage(query)]})

    # Access .content from the last response message
    response = result["messages"][-1].content
    print("\n--- Final Answer ---")
    print(response)
    return response


if __name__ == "__main__":
    query = "What is the best route from Delhi to Kochi and what are the toll costs and weather along the way?"

    asyncio.run(route_research(query))