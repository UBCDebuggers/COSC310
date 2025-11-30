from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.ratings import router as ratings_router
from app.routers.users import router as users_router
from app.routers.watchlist import router as watchlist_router
from app.routers.history import router as history_router
from app.routers.library import router as library_router
from app.routers.analytics import router as analytics_router
from app.routers.waitlist import router as waitlist_router
from app.routers.recommend import router as recommend_router
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timezone
from app.services import analytics_service
from app.services.penalties_service import deactivate_penalty, get_penalties
from app.services.waitlist_service import get_active_waitlists, update_waitlists

scheduler = AsyncIOScheduler()

def analytics_refresh():
    analytics_service.rebuild_analytics()

def waitlists_refresh():
    books_with_waitlists = get_active_waitlists()
    for isbn in books_with_waitlists:
        update_waitlists(isbn)
        
def penalties_refresh():
    active_penalties = None
    try:
        active_penalties = get_penalties()
    except HTTPException:
        pass
    if not active_penalties:
        return
    current_date = datetime.now(timezone.utc)
    for penalty in active_penalties:
        if penalty.expiry_date < current_date:
            deactivate_penalty(penalty.penalty_id)
        
@asynccontextmanager
async def lifespan(app: FastAPI):    
    if scheduler.running:
        scheduler.remove_all_jobs()
        scheduler.shutdown()
    
    scheduler.add_job(
        waitlists_refresh, 
        trigger=IntervalTrigger(seconds=10), 
        id="refresh-00",
        replace_existing=True
    )
    scheduler.add_job(
        penalties_refresh,
        trigger=IntervalTrigger(minutes=1),
        id="refresh-01",
        replace_existing= True
    )
    scheduler.add_job(
        analytics_refresh,
        trigger=IntervalTrigger(minutes=5),
        id="refresh-03",
        replace_existing=True
    )
    
    scheduler.start()
    
    yield
    
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router)
app.include_router(books_router)
app.include_router(ratings_router)
app.include_router(users_router)
app.include_router(watchlist_router)
app.include_router(history_router)
app.include_router(library_router)
app.include_router(analytics_router)
app.include_router(waitlist_router)
app.include_router(recommend_router)