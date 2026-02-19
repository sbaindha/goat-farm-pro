from ninja import Router
import time
from .weather_service import WeatherService

# auth=None — weather sabke liye open hai (frontend bina login ke use karta hai)
weather_api = Router(tags=["Weather Live"])


@weather_api.get("/current/", auth=None)
def get_current_weather(request, lat: float = None, lng: float = None):
    """
    Real-time current weather.
    Server-side FileBasedCache: 15 min TTL.
    Response mein from_cache + data_age_sec bhi aata hai.
    """
    try:
        w = WeatherService.get_current_weather(lat, lng)
        if w:
            now       = int(time.time())
            fetched   = w.get("fetched_at", now)
            age_sec   = now - fetched
            age_min   = age_sec // 60

            return {
                "success":       True,
                "location":      w.get("location"),
                "temperature":   w.get("temp"),
                "feels_like":    w.get("feels_like"),
                "humidity":      w.get("humidity"),
                "wind":          w.get("wind"),
                "wind_dir":      w.get("wind_dir"),
                "pressure":      w.get("pressure"),
                "visibility":    w.get("visibility"),
                "uv_index":      w.get("uv_index"),
                "condition":     w.get("condition"),
                "sunrise":       w.get("sunrise"),
                "sunset":        w.get("sunset"),
                # Cache info — frontend ke liye
                "from_cache":    w.get("from_cache", False),
                "data_age_sec":  age_sec,
                "data_age_min":  age_min,
                "is_realtime":   age_min < 16,
                "is_demo":       w.get("is_demo", False),
            }
    except Exception as e:
        print(f"❌ weather/current error: {e}")
    return {"success": False, "location": "", "temperature": 0}


@weather_api.get("/cache-clear/", auth=None)
def clear_weather_cache(request):
    """Cache manually clear karo — stale demo data hatane ke liye"""
    try:
        from django.core.cache import cache
        # Weather related saari keys delete karo
        cache.delete_many([
            f"weather_cur_{round(WeatherService.DEFAULT_LAT, 2)}_{round(WeatherService.DEFAULT_LNG, 2)}",
            f"weather_fore_{round(WeatherService.DEFAULT_LAT, 2)}_{round(WeatherService.DEFAULT_LNG, 2)}",
        ])
        # Poora cache clear karo (safest option)
        cache.clear()
        return {"success": True, "message": "Cache cleared successfully"}
    except Exception as e:
        return {"success": False, "message": str(e)}


@weather_api.get("/forecast/", auth=None)
def get_forecast(request, lat: float = None, lng: float = None, days: int = 10):
    """7-day forecast. Cache TTL: 1 hour."""
    try:
        forecast = WeatherService.get_forecast(lat, lng, days)
        if forecast:
            return {
                "success": True,
                "forecast": [
                    {
                        "date":      f["date"],
                        "temp":      f["temp"],
                        "temp_min":  f["temp_min"],
                        "temp_max":  f["temp_max"],
                        "humidity":  f["humidity"],
                        "rain":      f["rain"],
                        "condition": f["condition"],
                    }
                    for f in forecast
                ],
            }
    except Exception as e:
        print(f"❌ weather/forecast error: {e}")
    return {"success": False, "forecast": []}


@weather_api.get("/alerts/", auth=None)
def get_alerts(request, lat: float = None, lng: float = None):
    try:
        current = WeatherService.get_current_weather(lat, lng)
        alerts  = WeatherService.get_weather_alerts(current)
        return {"success": True, "alerts": alerts}
    except Exception as e:
        print(f"❌ weather/alerts error: {e}")
    return {"success": False, "alerts": []}


@weather_api.get("/health-recommendations/", auth=None)
def get_health(request, lat: float = None, lng: float = None):
    try:
        current = WeatherService.get_current_weather(lat, lng)
        tips    = WeatherService.get_health_impact(current)
        return {
            "success":         True,
            "temperature":     current.get("temp") if current else None,
            "condition":       current.get("condition") if current else None,
            "recommendations": tips,
        }
    except Exception as e:
        print(f"❌ weather/health error: {e}")
    return {"success": False, "recommendations": []}
