# TASKS: Introduce Spring Security with JWT-based Authentication on REST Endpoints

> **Scope:** Add Spring Security and JWT-based authentication to secure existing REST endpoints.
> **Option:** Moderate — token-based auth with stateless sessions, JWT issued on login, validated on protected routes.
> **Note:** Build tool, runtime version, and framework details were not provided in the tech analysis. Task file targets below use Spring Boot/Maven conventions as the most common baseline; adjust to your actual build file (`build.gradle`, `pom.xml`) and package structure as needed.

---

## Prerequisites

- [ ] [XS] Confirm Java SDK version (17+ recommended for Spring Security 6.x) is installed and set in `JAVA_HOME`
- [ ] [XS] Confirm Spring Boot version in `pom.xml` or `build.gradle` — Spring Security 6.x requires Spring Boot 3.x; Security 5.x targets Boot 2.7.x
- [ ] [XS] Verify access to the application's dependency registry (Maven Central or internal Nexus/Artifactory) to resolve `spring-security-*` and `jjwt` artifacts
- [ ] [XS] Ensure a working local build (`./mvnw clean verify` or `./gradlew build`) passes before any changes are made
- [ ] [XS] Confirm a dedicated feature branch policy is in place and create branch `feature/spring-security-jwt`

---

## Phase 1 — Preparation

- [ ] [S] Audit all existing REST controllers (e.g., `src/main/java/**/controller/`) and document which endpoints must be public vs. protected, recording findings in `docs/endpoint-auth-matrix.md`
- [ ] [S] Capture current integration-test baseline by running the full test suite and saving output to `docs/test-baseline-pre-security.txt` for regression comparison
- [ ] [XS] Add `spring-boot-starter-security` dependency to `pom.xml` (or `build.gradle`) and verify the build resolves without errors — note that this will lock down all endpoints by default
- [ ] [XS] Add `io.jsonwebtoken:jjwt-api`, `jjwt-impl`, and `jjwt-jackson` (version 0.12.x) dependencies to `pom.xml` (or `build.gradle`)
- [ ] [XS] Add a CI gate (e.g., GitHub Actions step or Jenkinsfile stage) that fails the build if `spring-security-*` or `jjwt` versions are unpinned or if `permitAll()` is applied globally without explicit review comment

---

## Phase 2 — Core Upgrade

