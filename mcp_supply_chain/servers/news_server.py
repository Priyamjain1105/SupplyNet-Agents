import sys
import asyncio
from typing import List, Dict, Any
from fastmcp import FastMCP

# Ensure UTF-8 output encoding on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Create FastMCP server for News and Disruption Monitoring
mcp = FastMCP("NewsServer")

# In-memory store for active traffic and news disruptions along major corridors
DISRUPTIONS_DB: List[Dict[str, Any]] = [
    {
        "id": "DIS-101",
        "city": "Gwalior",
        "location": "NH-44 Gwalior Bypass",
        "event_type": "PROTEST_ROADBLOCK",
        "severity": "HIGH",
        "title": "Farmer Protest causing 4-hour traffic standstill on NH-44 near Gwalior",
        "details": "Major roadblock reported on NH-44 highway near Gwalior. Heavy commercial vehicles advised to divert via Mehgaon / Bhind corridor.",
        "coordinates": {"lat": 26.2183, "lng": 78.1828},
    },
    {
        "id": "DIS-102",
        "city": "Nagpur",
        "location": "Outer Ring Road Junction",
        "event_type": "HIGHWAY_REPAIR",
        "severity": "MEDIUM",
        "title": "Bridge repair work slowing traffic near Nagpur",
        "details": "Single lane traffic movement due to flyover joint replacement. Expect 20-30 min delays.",
        "coordinates": {"lat": 21.1458, "lng": 79.0882},
    }
]

@mcp.tool()
async def get_traffic_news(city: str) -> str:
    """Get active traffic, news, protests, or roadblock disruptions for a given city or highway node."""
    city_clean = city.strip().lower()
    matches = [d for d in DISRUPTIONS_DB if d["city"].lower() == city_clean or city_clean in d["location"].lower()]
    
    if not matches:
        return f"No active traffic disruptions or roadblocks reported for '{city}'. Route clear."
    
    result = f"=== Traffic & News Alerts for {city} ===\n"
    for item in matches:
        result += f"- [{item['severity']}] {item['title']}\n"
        result += f"  Location: {item['location']}\n"
        result += f"  Event Type: {item['event_type']}\n"
        result += f"  Details: {item['details']}\n"
        result += f"  Coordinates: Lat {item['coordinates']['lat']}, Lng {item['coordinates']['lng']}\n"
    return result

@mcp.tool()
async def report_disruption(city: str, event_type: str, severity: str, details: str, lat: float = 0.0, lng: float = 0.0) -> str:
    """Report a new traffic or news disruption for a city corridor (e.g. ACCIDENT, PROTEST, ROADBLOCK)."""
    disruption_id = f"DIS-{len(DISRUPTIONS_DB) + 101}"
    new_event = {
        "id": disruption_id,
        "city": city,
        "location": f"{city} Highway Corridor",
        "event_type": event_type.upper(),
        "severity": severity.upper(),
        "title": f"{event_type.replace('_', ' ').title()} reported in {city}",
        "details": details,
        "coordinates": {"lat": lat, "lng": lng}
    }
    DISRUPTIONS_DB.append(new_event)
    return f"Successfully logged disruption '{disruption_id}' for {city} with severity {severity}."

@mcp.tool()
async def check_route_disruptions(cities: List[str]) -> str:
    """Check a list of planned transit cities for active news/traffic disruptions."""
    affected = []
    for c in cities:
        c_clean = c.strip().lower()
        matches = [d for d in DISRUPTIONS_DB if d["city"].lower() == c_clean]
        if matches:
            affected.extend(matches)
    
    if not affected:
        return "All cities along the planned route are free of reported news/traffic disruptions."
    
    report = f"=== ROUTE DISRUPTION WARNING ({len(affected)} issue(s) detected) ===\n"
    for d in affected:
        report += f"⚠️ City: {d['city']} | Severity: {d['severity']} | Event: {d['event_type']}\n"
        report += f"   Summary: {d['title']}\n"
        report += f"   Recommended Action: Bypass via neighboring corridor.\n\n"
    return report

if __name__ == "__main__":
    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        # Runs streamable HTTP server on port 8001
        mcp.run(transport="streamable-http", port=8001)

