FROM --platform=linux/amd64 <official-minimal-base-image> AS builder

WORKDIR /app
COPY . .

RUN <build-command>

FROM --platform=linux/amd64 <official-minimal-base-image>
WORKDIR /app
COPY --from=builder /app/ .

CMD ["<runtime-command>"]