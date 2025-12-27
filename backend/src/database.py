from tortoise import Tortoise
from src.config import DB_URL

async def init_db():
    await Tortoise.init(
        db_url=DB_URL,
        modules={'models': ['src.models']}
    )
    await Tortoise.generate_schemas(safe=True) 

async def close_db():
    await Tortoise.close_connections()