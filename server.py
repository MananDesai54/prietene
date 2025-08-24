import logging
from pyexpat import features
from typing import Any, Dict
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str) -> Dict[str, Any] | None:
    """Make a request to NWS API with proper error handling"""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url=url, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format error feature in to readable string"""
    props = feature["properties"]
    return f"""
Event: {props.get("event", "Unknown")}
Area: {props.get("areaDesc", "Unknown")}
Severity: {props.get("severity", "Unknown")}
Description: {props.get("description", "No Description available")}
Instructions: {props.get("instruction", "No Instructions available")}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get Weather alerts for a US state
    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """

    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    logging.debug(f"NWS alert {data}")

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found"
    if not data["features"]:
        return "No active alerts for this state"

    alerts = [format_alert(feature=feature) for feature in data["features"]]

    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(lat: float, lon: float) -> str:
    """Get Weather forecast for a location
    Args:
        lat: Latitude of the location
        lon: Longitude of the location
    """

    points_url = f"{NWS_API_BASE}/points/{lat},{lon}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return "Unable to fetch weather forecast for this location"

    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return "Unable to fetch weather forecast for this location"

    periods = forecast_data["properties"]["periods"]
    forecasts = []

    for period in periods[:5]:
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period["windSpeed"]} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

if __name__ == "__main__":
    mcp.run(transport="stdio")







