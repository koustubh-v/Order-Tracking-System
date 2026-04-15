FROM python:3.11-slim
# Install libpq-dev and gcc for psycopg2
RUN apt-get update && apt-get install -y libpq-dev gcc
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY db.py .
COPY processor.py .
CMD ["python", "processor.py"]
