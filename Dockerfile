FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN pip install --user --upgrade pip \
    && pip install --user --no-cache-dir -r requirements.txt

COPY . .

FROM python:3.12-slim

WORKDIR /app

ENV PATH="/root/.local/bin:$PATH"

COPY --from=builder /root/.local /root/.local
COPY . .

CMD ["python", "app.py"]