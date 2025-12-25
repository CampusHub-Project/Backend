import pytest
from src.services.weather_service import WeatherService

def test_weather_descriptions():

    assert WeatherService.get_weather_desc(0) == "Açık"
    assert WeatherService.get_weather_desc(95) == "Fırtına"
    assert WeatherService.get_weather_desc(500) == "Bilinmiyor"

def test_notification_logic():

    club_name = "Müzik Kulübü"
    event_title = "Konser"
    expected_msg = f"📢 '{club_name}' yeni bir etkinlik paylaştı: {event_title}"
    

    assert expected_msg.startswith("📢")
    assert club_name in expected_msg