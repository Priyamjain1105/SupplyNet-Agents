import sys
import math
from typing import List, Dict, Any
from fastmcp import FastMCP

# Ensure UTF-8 output encoding on Windows
sys.stdout.reconfigure(encoding='utf-8')

# Create FastMCP server for Toll Data & Advisory RAG
mcp = FastMCP("TollRAGServer")

# Knowledge base of Toll Advisories, FASTag Circulars, and Highway Detour Rules
TOLL_KNOWLEDGE_BASE = [
    {
        "id": "KB-TOLL-01",
        "title": "NH-44 Gwalior - Jhansi Toll Corridor Rates",
        "content": "For 4-axle to 6-axle Heavy Commercial Vehicles (HCV/Trucks), the toll fee at Gwalior Toll Plaza is Rs. 385. FASTag lane 3 and 4 are operational 24/7. Cash payments incur a 100% penalty rate.",
        "keywords": ["gwalior", "nh-44", "jhansi", "hcv", "truck", "rate", "fastag"],
        "cost_hcv": 385
    },
    {
        "id": "KB-TOLL-02",
        "title": "Mehgaon Bypass Highway Circular (State Highway 19)",
        "content": "State Highway 19 via Mehgaon and Bhind serves as an approved commercial bypass during NH-44 disruptions in Gwalior. The Mehgaon toll booth charges Rs. 140 for multi-axle trucks. Road weight clearance is rated up to 40 metric tons.",
        "keywords": ["mehgaon", "bhind", "bypass", "detour", "sh-19", "gwalior", "toll"],
        "cost_hcv": 140
    },
    {
        "id": "KB-TOLL-03",
        "title": "Agra - Gwalior Expressway Toll Charges",
        "content": "Toll rate for heavy trucks at Agra Plaza on NH-44 is Rs. 420. Dynamic tolling applies during peak rush hours (08:00 to 11:00 AM). Ensure minimum FASTag balance of Rs. 1,000.",
        "keywords": ["agra", "gwalior", "expressway", "hcv", "truck", "fastag"],
        "cost_hcv": 420
    },
    {
        "id": "KB-TOLL-04",
        "title": "Nagpur Outer Ring Road Toll Advisory",
        "content": "Commercial vehicles bypassing Nagpur city center via Outer Ring Road pay a flat toll fee of Rs. 260. Overloaded trucks exceeding axle load limits will be turned back at weighbridge #2.",
        "keywords": ["nagpur", "ring road", "weighbridge", "toll", "hcv", "truck"],
        "cost_hcv": 260
    },
    {
        "id": "KB-TOLL-05",
        "title": "Visakhapatnam Port Highway Toll & Entry Policy",
        "content": "Port entry highway toll at Visakhapatnam for freight trucks is Rs. 310. RFID gate scanning is mandatory. Container trucks must present valid e-way bill documentation at checkpost.",
        "keywords": ["visakhapatnam", "port", "freight", "truck", "toll", "e-way"],
        "cost_hcv": 310
    }
]

@mcp.tool()
async def search_toll_advisories(query: str) -> str:
    """RAG Search over unstructured toll plaza advisories, FASTag rules, and highway detour regulations."""
    query_words = set(query.lower().split())
    scored_results = []
    
    for doc in TOLL_KNOWLEDGE_BASE:
        # Simple TF/keyword relevance score matching RAG vector indexing concept
        score = 0
        for word in query_words:
            if word in doc["title"].lower():
                score += 3
            if word in doc["content"].lower():
                score += 1
            if word in doc["keywords"]:
                score += 2
        if score > 0:
            scored_results.append((score, doc))
            
    scored_results.sort(key=lambda x: x[0], reverse=True)
    
    if not scored_results:
        return f"No specific toll advisories or circulars matching query '{query}'. Standard NHAI rates apply."
    
    response = f"=== Toll Advisory RAG Search Results for '{query}' ===\n"
    for score, doc in scored_results[:3]:
        response += f"📄 Document [{doc['id']}]: {doc['title']}\n"
        response += f"   Relevance Score: {score}\n"
        response += f"   Content: {doc['content']}\n"
        response += f"   Toll Rate (Trucks): Rs. {doc['cost_hcv']}\n\n"
    return response

@mcp.tool()
async def calculate_toll_cost(route_cities: List[str], vehicle_type: str = "truck") -> str:
    """Calculate estimated total toll cost for a sequence of transit cities along a route."""
    total_cost = 0
    breakdown = []
    
    multiplier = 1.0 if vehicle_type.lower() in ["truck", "hcv", "heavy"] else 0.5
    
    for city in route_cities:
        c_clean = city.strip().lower()
        matched = False
        for doc in TOLL_KNOWLEDGE_BASE:
            if c_clean in doc["keywords"] or c_clean in doc["title"].lower():
                cost = int(doc["cost_hcv"] * multiplier)
                total_cost += cost
                breakdown.append(f"{city.title()} Plaza ({doc['id']}): Rs. {cost}")
                matched = True
                break
        if not matched:
            # Default estimated toll for unlisted city plaza
            cost = int(200 * multiplier)
            total_cost += cost
            breakdown.append(f"{city.title()} Toll Gate (Est.): Rs. {cost}")
            
    res = f"=== TOLL COST ESTIMATE ({vehicle_type.upper()}) ===\n"
    res += "\n".join(f"- {b}" for b in breakdown) + "\n"
    res += f"----------------------------------------\n"
    res += f"Total Estimated Toll Cost: Rs. {total_cost}\n"
    return res

if __name__ == "__main__":
    if "--stdio" in sys.argv:
        mcp.run(transport="stdio")
    else:
        # Runs streamable HTTP server on port 8003
        mcp.run(transport="streamable-http", port=8003)

