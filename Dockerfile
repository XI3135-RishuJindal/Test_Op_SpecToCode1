FROM python:3.12-slim AS base

WORKDIR /app

FROM base AS builder
RUN pip install --upgrade pip
RUN pip install --prefix=/install SQLAlchemy
RUN find /install -type f -name '__pycache__' -delete

FROM base
COPY --from=builder /install /usr/local
COPY . /app

CMD ["python"]