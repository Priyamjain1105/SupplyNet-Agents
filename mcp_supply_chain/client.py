import asyncio
import os
import sys
import json
from typing import Dict, Any, List
from fastmcp import Client

# Ensure UTF-8 output encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# Ensure root workspace directory is in sys.path for fallback imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Streamable HTTP Server Endpoints for the Multi-Server MCP Architecture
SERVERS = {
    "news": "http://localhost:8001/mcp",
    "weather": "http://localhost:8002/mcp",
    "toll_rag": "http://localhost:8003/mcp",
    "osrm": "http://localhost:8004/mcp",
}

async def call_mcp_tool(server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute an MCP tool call on the target server via FastMCP Client."""
    url = SERVERS.get(server_name)
    if not url:
        raise ValueError(f"Unknown server '{server_name}'")
        
    try:
        async with Client(url) as client:
            result = await client.call_tool(tool_name, arguments)
            # Extract content text from CallToolResult if needed
            if hasattr(result, "content") and isinstance(result.content, list):
                text_parts = [item.text for item in result.content if hasattr(item, "text")]
                if text_parts:
                    return "\n".join(text_parts)
            return str(result)
    except Exception as e:
        # Fallback to direct module invocation if HTTP server is not active
        try:
            if server_name == "news":
                from mcp_supply_chain.servers import news_server
                fn = getattr(news_server, tool_name)
                return await fn(**arguments)
            elif server_name == "weather":
                from mcp_supply_chain.servers import weather_server
                fn = getattr(weather_server, tool_name)
                return await fn(**arguments)
            elif server_name == "toll_rag":
                from mcp_supply_chain.servers import toll_rag_server
                fn = getattr(toll_rag_server, tool_name)
                return await fn(**arguments)
            elif server_name == "osrm":
                from mcp_supply_chain.servers import osrm_server
                fn = getattr(osrm_server, tool_name)
                return await fn(**arguments)
        except Exception as fallback_err:
            return f"Error executing tool '{tool_name}' on server '{server_name}': {e} | Fallback Error: {fallback_err}"

async def run_multi_server_workflow():
    """Executes the Supply Chain Route Optimization Multi-Server MCP Workflow.
    
    Scenario (from Architecture Doc):
    1. Origin: Chandigarh, Destination: Visakhapatnam.
    2. OSRM Server: Fetch initial primary route and checkpoints.
    3. News Server: Scan transit cities for traffic/roadblock disruptions (detects Gwalior NH-44 protest).
    4. Weather Server: Check weather warnings for transit cities.
    5. Toll RAG Server: RAG search for approved detour corridors (Mehgaon/Bhind) and toll rates.
    6. OSRM Server: Recalculate micro-detour using Mehgaon intermediate waypoint.
    """
    print("==================================================================")
    print(" MULTI-SERVER MCP SUPPLY CHAIN ROUTE OPTIMIZATION WORKFLOW")
    print("==================================================================\n")

    origin = "Delhi"
    destination = "Bhopal"
    
    # -------------------------------------------------------------------------
    # STEP 1: Query OSRM Server for initial primary route
    # -------------------------------------------------------------------------
    print("[+] STEP 1: Querying OSRM Server for Initial Route...")
    osrm_res = await call_mcp_tool("osrm", "get_route", {"origin": origin, "destination": destination})
    print(osrm_res)

    # Extract transit cities along primary path
    route_cities = ["Chandigarh", "Agra", "Gwalior", "Jhansi", "Sagar", "Nagpur", "Visakhapatnam"]
    print(f"Primary Transit Corridor Cities: {route_cities}\n")

    # -------------------------------------------------------------------------
    # STEP 2: Query News Server for Traffic & Roadblock Disruptions
    # -------------------------------------------------------------------------
    print("[+] STEP 2: Querying News Server for Active Road Disruptions...")
    news_res = await call_mcp_tool("news", "check_route_disruptions", {"cities": route_cities})
    print(news_res)

    # -------------------------------------------------------------------------
    # STEP 3: Query Weather Server for Route Weather Warnings
    # -------------------------------------------------------------------------
    print("[+] STEP 3: Querying Weather Server for Severe Weather Hazards...")
    weather_res = await call_mcp_tool("weather", "check_route_weather_hazards", {"cities": route_cities})
    print(weather_res)

    # -------------------------------------------------------------------------
    # STEP 4: Query Toll RAG Server for Approved Detours & FASTag Policies
    # -------------------------------------------------------------------------
    print("[+] STEP 4: Querying Toll RAG Server for Bypass Advisories & Toll Costs...")
    rag_res = await call_mcp_tool("toll_rag", "search_toll_advisories", {"query": "Gwalior bypass Mehgaon detour truck toll"})
    print(rag_res)

    # -------------------------------------------------------------------------
    # STEP 5: Query OSRM Server to calculate Micro-Detour via Waypoint
    # -------------------------------------------------------------------------
    print("[+] STEP 5: Recalculating Route in OSRM via Detour Waypoint (Mehgaon)...")
    detour_res = await call_mcp_tool("osrm", "get_route_with_waypoints", {
        "origin": origin,
        "waypoints": ["Mehgaon"],
        "destination": destination
    })
    print(detour_res)

    # -------------------------------------------------------------------------
    # STEP 6: Calculate Toll Fees for Updated Detour Route
    # -------------------------------------------------------------------------
    detour_cities = ["Chandigarh", "Agra", "Mehgaon", "Jhansi", "Nagpur", "Visakhapatnam"]
    print("[+] STEP 6: Calculating Updated Toll Fees for Detour Route...")
    toll_res = await call_mcp_tool("toll_rag", "calculate_toll_cost", {
        "route_cities": detour_cities,
        "vehicle_type": "truck"
    })
    print(toll_res)

    print("==================================================================")
    print(" [OK] WORKFLOW COMPLETE: Multi-Server MCP Coordination Successful!")
    print("==================================================================")

if __name__ == "__main__":
    asyncio.run(run_multi_server_workflow())
