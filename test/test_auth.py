from fastapi.testclient import TestClient
from app.main import app



client = TestClient(app)


def test_home():

    response = client.get("/")

    assert response.status_code == 200


def test_register_user(client):

    response = client.post(
        "/register",
        json={
            "username": "aniket",
            "email": "aniket@gmail.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

def test_login_user(client):

    # Register user first
    client.post(
        "/register",
        json={
            "username": "aniket",
            "email": "aniket@gmail.com",
            "password": "123456"
        }
    )

    # Login
    response = client.post(
        "/login",
        json ={
            "email": "aniket@gmail.com",
            "password": "123456"
        }
    )
    print(response.json())
    assert response.status_code == 200

    data = response.json()


    print(f"data is {data}")

    assert "access_token" in data
    assert "refresh_token" in data