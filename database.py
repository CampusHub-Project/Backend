import aiomysql
import os

pool = None

async def init_db(app, loop):
    global pool
    pool = await aiomysql.create_pool(
        host=os.getenv('DB_HOST'),
        port=3306,
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        db=os.getenv('MYSQL_DATABASE'),
        loop=loop,
        autocommit=True
    )
    print("\n ---Veritabani baglantisi basarili!--- \n")

async def close_db(app, loop):
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()
        pool = None

async def execute_query(query, args=()):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, args)
            return cur.lastrowid

async def fetch_all(query, args=()):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            return await cur.fetchall()

async def fetch_one(query, args=()):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(query, args)
            return await cur.fetchone()