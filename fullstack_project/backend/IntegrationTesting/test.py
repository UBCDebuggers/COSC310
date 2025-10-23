from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    r = client.get("/")
    assert r.status_code == 404
    assert r.json() ==  {"detail":"Not Found"}
    
def test_get_item():
    r = client.get("/books/0195153448")
    assert r.json() == {"isbn":"0195153448","title":"Classical Mythology","author":"Mark P. O. Morford","year_of_publication":2002,"publisher":"Oxford University Press","img_url_s":"http://images.amazon.com/images/P/0195153448.01.THUMBZZZ.jpg","img_url_m":"http://images.amazon.com/images/P/0195153448.01.MZZZZZZZ.jpg","img_url_l":"http://images.amazon.com/images/P/0195153448.01.LZZZZZZZ.jpg"}