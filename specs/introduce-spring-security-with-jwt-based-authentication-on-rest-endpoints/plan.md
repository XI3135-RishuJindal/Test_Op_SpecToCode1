# PLAN: Introduce Spring Security with JWT-based Authentication on REST Endpoints

---

## Overview

**Migration Strategy: Feature-Flag Gated**

Spring Security with JWT authentication will be introduced behind a feature flag, allowing the security layer to be enabled and disabled without redeploying the application. This approach is chosen because:

- The upgrade urgency is **medium**, meaning there is no immediate pressure to perform a hard cutover.
- The existing codebase and runtime details are **partially unknown**, making a big-bang approach risky.
- A feature-flag gate allows incremental endpoint-by-endpoint rollout, reducing blast radius if integration issues arise.
- Security changes are high-sensitivity; parallel validation against unprotected endpoints during transition reduces regression risk.

> **NOTE:** Because the tech analysis does not provide specific framework versions, runtime, or build tool details, several sections below are marked **TODO** and must be resolved during discovery before implementation begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Discovery & Baseline | Audit existing REST endpoints, identify authentication gaps, confirm build tool and runtime versions, establish test baseline | Access to codebase and CI environment | TODO (derive from confirmed person-days once option details are provided) |
| 2 — Dependency Integration | Add Spring Security and JWT library dependencies; configure build tool; verify application still starts | Phase 1 complete | TODO |
| 3 — Security Configuration | Implement `SecurityFilterChain`, JWT filter, token provider, and `UserDetailsService`; wire feature flag | Phase 2 complete | TODO |
| 4 — Endpoint Protection | Annotate or configure endpoint authorization rules; implement login/token-issuance endpoint | Phase 3 complete | TODO |
| 5 — Testing & Hardening | Unit, integration, and security regression tests; penetration/fuzzing of auth endpoints | Phase 4 complete | TODO |
| 6 — Rollout & Cleanup | Enable feature flag in production; remove flag scaffolding after stabilization period | Phase 5 signed off | TODO |

> **TODO:** Populate effort column (person-days) once the "moderate" upgrade option details are confirmed.

---

## Component Changes

> **TODO:** Specific file paths, class names, and package structures cannot be confirmed because the codebase context was not provided. The following describes the **expected structural changes** using standard Spring Boot conventions. All names must be verified against the actual codebase during Phase 1.

### 1. Security Configuration Class
- **New file:** `src/main/java/.../security/SecurityConfig.java`
- Defines a `@Configuration @EnableWebSecurity` class.
- Exposes a `SecurityFilterChain` bean that:
  - Disables CSRF (stateless JWT API).
  - Sets session management to `STATELESS`.
  - Configures `permitAll()` on the login/token endpoint.
  - Applies `authenticated()` to all other REST endpoints.
- Registers the `JwtAuthenticationFilter` before `UsernamePasswordAuthenticationFilter`.

### 2. JWT Token Provider
- **New file:** `src/main/java/.../security/JwtTokenProvider.java`
- Methods:
  - `generateToken(Authentication authentication) → String`
  - `validateToken(String token) → boolean`
  - `getUsernameFromToken(String token) → String`
- Reads signing secret and expiry from `application.properties` / `application.yml` keys:
  - `app.jwt.secret`
  - `app.jwt.expiration-ms`

### 3. JWT Authentication Filter
- **New file:** `src/main/java/.../security/JwtAuthenticationFilter.java`
- Extends `OncePerRequestFilter`.
- Overrides `doFilterInternal`: extracts `Authorization: Bearer <token>` header, validates token, sets `SecurityContextHolder`.

### 4. Authentication Controller (Login Endpoint)
- **New or modified file:** `src/main/java/.../controller/AuthController.java`
- Exposes `POST /api/auth/login` (path is **TODO** — confirm with team).
- Accepts `LoginRequest` DTO (username, password).
- Returns `JwtResponse` DTO (token, expiry).

### 5. UserDetailsService Implementation
- **New file:** `src/main/java/.../security/AppUserDetailsService.java`
- Implements `UserDetailsService`.
- `loadUserByUsername(String username)` — integrates with existing user repository.
- **TODO:** Identify existing user/account entity and repository class names.

### 6. Feature Flag Configuration
- **Modified file:** `src/main/resources/application.properties` (or `.yml`)
- New key: `app.security.jwt.enabled=false` (default off during rollout).
- `SecurityConfig` conditionally activates full filter chain based on this flag.
- **TODO:** Confirm whether a feature-flag framework (e.g., Togglz, LaunchDarkly, Spring Cloud Config) is already in use.

### 7. Exception Handling
- **New or modified file:** `src/main/java/.../security/JwtAuthenticationEntryPoint.java`
- Implements `AuthenticationEntryPoint`.
- Returns `401 Unauthorized` JSON response on missing/invalid token.

---

## Dependency Upgrade Plan

