from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend
from src.database import init_db, close_db
from src.config import REDIS_URL, logger
from src.routes.auth import auth_bp
from src.routes.clubs import clubs_bp
from src.routes.events import events_bp
from src.routes.comments import comments_bp
from src.routes.users import users_bp
from src.routes.notifications import notif_bp
from src.routes.admin import admin_bp  # <--- YENİ EKLENDİ
from redis import asyncio as aioredis
from sanic_limiter import Limiter, get_remote_address

app = Sanic("CampusHubAPI")
app.config.CORS_ORIGINS = "*"

limiter = Limiter(
    app, 
    global_limits=["60 per minute"], 
    key_func=get_remote_address,
    storage_uri=REDIS_URL
)

app.blueprint(auth_bp)
app.blueprint(clubs_bp)
app.blueprint(events_bp)
app.blueprint(comments_bp)
app.blueprint(users_bp)
app.blueprint(notif_bp)
app.blueprint(admin_bp) # <--- YENİ EKLENDİ

Extend(app)

@app.before_server_start
async def setup_db(app, loop):
    logger.info("Server Starting... Connecting to DB and Redis.")
    await init_db()
    app.ctx.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
    logger.info("Connected to Database and Redis.")

@app.after_server_stop
async def stop_db(app, loop):
    logger.info("Server Stopping... Closing connections.")
    await close_db()
    await app.ctx.redis.close()
    logger.info("Connections closed.")

@app.get("/")
async def health_check(request):
    return json({"status": "active", "message": "CampusHub Backend is running!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)