from fastapi import FastAPI
from app.routers.users import router as users_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(users_router)
