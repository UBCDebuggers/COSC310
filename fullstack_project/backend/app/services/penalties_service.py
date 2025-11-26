from app.repositories.penalties_repo import load_all, save_all
from app.schemas.penalties import PenaltyCreate, PenaltyUpdate, Pentalty
from fastapi import HTTPException, status