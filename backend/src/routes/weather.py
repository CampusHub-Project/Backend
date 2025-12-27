from sanic import Blueprint
from sanic.response import json
from src.services.weather_service import WeatherService

weather_bp = Blueprint("weather", url_prefix="/weather")

@weather_bp.get("/")
async def get_weather(request):
    city = request.args.get("city", "Ankara")
    
    redis = request.app.ctx.redis
    
    result, status = await WeatherService.get_current_weather(redis, city)
    return json(result, status=status)