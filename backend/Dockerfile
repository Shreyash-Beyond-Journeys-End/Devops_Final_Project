FROM python:3.12-slim

# print logs straight away
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# copy requirements first so this layer is cached when only code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# create a normal user so the container does not run as root
RUN useradd --uid 10001 --no-create-home appuser
USER 10001

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
