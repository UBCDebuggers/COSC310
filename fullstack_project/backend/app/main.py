'''
from fastapi import FastAPI
from routers.items import router as items_router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(items_router)
'''

#use for mac
#uvicorn fullstack_project.backend.app.main:app --reload 

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"ok": True, "msg": "Hello from FastAPI!"}

