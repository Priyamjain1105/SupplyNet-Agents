import sys
import httpx
from typing import List, Dict, Any
from fastmcp import FastMCP

# Ensure UTF-8 output encoding on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Create FastMCP server for Weather Monitoring
mcp = FastMCP("WeatherServer")

# Known severe weather alerts for supply chain corridors
WEATHER_ALERTS_DB: Dict[str, Dict[str, Any]] = {
    "gondia": {
        "condition": "Severe Cyclonic Storm & Heavy Rainfall",
        "severity": "CRITICAL",
        "visibility_km": 1.2,
        "wind_speed_kmh": 65,
        "advisory": "Flash flood warning on regional highways. Heavy vehicles advised to halt or detour.",
    },
    "gwalior": {
        "condition": "Clear Sky",
        "severity": "NONE",
        "visibility_km": 10.0,
        "wind_speed_kmh": 12,
        "advisory": "Normal driving conditions.",
    },
    "agra": {
        "condition": "Moderate Dense Fog",
        "severity": "LOW",
        "visibility_km": 4.0,
        "wind_speed_kmh": 8,
        "advisory": "Exercise caution during night driving.",
    }
}

@mcp.tool()
async def get_city_weather(location: str) -> str:
    """Get current weather details and road visibility for a transit city."""
    loc_key = location.strip().lower()
    
    # Try fetching live data from wttr.in with timeout
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(f"https://wttr.in/{location}?format=j1")
            if resp.status_code == 200:
                data = resp.json()
                curr = data["current_condition"][0]
                area = data["nearest_area"][0]["areaName"][0]["value"]
                temp_c = curr.get("temp_C", "N/A")
                desc = curr.get("weatherDesc", [{}])[0].get("value", "Clear")
                vis = curr.get("visibility", "10")
                wind = curr.get("windspeedKmph", "10")
                return f"Weather in {area}: {temp_c}°C, Condition: {desc}, Visibility: {vis}km, Wind: {wind} km/h."
    except Exception:
        pass

    # Fallback / Local Alert lookup
    if loc_key in WEATHER_ALERTS_DB:
        info = WEATHER_ALERTS_DB[loc_key]
        return f"Weather in {location.title()}: {info['condition']} (Severity: {info['severity']}). Visibility: {info['visibility_km']}km. Advisory: {info['advisory']}"
    
    return f"Weather in {location.title()}: 28°C, Clear Sky, Visibility: 10km, Wind: 15 km/h. Normal transit conditions."

@mcp.tool()
async def get_weather_alerts(location: str) -> str:
    """Check for active severe weather alerts (heavy rain, storms, fog) for a specific city."""
    loc_key = location.strip().lower()
    if loc_key in WEATHER_ALERTS_DB and WEATHER_ALERTS_DB[loc_key]["severity"] != "NONE":
        info = WEATHER_ALERTS_DB[loc_key]
        return f"⚠️ WEATHER ALERT for {location.title()} [{info['severity']}]: {info['condition']}. {info['advisory']}"
    return f"No severe weather warnings active for {location.title()}."

@mcp.tool()
async def check_route_weather_hazards(cities: List[str]) -> str:
    """Check a sequence of transit cities for severe weather hazards affecting truck routing."""
    hazards = []
    for city in cities:
        c_key = city.strip().lower()
        if c_key in WEATHER_ALERTS_DB and WEATHER_ALERTS_DB[c_key]["severity"] in ["MEDIUM", "HIGH", "CRITICAL"]:
            hazards.append((city.title(), WEATHER_ALERTS_DB[c_key]))
    
    if not hazards:
        return "All cities along the route have clear weather conditions without severe alerts."
    
    report = f"=== WEATHER HAZARD REPORT ({len(hazards)} warning(s)) ===\n"
    for city, h in hazards:
        report += f"🌧️ City: {city} | Severity: {h['severity']} | Condition: {h['condition']}\n"
        report += f"   Visibility: {h['visibility_km']} km | Advisory: {h['advisory']}\n"
    return report

if __name__ == "__main__":
    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        # Runs streamable HTTP server on port 8002
        mcp.run(transport="streamable-http", port=8002)