> **TODO:** All version numbers below are marked TODO because the tech analysis did not supply current or target versions. These **must** be populated from the confirmed tech analysis before Phase 2 begins. Do not use training-data version guesses.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `spring-boot-starter-security` | TODO | TODO | TODO | Adds auto-configured security; all endpoints become protected by default — requires explicit `permitAll` configuration |
| `spring-security-test` (test scope) | TODO | TODO | TODO | Required for `@WithMockUser`, `MockMvc` security integration tests |
| JWT library (e.g., `io.jsonwebtoken:jjwt-api`, `jjwt-impl`, `jjwt-jackson`) | TODO (not present) | TODO | N/A — new dependency | Confirm library choice (JJWT vs Nimbus JOSE); align with team's preference |
| `spring-boot-starter-web` | TODO | TODO | TODO | Confirm already present; no change expected |

> **TODO:** Run `./mvnw dependency:tree` or `./gradlew dependencies` to capture current versions and confirm no transitive conflicts with the chosen JWT library.

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. The following items must be investigated during Phase 1.

- **TODO:** Confirm whether the JWT signing secret should be injected as an environment variable or Kubernetes Secret rather than stored in `application.properties`.
- **TODO:** Confirm whether the CI pipeline has a security scanning step (e.g., OWASP Dependency-Check, Snyk) that should be updated to include new JWT dependencies.
- **TODO:** Confirm whether API gateway or load balancer terminates TLS — JWT over plain HTTP is insecure; TLS must be enforced at some layer.
- **TODO:** Confirm Docker base image and whether it needs updating to support the target Spring Boot version.

---

## Rollback Strategy

Each phase is independently reversible:

| Phase | Rollback Action |
|-------|----------------|
| Phase 2 — Dependency Integration | Revert dependency additions in `pom.xml` / `build.gradle`; rebuild and redeploy. Spring Boot will start without Security on classpath. |
| Phase 3 — Security Configuration | Set `app.security.jwt.enabled=false` in config; restart application. Security filter chain will not activate. No code removal required. |
| Phase 4 — Endpoint Protection | Same as Phase 3 — feature flag disables enforcement. Alternatively, revert `SecurityConfig` authorization rules to `permitAll()` on all endpoints. |
| Phase 5 — Testing | No production impact; revert test code only if it causes CI failures. |
| Phase 6 — Production Rollout | Set `app.security.jwt.enabled=false` via config server or environment variable; restart pods/containers. Token issuance endpoint becomes inactive. Clients revert to unauthenticated access during rollback window. |

> **Key principle:** The feature flag in `application.properties` / environment config is the primary rollback lever for Phases 3–6 and must be operable without a code redeploy.

---

## Testing Strategy

### Unit Tests
- **Tool:** JUnit 5 + Mockito (TODO: confirm already in use)
- `JwtTokenProviderTest`: test `generateToken`, `validateToken` (valid, expired, tampered, wrong signature), `getUsernameFromToken`.
- `JwtAuthenticationFilterTest`: mock `HttpServletRequest` with and without `Authorization` header; verify `SecurityContextHolder` state.
- **Coverage target:** ≥ 90% line coverage on all classes in the `security` package.

### Integration Tests
- **Tool:** Spring Boot Test (`@SpringBootTest`) + `MockMvc` + `spring-security-test`
- Test `POST /api/auth/login` with valid credentials → assert 200 + token in response.
- Test `POST /api/auth/login` with invalid credentials → assert 401.
- Test protected endpoint without token → assert 401.
- Test protected endpoint with valid token → assert 200.
- Test protected endpoint with expired token → assert 401.
- Test protected endpoint with tampered token → assert 401.

### Regression Tests
- Re-run existing endpoint integration tests with the feature flag **disabled** to confirm zero regression on current behavior.
- Re-run with flag **enabled** to confirm all previously passing tests still pass when valid tokens are supplied.

### Security-Specific Tests
- **Tool:** TODO (consider OWASP ZAP, or manual curl-based scripts in CI)
- Verify `Authorization` header is not logged.
- Verify token is rejected after expiry.
- Verify algorithm confusion attack is not possible (reject `alg: none`).

### CI Gates
- All unit and integration tests must pass before merge to main.
- Coverage gate: security package ≥ 90% (TODO: configure in Jacoco / build tool).
- TODO: Add OWASP Dependency-Check scan as a CI step gating the dependency upgrade PR.

---

## Timeline

> **TODO:** All estimated completion dates and owners are marked TODO because the "moderate" upgrade option person-days estimate was not provided and team structure is unknown. Populate after Phase 1 discovery and team assignment.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Codebase audit complete; versions confirmed | Phase 1 | TODO | TODO |
| Dependencies added; green build confirmed | Phase 2 | TODO | TODO |
| `SecurityConfig`, `JwtTokenProvider`, filter implemented | Phase 3 | TODO | TODO |
| Login endpoint live; all endpoints protected (flag off) | Phase 4 | TODO | TODO |
| Full test suite passing; coverage gate met | Phase 5 | TODO | TODO |
| Feature flag enabled in production; flag scaffolding removed | Phase 6 | TODO | TODO |

---

*Document status: **DRAFT — pending Phase 1 discovery to resolve all TODO items.** No implementation should begin until runtime, build tool, and dependency versions are confirmed and this document is updated.*