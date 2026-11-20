import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SEED_DEMO"] = "1"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="module")
def client():
    Base.metadata.drop_all(engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(engine)


def login(c, email):
    r = c.post("/auth/login", json={"email": email, "password": "demo1234"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


def test_auth_and_roles(client):
    assert client.get("/me").status_code == 401
    assert client.post("/auth/login", json={"email": "student@demo.uz", "password": "xxx"}).status_code == 401
    # ochiq ro'yxatdan o'tishda universitet roli yo'q
    r = client.post("/auth/register", json={"email": "x@y.uz", "name": "Xx", "password": "12345678", "role": "university"})
    assert r.status_code == 422
    st = login(client, "student@demo.uz")
    assert client.get("/review/queue", headers=st).status_code == 403
    assert client.get("/employer/candidates?profession_id=1", headers=st).status_code == 403


def test_skill_gap_uses_only_verified(client):
    st = login(client, "student@demo.uz")
    g = client.get("/skill-gap", headers=st).json()
    by = {i["skill"]["name"]: i for i in g["items"]}
    assert by["Python dasturlash"]["verified"] == 3 and by["Python dasturlash"]["gap"] == 1
    # o'zini baholash tasdiq emas: da'vo bor, verified=0
    assert by["Jamoada ishlash"]["verified"] == 0 and by["Jamoada ishlash"]["status"] == "unverified"
    assert 0 < g["readiness"] < 100


def test_review_flow_and_passport(client):
    st, uni = login(client, "student@demo.uz"), login(client, "uni@demo.uz")
    pass_before = {s["skill"]["name"] for s in client.get("/passport", headers=st).json()["skills"]}
    assert "SQL va ma'lumotlar bazalari" not in pass_before  # pending hali pasportda yo'q
    q = client.get("/review/queue", headers=uni).json()
    assert len(q) == 1
    assert client.post(f"/review/{q[0]['id']}", json={"approve": True, "verified_level": 3}, headers=uni).status_code == 200
    pass_after = {s["skill"]["name"] for s in client.get("/passport", headers=st).json()["skills"]}
    assert "SQL va ma'lumotlar bazalari" in pass_after
    assert client.post(f"/review/{q[0]['id']}", json={"approve": True}, headers=uni).status_code == 404


def test_evidence_ai_and_roadmap(client):
    st = login(client, "student@demo.uz")
    sk = client.get("/skills", headers=st).json()
    sid = next(s["id"] for s in sk if s["name"] == "Web API (REST) ishlab chiqish")
    r = client.post("/evidence", json={"skill_id": sid, "type": "project", "title": "REST API", "description": "FastAPI da CRUD API", "claimed_level": 3}, headers=st)
    assert r.status_code == 201 and r.json()["status"] == "pending"
    a = client.post(f"/evidence/{r.json()['id']}/analyze", headers=st).json()
    assert 1 <= a["ai_level"] <= 5 and a["ai_feedback"]
    assert a["status"] == "pending"  # AI tasdiqlamaydi
    items = client.post("/roadmap/generate", headers=st).json()
    assert items and all(i["done"] is False for i in items)
    assert client.patch(f"/roadmap/{items[0]['id']}", json={"done": True}, headers=st).json()["done"] is True


def test_employer_consent_and_analytics(client):
    hr, uni, st = login(client, "hr@demo.uz"), login(client, "uni@demo.uz"), login(client, "student@demo.uz")
    c = client.get("/employer/candidates?profession_id=1", headers=hr).json()["candidates"]
    assert len(c) == 1 and "email" not in c[0]
    client.patch("/me", json={"consent_employers": False}, headers=st)
    assert client.get("/employer/candidates?profession_id=1", headers=hr).json()["candidates"] == []
    a = client.get("/university/analytics", headers=uni).json()
    assert a["students_total"] == 1 and "email" not in str(a)
