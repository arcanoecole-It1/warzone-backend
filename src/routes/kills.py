from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
from src.models.match import Match
from src.schemas.kill import KillCreate, KillResponse, KillBatchCreate
from src.services.kill_service import record_kill, record_kills_batch

router = APIRouter(prefix="/kills", tags=["kills"])

@router.post("/", response_model=KillResponse, status_code=201)
async def create_kill(body: KillCreate, db: Session = Depends(get_db)):
    # Vérifie que la partie est bien en cours
    match = db.query(Match).filter_by(id=body.match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    if match.status != "ongoing":
        raise HTTPException(status_code=409, detail="La partie est terminée")
    return await record_kill(body, db)

@router.post("/batch", response_model=list[KillResponse], status_code=201)
async def create_kills_batch(body: KillBatchCreate, db: Session = Depends(get_db)):
    match_ids = {kill.match_id for kill in body.kills}
    if not match_ids:
        return []

    matches = db.query(Match).filter(Match.id.in_(match_ids)).all()
    if len(matches) != len(match_ids):
        raise HTTPException(status_code=404, detail="Une ou plusieurs parties sont introuvables")

    for match in matches:
        if match.status != "ongoing":
            raise HTTPException(status_code=409, detail="Une ou plusieurs parties sont terminées")

    return await record_kills_batch(body.kills, db)