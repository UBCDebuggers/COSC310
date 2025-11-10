from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    r = client.get("/")
    assert r.status_code == 404
    assert r.json() ==  {"detail":"Not Found"}
    