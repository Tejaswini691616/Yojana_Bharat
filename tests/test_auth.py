# PATH: GovScheme/tests/test_auth.py
import uuid


def test_dashboard_requires_login(client):
    resp = client.get("/dashboard", follow_redirects=True)
    assert b"Log In" in resp.data or b"login" in resp.request.path.encode()


def test_register_and_login_flow(client):
    email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post("/register", data={
        "full_name": "Test User", "email": email, "password": "Passw0rd!",
        "age": "30", "annual_income": "150000", "caste": "General",
        "farmer": "No", "student": "No", "disabled": "No",
        "senior_citizen": "No", "bpl": "No", "widow": "No",
    }, follow_redirects=True)
    assert resp.status_code == 200

    client.get("/logout")

    resp = client.post("/login", data={"email": email, "password": "Passw0rd!"},
                        follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"Welcome" in resp.data


def test_login_wrong_password(client):
    resp = client.post("/login", data={"email": "nobody@example.com", "password": "wrong"},
                        follow_redirects=True)
    assert b"Invalid" in resp.data
