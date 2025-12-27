import aiohttp
import json
from src.config import logger

class WeatherService:

    @staticmethod
    async def get_current_weather(redis, city: str = "Istanbul"):
        cache_key = f"weather:{city.lower()}"
        
        if redis:
            cached_data = await redis.get(cache_key)
            if cached_data:
                logger.info(f"Weather fetched from Cache for {city}")
                return json.loads(cached_data), 200

        headers = {
            "User-Agent": "CampusHub-Project/1.0 (Student Project; contact@example.com)"
        }

        try:
            async with aiohttp.ClientSession(trust_env=True) as session:
                
                geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=tr&format=json"
                
                async with session.get(geo_url, headers=headers) as geo_resp:
                    if geo_resp.status != 200:
                        logger.error(f"Geo API Error: {geo_resp.status}")
                        return {"error": "Geocoding service unavailable"}, 503
                    
                    geo_data = await geo_resp.json()
                    
                    if not geo_data.get("results"):
                        return {"error": "City not found"}, 404
                        
                    lat = geo_data["results"][0]["latitude"]
                    lon = geo_data["results"][0]["longitude"]
                    city_name = geo_data["results"][0]["name"]

                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                
                async with session.get(weather_url, headers=headers) as weather_resp:
                    if weather_resp.status != 200:
                        logger.error(f"Weather API Error: {weather_resp.status}")
                        return {"error": "Weather service unavailable"}, 503
                        
                    w_data = await weather_resp.json()
                    current = w_data.get("current_weather", {})

                    weather_code = current.get("weathercode", 0)
                    description = WeatherService.get_weather_desc(weather_code)

                    weather_info = {
                        "city": city_name,
                        "temperature": current.get("temperature"),
                        "wind_speed": current.get("windspeed"),
                        "description": description,
                        "latitude": lat,
                        "longitude": lon
                    }

                    if redis:
                        await redis.set(cache_key, json.dumps(weather_info), ex=900)
                    
                    logger.info(f"Weather fetched from Open-Meteo for {city}")
                    return {"weather": weather_info}, 200

        except aiohttp.ClientConnectorError as e:
            logger.error(f"Connection Error: {str(e)}")
            return {"error": "Internet connection failed inside Docker"}, 500
        except Exception as e:
            logger.error(f"Weather Service General Error: {str(e)}")
            return {"error": f"Service Error: {str(e)}"}, 500

    @staticmethod
    def get_weather_desc(code):
        codes = {
            0: "Açık", 1: "Çoğunlukla Açık", 2: "Parçalı Bulutlu", 3: "Kapalı",
            45: "Sisli", 48: "Kırağı Sis", 51: "Hafif Çiseleme", 53: "Çiseleme",
            55: "Yoğun Çiseleme", 61: "Hafif Yağmur", 63: "Yağmur", 65: "Şiddetli Yağmur",
            71: "Hafif Kar", 73: "Kar Yağışlı", 75: "Yoğun Kar", 95: "Fırtına"
        }
        return codes.get(code, "Bilinmiyor")