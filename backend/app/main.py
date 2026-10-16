from fastapi import Depends, FastAPI, HTTPException, Response
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import schemas
from .db import get_db
from .models import Job

app = FastAPI(title="PlaceTrack API")

# this adds the /metrics endpoint that prometheus scrapes
Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.get("/health")
def health():
    return {"status": "ok"}


# readiness check for kubernetes, only ready when the database works
@app.get("/ready")
def ready(response: Response, db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = 503
        return {"status": "database unavailable"}
    return {"status": "ready"}


def find_job(db, job_id):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/jobs", response_model=list[schemas.JobOut])
def list_jobs(status: schemas.Status | None = None, db: Session = Depends(get_db)):
    query = db.query(Job)
    if status:
        query = query.filter(Job.status == status)
    # newest first
    return query.order_by(Job.id.desc()).all()


# note: this has to be above /api/jobs/{job_id}, otherwise "stats" is taken as the id
@app.get("/api/jobs/stats", response_model=schemas.Stats)
def job_stats(db: Session = Depends(get_db)):
    result = {"total": 0}
    for status in schemas.STATUSES:
        count = db.query(Job).filter(Job.status == status).count()
        result[status] = count
        result["total"] += count
    return result


@app.get("/api/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return find_job(db, job_id)


@app.post("/api/jobs", response_model=schemas.JobOut, status_code=201)
def create_job(data: schemas.JobIn, db: Session = Depends(get_db)):
    job = Job(**data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@app.put("/api/jobs/{job_id}", response_model=schemas.JobOut)
def update_job(job_id: int, data: schemas.JobIn, db: Session = Depends(get_db)):
    job = find_job(db, job_id)
    job.company = data.company
    job.role = data.role
    job.status = data.status
    job.applied_on = data.applied_on
    job.notes = data.notes
    db.commit()
    db.refresh(job)
    return job


@app.delete("/api/jobs/{job_id}", status_code=204)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = find_job(db, job_id)
    db.delete(job)
    db.commit()
