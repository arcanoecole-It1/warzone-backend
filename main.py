from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
import bcrypt

from src.routes import players , matches , kills , admin , analytics , leaderboard , stats
from src.database import engine, Base, SessionLocal
from src.models.admin import Admin
from src.config import settings

Base.metadata.create_all(bind=engine)

def ensure_ban_column() -> None:
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = [col["name"] for col in inspector.get_columns("users")]
    if "is_banned" in columns:
        return

    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT FALSE")
        )

ensure_ban_column()

def create_default_admin() -> None:
    db = SessionLocal()
    try:
        existing_admin = db.query(Admin).first()
        if existing_admin is None:
            default_username = settings.DEFAULT_ADMIN_USERNAME
            default_password = settings.DEFAULT_ADMIN_PASSWORD
            password_hash = bcrypt.hashpw(default_password.encode(), bcrypt.gensalt()).decode()
            db.add(Admin(username=default_username, password_hash=password_hash))
            db.commit()
    finally:
        db.close()

@app.get("/health")
def healthcheck():
    return {"status": "healthy", "service": "warzone-api"}
    
create_default_admin()

app = FastAPI(title="Warzone API", description="API pour gérer les joueurs, les matchs et les statistiques de Warzone")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router)
app.include_router(matches.router)
app.include_router(kills.router)
app.include_router(leaderboard.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(stats.router)

