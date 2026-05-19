from pydantic import BaseModel, UUID4
from datetime import datetime

class MatchCreate(BaseModel):
    map_name:   str
    started_at: int | float | datetime

class MatchClose(BaseModel):
    winner_team: str
    ended_at:    int | float | datetime

class MatchResponse(BaseModel):
    id:          UUID4
    map_name:    str
    status:      str
    winner_team: str | None
    started_at:  datetime
    ended_at:    datetime | None

    model_config = {
        "from_attributes": True
    }