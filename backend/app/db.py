from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

# pool_pre_ping checks the connection before using it (helps when postgres restarts)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()


# gives a db session to each request and closes it after
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
