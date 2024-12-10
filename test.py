import pytest
import requests

BASE_URL = "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def start_server():
    # Server'ın çalıştığından emin olun
    import subprocess
    server = subprocess.Popen(["python", "app.py"])
    yield
    server.terminate()

def test_get_all_items():
    response = requests.get(f"{BASE_URL}/items")
    assert response.status_code == 200
    assert isinstance(response.json().get("items"), list)

def test_create_item():
    new_item = {"name": "Monitor", "price": 300}
    response = requests.post(f"{BASE_URL}/items", json=new_item)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Item created"
    assert data["item"]["name"] == "Monitor"
    assert data["item"]["price"] == 300

def test_get_specific_item():
    response = requests.get(f"{BASE_URL}/items/1")
    assert response.status_code == 200
    item = response.json().get("item")
    assert item["id"] == 1
    assert item["name"] == "Laptop"

def test_update_item():
    updated_data = {"name": "Gaming Laptop", "price": 2000}
    response = requests.put(f"{BASE_URL}/items/1", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Item updated"
    assert data["item"]["name"] == "Gaming Laptop"
    assert data["item"]["price"] == 2000

def test_delete_item():
    response = requests.delete(f"{BASE_URL}/items/3")
    assert response.status_code == 200
    assert response.json().get("message") == "Item deleted"

    # Silinen item'ı tekrar sorgula
    response = requests.get(f"{BASE_URL}/items/3")
    assert response.status_code == 404
    assert response.json().get("message") == "Item not found"
