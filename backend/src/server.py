from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend
from src.database import init_db, close_db
from src.config import REDIS_URL
from src.routes.auth import auth_bp
from src.routes.clubs import clubs_bp   # <--- YENİ
from src.routes.events import events_bp # <--- YENİ
from src.routes.comments import comments_bp
from src.routes.users import users_bp
from src.routes.notifications import notif_bp
from redis import asyncio as aioredis

app = Sanic("CampusHubAPI")
app.config.CORS_ORIGINS = "*"

app.blueprint(auth_bp)
app.blueprint(clubs_bp)   # <--- YENİ
app.blueprint(events_bp)  # <--- YENİ
app.blueprint(comments_bp)
app.blueprint(users_bp)
app.blueprint(notif_bp)

Extend(app)


@app.before_server_start
async def setup_db(app, loop):
    await init_db()
    app.ctx.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

@app.after_server_stop
async def stop_db(app, loop):
    await close_db()
    await app.ctx.redis.close()

@app.get("/")
async def health_check(request):
    return json({"status": "active", "message": "CampusHub Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
    