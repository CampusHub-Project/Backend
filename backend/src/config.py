import os

# Çevresel değişkenleri al (Docker'dan gelenler)
DB_URL = os.getenv("DB_URL", "mysql://root:root@localhost:3306/campushub")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

# Tortoise ORM Ayarları
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"], # aerich migrasyon için
            "default_connection": "default",
        }
    },
}