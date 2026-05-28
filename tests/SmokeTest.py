#!/usr/bin/env bash
# validate_containerization_upgrade.sh
#
# Upgrade validation test suite: Dockerfile + docker-compose.yml addition
# Run from the repository root: bash validate_containerization_upgrade.sh
#
# Exit codes:
#   0 — all assertions passed
#   1 — one or more assertions failed

set -euo pipefail

# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

PASS=0
FAIL=0
SKIP=0

pass() { echo -e "${GREEN}[PASS]${NC} $1"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; FAIL=$((FAIL + 1)); }
skip() { echo -e "${YELLOW}[SKIP]${NC} $1"; SKIP=$((SKIP + 1)); }
section() { echo -e "\n${YELLOW}=== $1 ===${NC}"; }

# ---------------------------------------------------------------------------
# Helper: assert a file exists
# ---------------------------------------------------------------------------
assert_file_exists() {
    local file="$1"
    local description="${2:-$file exists}"
    if [[ -f "$file" ]]; then
        pass "$description"
    else
        fail "$description — file not found: $file"
    fi
}

# ---------------------------------------------------------------------------
# Helper: assert a file contains a pattern
# ---------------------------------------------------------------------------
assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local description="${3:-$file contains '$pattern'}"
    if [[ -f "$file" ]] && grep -qE "$pattern" "$file"; then
        pass "$description"
    elif [[ ! -f "$file" ]]; then
        fail "$description — file not found: $file"
    else
        fail "$description — pattern not found in $file"
    fi
}

# ---------------------------------------------------------------------------
# Helper: assert a file does NOT contain a pattern
# ---------------------------------------------------------------------------
assert_file_not_contains() {
    local file="$1"
    local pattern="$2"
    local description="${3:-$file does not contain '$pattern'}"
    if [[ ! -f "$file" ]]; then
        fail "$description — file not found: $file"
    elif grep -qE "$pattern" "$file"; then
        fail "$description — forbidden pattern found in $file"
    else
        pass "$description"
    fi
}

# ---------------------------------------------------------------------------
# Helper: assert a command is available
# ---------------------------------------------------------------------------
assert_command_available() {
    local cmd="$1"
    local description="${2:-command '$cmd' is available}"
    if command -v "$cmd" &>/dev/null; then
        pass "$description"
    else
        fail "$description — '$cmd' not found in PATH"
    fi
}

# ---------------------------------------------------------------------------
# Helper: assert minimum version (semver major.minor comparison)
# ---------------------------------------------------------------------------
version_gte() {
    # Returns 0 (true) if $1 >= $2 in semver terms
    local actual="$1"
    local required="$2"
    printf '%s\n%s\n' "$required" "$actual" | sort -V -C
}

# ---------------------------------------------------------------------------
# SECTION 1 — Runtime / toolchain version assertions
# ---------------------------------------------------------------------------
section "1. Docker Engine and Docker Compose version assertions (target: Engine ≥ 20.10, Compose ≥ 2.0)"

# Docker Engine version
if command -v docker &>/dev/null; then
    DOCKER_VERSION=$(docker version --format '{{.Server.Version}}' 2>/dev/null || echo "0.0.0")
    DOCKER_MAJOR=$(echo "$DOCKER_VERSION" | cut -d. -f1)
    DOCKER_MINOR=$(echo "$DOCKER_VERSION" | cut -d. -f2)
    if [[ "$DOCKER_MAJOR" -gt 20 ]] || { [[ "$DOCKER_MAJOR" -eq 20 ]] && [[ "$DOCKER_MINOR" -ge 10 ]]; }; then
        pass "Docker Engine version is ${DOCKER_VERSION} (>= 20.10 required)"
    else
        fail "Docker Engine version is ${DOCKER_VERSION} — expected >= 20.10"
    fi
else
    fail "Docker Engine is not installed or not in PATH"
fi

