FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir bandit pip-audit

COPY . .

RUN bandit -r . -ll --exit-zero \
    && pip-audit --desc on

CMD ["python", "-m", "pytest"]