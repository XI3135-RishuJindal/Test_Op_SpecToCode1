FROM --platform=${TARGETPLATFORM} runtime:latest AS base

# Begin build stage
FROM --platform=${TARGETPLATFORM} build-essentials:latest AS builder
WORKDIR /app
COPY . .

# Assuming a placeholder for build command specific to the application
RUN build_command_here

# Set the entry point for the runtime container
FROM base AS final
COPY --from=builder /app/output /app
ENTRYPOINT ["executable_name_here"]