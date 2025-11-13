from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_get_diseases(monkeypatch):
    fake_response = [{"id": "D1", "label": "Disease 1"}]

    def mock_get_diseases_from_wikidata():
        return fake_response

    # Меняем функцию именно в backend.main, откуда её FastAPI вызывает
    monkeypatch.setattr("backend.main.get_diseases_from_wikidata", mock_get_diseases_from_wikidata)

    response = client.get("/api/diseases")
    assert response.status_code == 200
    assert response.json() == fake_response



def test_chat(monkeypatch):
    fake_reply = {
        "message": "This is a test reply.",
        "medications": ["med1", "med2"],
    }

    def mock_get_illness_and_drugs(message, top_k):
        return fake_reply

    monkeypatch.setattr("backend.main.get_illness_and_drugs", mock_get_illness_and_drugs)

    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    assert response.json() == {"reply": fake_reply}

def test_get_hospitals(monkeypatch):
    fake_hospitals = [
        {
            "id": "H1",
            "name": "Hospital 1",
            "address": "123 Main St",
            "phone": "+123456789",
            "mfo": "300001"
        }
    ]

    def mock_get_hospitals_from_wikidata(country):
        return fake_hospitals

    # Мокаем именно в backend.main, откуда FastAPI вызывает
    monkeypatch.setattr("backend.main.get_hospitals_from_wikidata", mock_get_hospitals_from_wikidata)

    response = client.get("/api/hospitals")
    assert response.status_code == 200
    assert response.json() == fake_hospitals


def test_get_drug_disease_data(monkeypatch):
    fake_graph = {
        "nodes": [{"id": "node1", "label": "Node 1"}],
        "edges": [{"source": "node1", "target": "node2"}]
    }

    def mock_get_drug_illness_graph():
        return fake_graph

    # Мокаем в backend.main
    monkeypatch.setattr("backend.main.get_drug_illness_graph", mock_get_drug_illness_graph)

    response = client.get("/api/drug-disease")
    assert response.status_code == 200
    assert response.json() == fake_graph
