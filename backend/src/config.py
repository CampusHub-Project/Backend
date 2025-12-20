import os

# Docker-compose.yml dosyasındaki ayarlara göre güncellendi:
# Kullanıcı: hubuser, Şifre: hubpass, Port: 3307 (Dış port)
DB_URL = os.getenv("DB_URL", "mysql://hubuser:hubpass@localhost:3307/campushub")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

# Tortoise ORM Ayarları
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}