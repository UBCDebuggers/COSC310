from fastapi import FastAPI
from app.routers.books import router as books_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(books_router)
