from sanic import Sanic
from sanic.response import json
from dotenv import load_dotenv
from database import init_db, close_db, fetch_all
from auth import auth_bp

load_dotenv()

app = Sanic("CampusHub")

app.blueprint(auth_bp)

app.register_listener(init_db, "before_server_start")
app.register_listener(close_db, "after_server_stop")

@app.route("/")
async def test(request):
    users = await fetch_all("SELECT * FROM Users")
    return json({
        "message": "CampusHub Backend Çalışıyor!", 
        "users": users
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)