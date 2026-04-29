FROM python:3.12-slim AS build

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

FROM python:3.12-slim

WORKDIR /app

COPY --from=build /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .

ENV FLASK_APP=app.py

CMD ["flask", "run", "--host=0.0.0.0"]