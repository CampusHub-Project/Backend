import os
from sanic import Sanic
from sanic.response import json
from dotenv import load_dotenv
from tortoise.contrib.sanic import register_tortoise # <-- YENİ

# Blueprintleri import et
from auth import auth_bp
from clubs import clubs_bp
from events import events_bp
from participants import participants_bp
from comments import comments_bp
from notifications import notifications_bp
load_dotenv()

app = Sanic("CampusHub")

# Blueprintleri ekle
app.blueprint(auth_bp)
app.blueprint(clubs_bp)
app.blueprint(events_bp)
app.blueprint(participants_bp)
app.blueprint(comments_bp)
app.blueprint(notifications_bp)

@app.route("/")
async def test(request):
    return json({"message": "CampusHub Backend (ORM Mode) Calisiyor!", "status": "success"})

DB_URL = f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('DB_HOST')}:3306/{os.getenv('MYSQL_DATABASE')}"

register_tortoise(
    app,
    db_url=DB_URL,
    modules={"models": ["models"]}, # models.py dosyasını okumasını söylüyoruz
    generate_schemas=True, # Tablolar yoksa OTOMATİK OLUŞTURUR (Development için harika)
)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)