# Multi-Server MCP Architecture for Supply Chain Route Optimization

This directory contains a **Multi-Server Model Context Protocol (MCP)** architecture designed for intelligent truck fleet routing and dynamic disruption handling.

---

## 🏛️ Multi-Server System Architecture

```
                       +-------------------------------+
                       |   Multi-Server MCP Client     |
                       |       (client.py)             |
                       +---------------+---------------+
                                       |
    +-------------------+--------------+--------------+-------------------+
    |                   |                             |                   |
    v                   v                             v                   v
+-------+           +-------+                     +-------+           +-------+
| News  |           |Weather|                     | Toll  |           | OSRM  |
|Server |           |Server |                     |  RAG  |           |Server |
| (8001)|           | (8002)|                     | (8003)|           | (8004)|
+-------+           +-------+                     +-------+           +-------+
```

---

## 🛰️ Included MCP Servers

### 1. **News Server** (`mcp/servers/news_server.py` | Port: `8001`)
Ingests and monitors traffic news, roadblocks, protests, and highway accidents.
- `get_traffic_news(city)`: Retrieves active news alerts for a specific location.
- `report_disruption(city, event_type, severity, details, lat, lng)`: Logs a new traffic event.
- `check_route_disruptions(cities)`: Checks an ordered list of transit cities for roadblock alerts.

### 2. **Weather Server** (`mcp/servers/weather_server.py` | Port: `8002`)
Monitors real-time weather and severe weather advisories along supply chain corridors.
- `get_city_weather(location)`: Fetches current temperature, condition, and road visibility.
- `get_weather_alerts(location)`: Returns active warnings (dense fog, heavy rainfall, storms).
- `check_route_weather_hazards(cities)`: Scans a full route sequence for weather hazards.

### 3. **Toll RAG Server** (`mcp/servers/toll_rag_server.py` | Port: `8003`)
Performs RAG / semantic search over unstructured toll plaza circulars, FASTag rules, and detour policies.
- `search_toll_advisories(query)`: Searches knowledge base for toll policies and approved bypass corridors.
- `calculate_toll_cost(route_cities, vehicle_type)`: Computes total toll charges for trucks along a route.

### 4. **OSRM Server** (`mcp/servers/osrm_server.py` | Port: `8004`)
Queries the Open Source Routing Machine (OSRM) for route geometries, distances, ETAs, and micro-detour waypoints.
- `geocode_location(location_name)`: Resolves city names into latitude & longitude coordinates.
- `get_route(origin, destination)`: Calculates primary driving route distance, ETA, and city sequence.
- `get_route_with_waypoints(origin, waypoints, destination)`: Calculates detour routes using intermediate waypoints (e.g. bypassing Gwalior via Mehgaon).
- `extract_route_checkpoints(origin, destination)`: Returns node sequence for truck tracking.

---

## 📁 Configuration Files

- [`mcp/mcp-http.json`](file:///c:/Users/priya/Downloads/Supply-Chain-Management/mcp/mcp-http.json): Configuration file for Streamable HTTP transport connecting to ports 8001..8004.
- [`mcp/mcp.json`](file:///c:/Users/priya/Downloads/Supply-Chain-Management/mcp/mcp.json): Configuration file for stdio transport.

---

## 🚀 How to Run

### Step 1: Activate Virtual Environment
```powershell
menv\Scripts\activate
```

### Step 2: Start All 4 MCP Servers
```powershell
python mcp/run_all_servers.py
```

### Step 3: Run the Multi-Server Client Workflow
In a separate terminal window:
```powershell
menv\Scripts\activate
python mcp/client.py
```

---

## 🚚 Example Workflow Output
The `client.py` script executes a full supply chain rerouting scenario:
1. **Route Initialized**: `Chandigarh ➔ Visakhapatnam` via `NH-44`.
2. **Disruption Detected**: `News Server` reports a **Protest Roadblock** on `NH-44` in `Gwalior`.
3. **Weather Check**: `Weather Server` verifies clear weather along detour options.
4. **Toll RAG Search**: `Toll RAG Server` retrieves approved bypass corridor via `Mehgaon` (State Highway 19).
5. **OSRM Reroute**: `OSRM Server` calculates micro-detour `Chandigarh ➔ Agra ➔ Mehgaon ➔ Visakhapatnam`.
6. **Cost Update**: `Toll RAG Server` computes updated toll fees for the truck.
