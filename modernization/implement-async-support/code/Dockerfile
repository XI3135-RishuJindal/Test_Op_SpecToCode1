FROM <minimal-base-image> AS builder

COPY . /app
WORKDIR /app

RUN <build-tool> install

FROM <minimal-base-image>

COPY --from=builder /app /app
WORKDIR /app

CMD ["<runtime-command>"]