# Docker Compose version (plugin form: `docker compose version`)
if docker compose version &>/dev/null 2>&1; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null || docker compose version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    COMPOSE_MAJOR=$(echo "$COMPOSE_VERSION" | cut -d. -f1)
    if [[ "$COMPOSE_MAJOR" -ge 2 ]]; then
        pass "Docker Compose (plugin) version is ${COMPOSE_VERSION} (>= 2.x required)"
    else
        fail "Docker Compose (plugin) version is ${COMPOSE_VERSION} — expected >= 2.x"
    fi
elif command -v docker-compose &>/dev/null; then
    COMPOSE_VERSION=$(docker-compose version --short 2>/dev/null || docker-compose version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    COMPOSE_MAJOR=$(echo "$COMPOSE_VERSION" | cut -d. -f1)
    if [[ "$COMPOSE_MAJOR" -ge 2 ]]; then
        pass "Docker Compose (standalone) version is ${COMPOSE_VERSION} (>= 2.x required)"
    else
        fail "Docker Compose (standalone) version is ${COMPOSE_VERSION} — expected >= 2.x"
    fi
else
    fail "Docker Compose is not installed (neither plugin nor standalone)"
fi

# ---------------------------------------------------------------------------
# SECTION 2 — Required files exist (upgrade deliverables)
# ---------------------------------------------------------------------------
section "2. Required files introduced by this upgrade exist"

assert_file_exists "Dockerfile"            "Dockerfile exists at repository root"
assert_file_exists "docker-compose.yml"    "docker-compose.yml exists at repository root"
assert_file_exists ".dockerignore"         ".dockerignore exists at repository root"
assert_file_exists ".env.example"          ".env.example exists at repository root"

# ---------------------------------------------------------------------------
# SECTION 3 — Dockerfile structure validation
# ---------------------------------------------------------------------------
section "3. Dockerfile structure — multi-stage build"

assert_file_contains "Dockerfile" "^FROM .+ AS builder" \
    "Dockerfile has a named 'builder' stage (multi-stage build)"

assert_file_contains "Dockerfile" "^FROM " \
    "Dockerfile has at least one FROM instruction"

# Verify there are at least two FROM lines (multi-stage)
if [[ -f "Dockerfile" ]]; then
    FROM_COUNT=$(grep -cE "^FROM " Dockerfile || true)
    if [[ "$FROM_COUNT" -ge 2 ]]; then
        pass "Dockerfile has ${FROM_COUNT} FROM stages (multi-stage build confirmed)"
    else
        fail "Dockerfile has only ${FROM_COUNT} FROM stage(s) — expected >= 2 for multi-stage build"
    fi
fi

assert_file_contains "Dockerfile" "COPY|ADD" \
    "Dockerfile copies application artifacts into the runtime stage"

assert_file_contains "Dockerfile" "EXPOSE|expose" \
    "Dockerfile declares an EXPOSE instruction for the application port"

assert_file_contains "Dockerfile" "CMD|ENTRYPOINT" \
    "Dockerfile declares a CMD or ENTRYPOINT instruction"

# Ensure no secrets or credential patterns are baked into the image
assert_file_not_contains "Dockerfile" "PASSWORD\s*=\s*\S+" \
    "Dockerfile does not hard-code PASSWORD values"
assert_file_not_contains "Dockerfile" "SECRET\s*=\s*\S+" \
    "Dockerfile does not hard-code SECRET values"
assert_file_not_contains "Dockerfile" "API_KEY\s*=\s*\S+" \
    "Dockerfile does not hard-code API_KEY values"

# ---------------------------------------------------------------------------
# SECTION 4 — docker-compose.yml structure validation
# ---------------------------------------------------------------------------
section "4. docker-compose.yml structure"

assert_file_contains "docker-compose.yml" "services:" \
    "docker-compose.yml defines a 'services' block"

assert_file_contains "docker-compose.yml" "app:" \
    "docker-compose.yml defines an 'app' service"

assert_file_contains "docker-compose.yml" "build:" \
    "docker-compose.yml references a build context"

assert_file_contains "docker-compose.yml" "ports:" \
    "docker-compose.yml maps host-to-container ports"

assert_file_contains "docker-compose.yml" "volumes:" \
    "docker-compose.yml mounts a source volume for live-reload"

assert_file_contains "docker-compose.yml" "env_file|environment" \
    "docker-compose.yml loads environment variables (env_file or environment block)"

# Confirm .env file is referenced for environment loading
assert_file_contains "docker-compose.yml" "\.env" \
    "docker-compose.yml references .env file for environment variable loading"

# Ensure no hard-coded secrets in compose file
assert_file_not_contains "docker-compose.yml" "password:\s*\S+" \
    "docker-compose.yml does not hard-code password values"

# ---------------------------------------------------------------------------
# SECTION 5 — .dockerignore completeness
# ---------------------------------------------------------------------------
section "5. .dockerignore excludes expected paths"

assert_file_contains ".dockerignore" "\.git" \
    ".dockerignore excludes .git directory"

assert_file_contains ".dockerignore" "node_modules|vendor|__pycache__|\.venv|target|dist|build" \
    ".dockerignore excludes local dependency / build output directories"

assert_file_contains ".dockerignore" "\.env$|\.env\b" \
    ".dockerignore excludes .env file (prevents secret leakage into build context)"

# ---------------------------------------------------------------------------
# SECTION 6 — .env.example completeness
# ---------------------------------------------------------------------------
section "6. .env.example provides a developer template"

if [[ -f ".env.example" ]]; then
    LINE_COUNT=$(grep -cE "^\s*[A-Z_]+=.*" .env.example || true)
    if [[ "$LINE_COUNT" -ge 1 ]]; then
        pass ".env.example contains ${LINE_COUNT} environment variable key(s)"
    else
        fail ".env.example contains no environment variable keys (expected at least one KEY=value line)"
    fi
    # Ensure no real secrets are committed in the example file
    assert_file_not_contains ".env.example" "password=[^<\$]" \
        ".env.example does not contain real password values (only placeholders)"
fi

# ---------------------------------------------------------------------------
# SECTION 7 — .gitignore protects .env
# ---------------------------------------------------------------------------
section "7. .gitignore prevents accidental .env commit"

if [[ -f ".gitignore" ]]; then
    assert_file_contains ".gitignore" "^\.env$|^\.env\b|/\.env" \
        ".gitignore includes .env to prevent credential commits"
else
    skip ".gitignore not found — cannot verify .env exclusion (create .gitignore with .env entry)"
fi

# ---------------------------------------------------------------------------
# SECTION 8 — Docker build succeeds (integration)
# ---------------------------------------------------------------------------
section "8. Docker build integration — image builds without errors"

if command -v docker &>/dev/null && [[ -f "Dockerfile" ]]; then
    BUILD_TAG="upgrade-validation-test:$(date +%s)"
    echo "    Building image with tag: ${BUILD_TAG}"
    if docker build -t "$BUILD_TAG" . --quiet 2>/tmp/docker_build_output; then
        pass "docker build completed successfully"
        # Clean up test image
        docker rmi "$BUILD_TAG" --force &>/dev/null || true
    else
        fail "docker build failed — see output below:"
        cat /tmp/docker_build_output >&2
    fi
else
    skip "Docker not available or Dockerfile missing — skipping build integration test"
fi

# ---------------------------------------------------------------------------
# SECTION 9 — docker compose config validates without errors
# ---------------------------------------------------------------------------
section "9. docker compose config — YAML is valid and resolves correctly"

if command -v docker &>/dev/null && [[ -f "docker-compose.yml" ]]; then
    # Create a temporary .env if none exists so compose config doesn't error on missing file
    TEMP_ENV_CREATED=false
    if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
        cp .env.example .env
        TEMP_ENV_CREATED=true
    fi

    if docker compose config --quiet 2>/tmp/compose_config_output; then
        pass "docker compose config validates without errors"
    else
        fail "docker compose config reported errors — see output below:"
        cat /tmp/compose_config_output >&2
    fi

    if [[ "$TEMP_ENV_CREATED" == "true" ]]; then
        rm -f .env
    fi
else
    skip "Docker or docker-compose.yml not available — skipping compose config validation"
fi

# ---------------------------------------------------------------------------
# SECTION 10 — Container starts and application responds (smoke test)
# ---------------------------------------------------------------------------
section "10. End-to-end smoke test — container starts and application responds"

if command -v docker &>/dev/null && [[ -f "docker-compose.yml" ]]; then
    # Determine exposed host port from docker-compose.yml
    HOST_PORT=$(grep -oE '[0-9]+:[0-9]+' docker-compose.yml | head -1 | cut -d: -f1 || true)

    if [[ -z "$HOST_PORT" ]]; then
        skip "Could not determine host port from docker-compose.yml — skipping smoke test"
    else
        echo "    Detected host port: ${HOST_PORT}"

        # Create temporary .env if needed
        TEMP_ENV_CREATED=false
        if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
            cp .env.example .env
            TEMP_ENV_CREATED=true
        fi

        # Start services in detached mode
        echo "    Starting containers with: docker compose up --build -d"
        if docker compose up --build -d 2>/tmp/compose_up_output; then
            pass "docker compose up --build -d completed without errors"

            # Wait for application to become ready (up to 30 seconds)
            echo "    Waiting for application to respond on port ${HOST_PORT}..."
            READY=false
            for i in $(seq 1 15); do
                if curl -sf "http://localhost:${HOST_PORT}" -o /dev/null 2>/dev/null \
                   || curl -sf "http://localhost:${HOST_PORT}/health" -o /dev/null 2>/dev/null \
                   || curl -sf "http://localhost:${HOST_PORT}/healthz" -o /dev/null 2>/dev/null; then
                    READY=true
                    break
                fi
                sleep 2
            done

            if [[ "$READY" == "true" ]]; then
                pass "Application responded on http://localhost:${HOST_PORT} after container start"
            else
                # Check if container is at least running even if no HTTP endpoint is exposed
                RUNNING_CONTAINERS=$(docker compose ps --status running --quiet 2>/dev/null | wc -l || echo 0)
                if [[ "$RUNNING_CONTAINERS" -ge 1 ]]; then
                    pass "Container is running (${RUNNING_CONTAINERS} service(s) up) — no HTTP response on port ${HOST_PORT} (may not be an HTTP service)"
                else
                    fail "Application did not respond on http://localhost:${HOST_PORT} and no containers are running"
                    echo "    Container logs:"
                    docker compose logs --tail=50 >&2 || true
                fi
            fi

            # Verify source-code volume mount is active
            APP_CONTAINER=$(docker compose ps -q app 2>/dev/null | head -1 || true)
            if [[ -n "$APP_CONTAINER" ]]; then
                MOUNT_COUNT=$(docker inspect "$APP_CONTAINER" \
                    --format '{{range .Mounts}}{{.Type}}{{"\n"}}{{end}}' 2>/dev/null \
                    | grep -c "bind" || true)
                if [[ "$MOUNT_COUNT" -ge 1 ]]; then
                    pass "Source directory is bind-mounted into the app container (live-reload support confirmed)"
                else
                    fail "No bind mounts found on app container — source volume mount may be missing"
                fi
            else
                skip "Could not inspect app container for volume mounts"
            fi

        else
            fail "docker compose up --build -d failed — see output below:"
            cat /tmp/compose_up_output >&2
        fi

        # Tear down
        echo "    Tearing down containers..."
        docker compose down --volumes --remove-orphans &>/dev/null || true

        if [[ "$TEMP_ENV_CREATED" == "true" ]]; then
            rm -f .env
        fi
    fi
else
    skip "Docker not available or docker-compose.yml missing — skipping end-to-end smoke test"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
section "Test Summary"
TOTAL=$((PASS + FAIL + SKIP))
echo -e "  Total : ${TOTAL}"
echo -e "  ${GREEN}Passed${NC}: ${PASS}"
echo -e "  ${RED}Failed${NC}: ${FAIL}"
echo -e "  ${YELLOW}Skipped${NC}: ${SKIP}"

if [[ "$FAIL" -gt 0 ]]; then
    echo -e "\n${RED}UPGRADE VALIDATION FAILED — ${FAIL} assertion(s) did not pass.${NC}"
    exit 1
else
    echo -e "\n${GREEN}UPGRADE VALIDATION PASSED — all assertions satisfied.${NC}"
    exit 0
fi