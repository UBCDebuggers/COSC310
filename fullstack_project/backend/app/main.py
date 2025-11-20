from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.ratings import router as ratings_router
from app.routers.users import router as users_router
from app.routers.watchlist import router as watchlist_router
from app.routers.history import router as history_router
from app.routers.ratedBooks import router as ratedBooks_router
from app.routers.library import router as library_router

app = FastAPI()

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
app.include_router(ratedBooks_router)
app.include_router(library_router)
