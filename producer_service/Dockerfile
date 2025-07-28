FROM python:3.11

WORKDIR /app

COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt

COPY . .

CMD ["uvicorn", "producer:app", "--host", "0.0.0.0", "--port", "8000"]
