import os
import logging
import sys

# --- LOGGING YAPILANDIRMASI ---
# Logların formatı: Zaman [Seviye] İsim: Mesaj
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout) # Çıktıyı konsola (Docker loglarına) ver
    ]
)
# Uygulama genelinde kullanacağımız logger nesnesi
logger = logging.getLogger("CampusHub")

# --- DİĞER AYARLAR ---
DB_URL = os.getenv("DB_URL", "mysql://hubuser:hubpass@localhost:3307/campushub")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}