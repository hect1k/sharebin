FROM python:3.13-rc-slim AS builder

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.13-rc-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY app/ ./app

COPY static/ ./static

COPY data/ ./data

COPY logs/ ./logs

ENV PORT 8000

EXPOSE ${PORT}

CMD ["sh", "-c", "fastapi run --host 0.0.0.0 --port $PORT"]
