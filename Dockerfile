FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip wheel --wheel-dir=/wheels -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=build /wheels /wheels
COPY --from=build /requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]