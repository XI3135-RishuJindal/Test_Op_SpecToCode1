FROM python:3.12-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir --requirement requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir Flask>=3.0,<4.0

CMD ["flask", "run", "--host=0.0.0.0"]