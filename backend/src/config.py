import os
import logging
import sys

# --- LOGGING YAPILANDIRMASI ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CampusHub")

# --- DİĞER AYARLAR (GÜVENLİ HALİ) ---
# Artık "default" değer olarak şifre yazmıyoruz.
# Eğer .env okunamazsa program hata verip durmalı, yanlış şifreyle çalışmamalı.

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    raise ValueError("KRİTİK HATA: DB_URL ortam değişkeni bulunamadı! .env dosyasını kontrol edin.")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379") # Redis localde şifresiz olabilir, bu kalabilir.

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("KRİTİK HATA: SECRET_KEY ayarlanmamış! Güvenlik için zorunludur.")

TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["src.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}