import os
import requests
import logging
import time

logger = logging.getLogger(__name__)



# Django cache — settings.py mein configure hai (FileBasedCache)
try:
    from django.core.cache import cache as django_cache
    from django.conf import settings
    WEATHER_TTL   = getattr(settings, "WEATHER_CACHE_TTL",  15 * 60)
    FORECAST_TTL  = getattr(settings, "FORECAST_CACHE_TTL", 60 * 60)
    GEO_TTL       = getattr(settings, "GEO_CACHE_TTL",      1 * 24 * 3600)
    DJANGO_CACHE  = True
except Exception:
    # Fallback: agar Django setup nahi hua (e.g. direct script run)
    django_cache  = None
    WEATHER_TTL   = 15 * 60
    FORECAST_TTL  = 60 * 60
    GEO_TTL       = 7 * 24 * 3600
    DJANGO_CACHE  = False


def _get(key):
    """Cache se value lo"""
    if DJANGO_CACHE:
        return django_cache.get(key)
    return None

def _set(key, value, ttl):
    """Cache mein value save karo"""
    if DJANGO_CACHE:
        django_cache.set(key, value, ttl)


class WeatherService:
    # API Key har call pe fresh read hoti hai — class load time pe nahi
    # Isse server restart ke bina bhi .env changes apply ho jaate hain
    DEFAULT_LAT  = 26.9124
    DEFAULT_LNG  = 75.7873
    BASE_URL     = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

    @classmethod
    def _get_api_key(cls):
        """API key lo — Django settings > environment variable order mein"""
        # 1st: Django settings se (settings.py ne .env load kiya hoga)
        try:
            from django.conf import settings as dj_settings
            key = getattr(dj_settings, "WEATHER_API_KEY", None)
            if key and str(key).strip():
                return str(key).strip()
        except Exception:
            pass
        # 2nd: Direct environment variable
        key = os.environ.get("WEATHER_API_KEY", "").strip()
        return key

    @staticmethod
    def _loc_key(lat, lng):
        return f"weather_loc_{round(lat, 2)}_{round(lng, 2)}"

    @staticmethod
    def _cur_key(lat, lng):
        return f"weather_cur_{round(lat, 2)}_{round(lng, 2)}"

    @staticmethod
    def _fore_key(lat, lng):
        return f"weather_fore_{round(lat, 2)}_{round(lng, 2)}"

    @classmethod
    def _demo_weather(cls, lat, lng):
        """
        Demo data — WEATHER_API_KEY set nahi hai tab use hota hai.
        Dashboard khaali nahi dikhega, demo values dikhega.
        """
        import time as t
        location = cls.get_location_name(lat, lng) or "Your Farm Location"
        return {
            "location":     location,
            "temp":         28.0,
            "feels_like":   30.0,
            "humidity":     65.0,
            "wind":         12.0,
            "wind_dir":     180,
            "pressure":     1013.0,
            "visibility":   10.0,
            "uv_index":     6,
            "condition":    "Partly Cloudy",
            "sunrise":      "06:15:00",
            "sunset":       "18:45:00",
            "fetched_at":   int(t.time()),
            "from_cache":   False,
            "is_demo":      True,   # frontend mein "(Demo)" badge dikhao
        }

    # ── Reverse Geocoding ────────────────────────────────────────────────────
    @classmethod
    def get_location_name(cls, lat, lng):
        """Coordinates → City, State  (OpenStreetMap Nominatim — free, no key)"""
        key = cls._loc_key(lat, lng)
        cached = _get(key)
        if cached:
            logger.debug(f"Geo cache hit: {cached}")
            return cached

        try:
            res = requests.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"lat": lat, "lon": lng, "format": "json",
                        "zoom": 10, "addressdetails": 1},
                headers={"User-Agent": "GoatFarmPro/5.0"},
                timeout=5,
            )
            res.raise_for_status()
            addr = res.json().get("address", {})

            city =  (addr.get("village") or addr.get("city") or addr.get("town") or
                     addr.get("state_district") or addr.get("county") or  addr.get("suburb") or "")
            state = addr.get("state", "")
            name  = f"{city}, {state}" if city and state else (city or state or "")

            _set(key, name, GEO_TTL)   # 1 din ke liye cache — naam kabhi nahi badlega
            logger.info(f"Geo resolved: {name}")
            return name

        except Exception as e:
            logger.warning(f"Reverse geocoding failed: {e}")
            return None

    # ── Current Weather ──────────────────────────────────────────────────────
    @classmethod
    def get_current_weather(cls, lat=None, lng=None):
        lat = lat or cls.DEFAULT_LAT
        lng = lng or cls.DEFAULT_LNG
        key = cls._cur_key(lat, lng)

        # Cache check
        cached = _get(key)
        if cached:
            cached["from_cache"] = True
            logger.info(f"Weather cache HIT for {key}")
            return cached

        # API key check — agar nahi hai to demo data return karo
        api_key = cls._get_api_key()
        if not api_key:
            logger.warning("WEATHER_API_KEY not set — returning demo data")
            return cls._demo_weather(lat, lng)

        # Fresh API call
        try:
            url    = f"{cls.BASE_URL}{lat},{lng}"
            params = {
                "key":         api_key,
                "unitGroup":   "metric",
                "include":     "current",   # sirf current — fast & free quota save
                "contentType": "json",
                "elements":    "temp,feelslike,humidity,windspeed,winddir,"
                               "pressure,visibility,uvindex,conditions,"
                               "sunrise,sunset",
            }
            logger.info(f"Weather API CALL: {lat},{lng}")
            res = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data    = res.json()
            current = data.get("currentConditions", {})

            # Location name
            location = cls.get_location_name(lat, lng)
            if not location:
                raw    = data.get("resolvedAddress", "")
                parts  = [p.strip() for p in raw.split(",") if p.strip()]
                named  = [p for p in parts
                          if not all(c in "0123456789.-+ " for c in p)]
                location = ", ".join(named[:2]) if named else raw

            result = {
                "location":     location,
                "temp":         current.get("temp"),
                "feels_like":   current.get("feelslike"),
                "humidity":     current.get("humidity"),
                "wind":         current.get("windspeed"),
                "wind_dir":     current.get("winddir"),
                "pressure":     current.get("pressure"),
                "visibility":   current.get("visibility"),
                "uv_index":     current.get("uvindex"),
                "condition":    current.get("conditions"),
                "sunrise":      current.get("sunrise"),
                "sunset":       current.get("sunset"),
                "fetched_at":   int(time.time()),
                "from_cache":   False,
            }

            # Django FileBasedCache mein store karo
            _set(key, result, WEATHER_TTL)
            logger.info(f"Weather cached: {location} for {WEATHER_TTL}s")
            return result

        except requests.exceptions.Timeout:
            logger.error("Weather API timeout")
            return None
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return None

    # ── Forecast ─────────────────────────────────────────────────────────────
    @classmethod
    def get_forecast(cls, lat=None, lng=None, days=10):
        lat = lat or cls.DEFAULT_LAT
        lng = lng or cls.DEFAULT_LNG
        key = cls._fore_key(lat, lng)

        cached = _get(key)
        if cached:
            logger.info(f"Forecast cache HIT for {key}")
            return cached

        # API key nahi hai — demo forecast do
        api_key = cls._get_api_key()
        if not api_key:
            logger.warning("WEATHER_API_KEY not set — returning demo forecast")
            from datetime import date, timedelta
            today = date.today()
            return [
                {
                    "date":      str(today + timedelta(days=i)),
                    "temp":      27 + i,
                    "temp_min":  22 + i,
                    "temp_max":  32 + i,
                    "humidity":  60 + i * 2,
                    "rain":      10 + i * 5,
                    "condition": "Partly Cloudy",
                }
                for i in range(days)
            ]

        try:
            url    = f"{cls.BASE_URL}{lat},{lng}"
            params = {
                "key":         api_key,
                "unitGroup":   "metric",
                "include":     "days",
                "contentType": "json",
                "elements":    "datetime,temp,tempmin,tempmax,humidity,"
                               "precipprob,conditions",
            }
            res  = requests.get(url, params=params, timeout=10)
            res.raise_for_status()
            data = res.json()

            forecast = [
                {
                    "date":      d["datetime"],
                    "temp":      d["temp"],
                    "temp_min":  d["tempmin"],
                    "temp_max":  d["tempmax"],
                    "humidity":  d["humidity"],
                    "rain":      d.get("precipprob", 0),
                    "condition": d["conditions"],
                }
                for d in data.get("days", [])[:days]
            ]

            _set(key, forecast, FORECAST_TTL)
            logger.info(f"Forecast cached for {FORECAST_TTL}s")
            return forecast

        except Exception as e:
            logger.error(f"Forecast error: {e}")
            return []

    # ── Alerts ───────────────────────────────────────────────────────────────
    @classmethod
    def get_weather_alerts(cls, current):
        if not current:
            return []
        alerts = []
        temp     = current.get("temp", 0) or 0
        humidity = current.get("humidity", 0) or 0
        wind     = current.get("wind", 0) or 0

        if temp > 40:   alerts.append("🔥 Extreme Heat — take immediate action")
        elif temp > 35: alerts.append("🌡️ High Temperature Alert")
        if temp < 5:    alerts.append("❄️ Cold Alert — protect goats")
        if humidity > 85: alerts.append("💧 Very High Humidity — disease risk high")
        elif humidity > 75: alerts.append("💧 High Humidity")
        if wind > 40:   alerts.append("💨 Strong Wind Alert")
        return alerts

    # ── Health Tips ──────────────────────────────────────────────────────────
    @classmethod
    def get_health_impact(cls, current):
        if not current:
            return []
        tips = []
        temp     = current.get("temp", 20) or 20
        humidity = current.get("humidity", 50) or 50

        if temp > 35:
            tips.append("🥤 Extra water — 4+ litres per goat")
            tips.append("🌿 Shade mandatory during 11am–4pm")
        elif temp > 30:
            tips.append("🥤 Increase water supply")
        if temp < 10:
            tips.append("🔥 Extra bedding, close pen vents at night")
        if humidity > 75:
            tips.append("🧹 Clean pen daily — hoof rot risk high")
        return tips