- [ ] [M] Create `JwtProperties` configuration class in `src/main/java/**/security/config/JwtProperties.java` to hold `secret`, `expiration-ms`, and `issuer` values, bound from `application.yml` under `app.jwt.*`
- [ ] [XS] Add `app.jwt.secret`, `app.jwt.expiration-ms`, and `app.jwt.issuer` keys to `src/main/resources/application.yml`; add placeholder entries to `src/main/resources/application-example.yml` with instructions — do NOT commit real secrets
- [ ] [M] Implement `JwtTokenProvider` service in `src/main/java/**/security/jwt/JwtTokenProvider.java` with methods `generateToken(Authentication)`, `validateToken(String)`, and `getAuthentication(String)` using the `jjwt` library
- [ ] [M] Implement `JwtAuthenticationFilter` (extending `OncePerRequestFilter`) in `src/main/java/**/security/jwt/JwtAuthenticationFilter.java` to extract the `Authorization: Bearer <token>` header, validate it via `JwtTokenProvider`, and set the `SecurityContextHolder`
- [ ] [M] Create `UserDetailsServiceImpl` in `src/main/java/**/security/service/UserDetailsServiceImpl.java` implementing `UserDetailsService`, loading user credentials from the existing user store (database, in-memory, or external service — adapt to actual data layer)
- [ ] [M] Create `SecurityConfig` class in `src/main/java/**/security/config/SecurityConfig.java` annotated with `@Configuration` and `@EnableWebSecurity`, defining the `SecurityFilterChain` bean: stateless session (`SessionCreationPolicy.STATELESS`), CSRF disabled for REST, `JwtAuthenticationFilter` registered before `UsernamePasswordAuthenticationFilter`, and endpoint rules from `docs/endpoint-auth-matrix.md`
- [ ] [S] Implement `AuthController` in `src/main/java/**/controller/AuthController.java` with a `POST /api/auth/login` endpoint that authenticates credentials via `AuthenticationManager` and returns a signed JWT in the response body
- [ ] [S] Implement `AuthController` `POST /api/auth/refresh` endpoint (if refresh tokens are in scope) or mark as out-of-scope in `docs/endpoint-auth-matrix.md`
- [ ] [XS] Annotate protected REST controllers or individual handler methods with `@PreAuthorize` or rely on `SecurityConfig` URL rules — ensure consistency with `docs/endpoint-auth-matrix.md`
- [ ] [S] Handle `AuthenticationException` and `AccessDeniedException` in a `SecurityExceptionHandler` (or extend existing `@ControllerAdvice`) in `src/main/java/**/exception/SecurityExceptionHandler.java` to return structured JSON error responses (401/403) instead of default Spring Security HTML pages

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for `JwtTokenProvider` in `src/test/java/**/security/jwt/JwtTokenProviderTest.java` covering token generation, successful validation, expired token rejection, and tampered token rejection
- [ ] [M] Write unit tests for `JwtAuthenticationFilter` in `src/test/java/**/security/jwt/JwtAuthenticationFilterTest.java` covering missing header, malformed token, and valid token scenarios using `MockHttpServletRequest`
- [ ] [M] Write integration tests for `AuthController` in `src/test/java/**/controller/AuthControllerTest.java` using `@SpringBootTest` + `MockMvc`: valid login returns 200 + token, invalid credentials return 401
- [ ] [M] Write integration tests for at least two protected endpoints in `src/test/java/**/controller/` verifying: no token → 401, valid token → 200, expired token → 401, insufficient role → 403
- [ ] [S] Run full test suite and compare results against `docs/test-baseline-pre-security.txt`; document any new failures in `docs/test-delta-post-security.md` and resolve before merge
- [ ] [XS] Verify test coverage for `security/` package meets project threshold (add Jacoco or equivalent config to `pom.xml`/`build.gradle` if not already present)

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI pipeline configuration (`.github/workflows/ci.yml`, `Jenkinsfile`, or equivalent) to inject `APP_JWT_SECRET` from a secrets store (GitHub Secrets, Vault, etc.) as an environment variable during test and build stages — never hardcode
- [ ] [XS] If a `Dockerfile` exists, verify no JWT secret is baked into the image; confirm the secret is passed at runtime via environment variable in `docker-compose.yml` or Kubernetes `Secret` manifest
- [ ] [XS] Add `APP_JWT_SECRET` and `APP_JWT_EXPIRATION_MS` to the environment variable documentation in `docs/runbook.md` (or equivalent ops doc) with required format and rotation guidance

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CHANGELOG.md` with a new entry describing the addition of Spring Security JWT authentication, listing affected endpoints, and noting any breaking changes (all previously open endpoints now require a token unless explicitly permitted)
- [ ] [S] Update `docs/runbook.md` with: how to generate/rotate the JWT secret, token expiry configuration, how to call `POST /api/auth/login`, and how to pass the token in subsequent requests
- [ ] [XS] Update `README.md` with a "Authentication" section linking to the runbook and showing a minimal `curl` example for login and authenticated request
- [ ] [M] Perform a staged rollout: deploy to a staging environment, run smoke tests against `POST /api/auth/login` and at least one protected and one public endpoint, and record results in `docs/staging-smoke-test-results.md`
- [ ] [XS] Set up post-deployment monitoring alert for elevated 401/403 response rates on the REST API (add to existing alerting config, e.g., Prometheus alert rule or CloudWatch alarm) to catch misconfigured clients after rollout