import os

# database url comes from env variable
# default one is for running locally with the postgres from docker compose
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://placetrack:placetrack@localhost:5432/placetrack",
)
