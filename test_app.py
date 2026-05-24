from fastapi.testclient import TestClient
from app import app

# This creates a fake browser to test FastAPI app
client = TestClient(app)

def test_index_route():
    """Test if the home page loads successfully"""
    response = client.get("/")
    assert response.status_code == 200 

def test_docs_route():
    """Test if the Swagger UI loads successfully"""
    response = client.get("/docs")
    assert response.status_code == 200