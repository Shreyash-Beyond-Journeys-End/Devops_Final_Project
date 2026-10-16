from app.db import get_db
from app.main import app

sample_job = {
    "company": "Acme",
    "role": "SDE Intern",
    "status": "applied",
    "applied_on": "2026-09-01",
    "notes": "referral",
}


# helper to add a job, can change some fields
def add_job(client, **changes):
    data = sample_job.copy()
    data.update(changes)
    return client.post("/api/jobs", json=data)


# ---------- health checks ----------

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_ready(client):
    assert client.get("/ready").status_code == 200


def test_ready_gives_503_when_db_is_down(client):
    class BrokenDB:
        def execute(self, *args):
            raise RuntimeError("db down")

    app.dependency_overrides[get_db] = lambda: BrokenDB()
    assert client.get("/ready").status_code == 503


# ---------- create ----------

def test_create_job(client):
    res = add_job(client)
    assert res.status_code == 201
    assert res.json()["id"] == 1
    assert res.json()["company"] == "Acme"


def test_create_with_wrong_status(client):
    res = add_job(client, status="ghosted")
    assert res.status_code == 422


def test_create_with_blank_company(client):
    res = add_job(client, company="   ")
    assert res.status_code == 422


# ---------- read ----------

def test_list_jobs_and_filter(client):
    add_job(client)
    add_job(client, company="Beta", status="offer")

    all_jobs = client.get("/api/jobs").json()
    assert len(all_jobs) == 2

    offers = client.get("/api/jobs?status=offer").json()
    assert len(offers) == 1
    assert offers[0]["company"] == "Beta"


def test_get_one_job(client):
    add_job(client)
    res = client.get("/api/jobs/1")
    assert res.json()["role"] == "SDE Intern"


def test_get_job_not_found(client):
    assert client.get("/api/jobs/99").status_code == 404


# ---------- update ----------

def test_update_job(client):
    add_job(client)
    new_data = sample_job.copy()
    new_data["status"] = "interview"
    res = client.put("/api/jobs/1", json=new_data)
    assert res.status_code == 200
    assert res.json()["status"] == "interview"


def test_update_job_not_found(client):
    assert client.put("/api/jobs/99", json=sample_job).status_code == 404


# ---------- delete ----------

def test_delete_job(client):
    add_job(client)
    assert client.delete("/api/jobs/1").status_code == 204
    assert client.get("/api/jobs/1").status_code == 404


def test_delete_job_not_found(client):
    assert client.delete("/api/jobs/99").status_code == 404


# ---------- stats and metrics ----------

def test_stats_when_empty(client):
    res = client.get("/api/jobs/stats")
    assert res.json() == {"total": 0, "applied": 0, "interview": 0, "offer": 0, "rejected": 0}


def test_stats_counts(client):
    add_job(client)
    add_job(client, status="offer")
    stats = client.get("/api/jobs/stats").json()
    assert stats["total"] == 2
    assert stats["applied"] == 1
    assert stats["offer"] == 1


def test_metrics_endpoint(client):
    client.get("/health")
    res = client.get("/metrics")
    assert "http_requests_total" in res.text
