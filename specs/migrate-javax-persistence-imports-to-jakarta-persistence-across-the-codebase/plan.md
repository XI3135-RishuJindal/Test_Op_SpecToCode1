# PLAN: Migrate `javax.persistence` → `jakarta.persistence`

> **Spec reference:** Migrate javax.persistence imports to jakarta.persistence across the codebase
> **Option:** moderate
> **Status:** Draft

---

## Overview

**Strategy: Big-Bang Migration (with feature-flag-gated validation)**

The migration replaces `javax.persistence.*` import statements and any associated configuration references with their `jakarta.persistence.*` equivalents across the entire codebase in a single coordinated effort.

**Justification:**
- `javax.persistence` and `jakarta.persistence` packages are **mutually exclusive** at runtime — mixing them within the same persistence unit causes classloading conflicts and is not a viable long-term parallel-run state.
- A strangler-fig approach is not practical here because the persistence layer is typically a cross-cutting concern; partial migration would require maintaining two separate EntityManagerFactory configurations simultaneously, adding significant complexity with little benefit.
- The upgrade urgency is rated **medium**, meaning there is no emergency pressure, but the scope is well-understood and bounded — a big-bang approach with a thorough test gate is the lowest-risk path.
- The effort is moderate and primarily mechanical (find-and-replace + dependency version bump), making a single-phase cutover tractable.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Audit & Inventory** — Identify all files containing `javax.persistence` imports, annotations, and XML/properties config references. Produce a full impact list. | Access to full codebase | 0.5 person-days |
| 2 | **Dependency Upgrade** — Update build file(s) to replace `javax.persistence` artifact(s) with `jakarta.persistence-api` at the target version. Resolve any transitive conflicts. | Phase 1 complete | 0.5 person-days |
| 3 | **Import & Annotation Migration** — Execute automated find-and-replace of `javax.persistence` → `jakarta.persistence` across all source files. Manually review edge cases (e.g., string literals, XML descriptors, `persistence.xml`). | Phase 2 complete | 1 person-day |
| 4 | **Validation & Testing** — Run full test suite (unit, integration, regression). Fix any compilation errors or runtime failures surfaced by the migration. | Phase 3 complete | 1 person-day |
| 5 | **Merge & Release** — Code review, merge to main branch, tag release, deploy to staging for smoke test. | Phase 4 complete | 0.5 person-days |

**Total estimated effort: ~3.5 person-days**

---

## Component Changes

> **NOTE:** Specific file names, class names, and method names are not available in the provided context. The changes below are described structurally. Once the Phase 1 audit is complete, this section should be updated with concrete file paths.

### JPA Entity Classes
- **What changes:** All `import javax.persistence.*` statements replaced with `import jakarta.persistence.*`.
- **Annotations affected:** `@Entity`, `@Table`, `@Column`, `@Id`, `@GeneratedValue`, `@ManyToOne`, `@OneToMany`, `@ManyToMany`, `@OneToOne`, `@JoinColumn`, `@Embeddable`, `@Embedded`, `@MappedSuperclass`, `@NamedQuery`, `@NamedNativeQuery`, `@Enumerated`, `@Temporal`, `@Lob`, `@Transient`, `@Version`, `@PrePersist`, `@PostPersist`, etc.
- **Files affected:** TODO — enumerate from Phase 1 audit (expected pattern: `**/model/*.java`, `**/entity/*.java`, `**/domain/*.java`).

### Repository / DAO Classes
- **What changes:** Any direct use of `javax.persistence.EntityManager`, `javax.persistence.EntityManagerFactory`, `javax.persistence.Query`, `javax.persistence.TypedQuery`, `javax.persistence.criteria.*` replaced with `jakarta.persistence.*` equivalents.
- **Files affected:** TODO — enumerate from Phase 1 audit (expected pattern: `**/repository/*.java`, `**/dao/*.java`).

### Configuration / Bootstrap Classes
- **What changes:** Any programmatic JPA configuration referencing `javax.persistence` provider strings or class literals updated to `jakarta.persistence`.
- **Files affected:** TODO — e.g., `persistence.xml`, `orm.xml`, Spring `@Configuration` classes, Quarkus `application.properties` JPA keys.

### XML Descriptors
- **What changes:** `persistence.xml` namespace/schema URLs may need updating from `http://java.sun.com/xml/ns/persistence` to `https://jakarta.ee/xml/ns/persistence` depending on the JPA provider version targeted.
- **Files affected:** TODO — `src/main/resources/META-INF/persistence.xml` (if present).

### String Literals & Reflection
- **What changes:** Any string literals containing `"javax.persistence"` (e.g., provider class names, JPQL hints, property keys) must be reviewed manually — automated replacement may not catch these.
- **Files affected:** TODO — surface via `grep -r '"javax\.persistence'` during audit.

---

## Dependency Upgrade Plan

> **NOTE:** The tech analysis did not supply specific current or target version numbers, build tool, or framework versions. The table below documents the structural change required. **All version numbers must be confirmed from the project's actual build file before execution — do not use values from this table as-is.**

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `javax.persistence:javax.persistence-api` (or equivalent) | TODO — confirm from build file | TODO — confirm target (e.g., `jakarta.persistence:jakarta.persistence-api:3.x`) | Package namespace changes from `javax.persistence` to `jakarta.persistence`; not binary-compatible | Remove old artifact; add `jakarta.persistence:jakarta.persistence-api` at confirmed target version |
| JPA Provider (e.g., Hibernate, EclipseLink) | TODO | TODO | Provider must support Jakarta Persistence API; older Hibernate 5.x uses `javax`, Hibernate 6.x uses `jakarta` | Confirm provider version supports `jakarta.persistence`; may require provider upgrade in tandem |
| Framework integration (e.g., Spring Boot, Quarkus) | TODO | TODO | Spring Boot 3.x requires Jakarta EE 9+; Spring Boot 2.x uses `javax` | If framework is Spring Boot, migration to 3.x is a prerequisite or co-requisite |

---

## Infrastructure Changes

TODO — No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. Once the runtime environment is known, assess:

- **Docker base image:** If the base image pins a JDK or application server that bundles `javax.persistence`, the image may need updating (e.g., moving from a Jakarta EE 8 to Jakarta EE 10 base image).
- **CI/CD pipeline:** Ensure the pipeline runs the full test suite post-migration (see Testing Strategy). No structural pipeline changes are anticipated for a pure import migration.
- **IaC:** TODO — not derivable from provided context.

---

## Rollback Strategy

Each phase produces a discrete, reversible artifact (a commit or branch). Rollback is performed by reverting the relevant commit(s).

| Phase | Rollback Action |
|-------|----------------|
| **Phase 1 — Audit** | No code changes made; discard audit notes. No rollback needed. |
| **Phase 2 — Dependency Upgrade** | Revert the build file commit that changed the dependency coordinates. Restore the original `javax.persistence` artifact reference and version. Run `./mvnw dependency:resolve` (or equivalent) to confirm restoration. |
| **Phase 3 — Import Migration** | Revert the commit(s) containing import replacements. If done on a feature branch, simply delete or abandon the branch. Confirm compilation succeeds against the reverted dependency. |
| **Phase 4 — Validation** | No additional rollback action; test fixes are on the feature branch. Abandon the branch if validation cannot be completed. |
| **Phase 5 — Merge & Release** | If a defect is discovered post-merge: create a revert commit on main (`git revert <merge-commit-sha>`), redeploy the previous artifact from the artifact registry. Tag the revert as a patch release. |

**Key principle:** All migration work should be performed on a dedicated feature branch. The main branch is not affected until Phase 5, making rollback before that point a zero-risk branch deletion.

---

## Testing Strategy

### Unit Tests
- **Scope:** Entity classes, value objects, any utility that uses JPA annotations.
- **Goal:** Confirm all annotated classes compile and that annotation processors (e.g., Hibernate Validator, Lombok) resolve correctly against `jakarta.persistence`.
- **Tool:** TODO — confirm from project (JUnit 5 / TestNG expected).
- **CI Gate:** Build must compile with zero errors; all existing unit tests must pass.

### Integration Tests
- **Scope:** Repository/DAO layer against an in-memory or containerized database.
- **Goal:** Confirm `EntityManager` operations (persist, find, query, merge, remove) function correctly under the new namespace.
- **Tool:** TODO — confirm from project (expected: Testcontainers + PostgreSQL/H2, or Spring Boot Test slice `@DataJpaTest`).
- **CI Gate:** All integration tests pass; zero `ClassNotFoundException` or `NoSuchMethodError` for `jakarta.persistence` types.

### Regression Tests
- **Scope:** Full application smoke test covering all persistence-backed endpoints or use cases.
- **Goal:** Confirm no runtime regressions in JPQL queries, lazy loading, transaction demarcation, or schema validation.
- **Tool:** TODO — confirm from project (e.g., REST-assured, Postman/Newman, Cucumber).
- **CI Gate:** All regression scenarios pass on staging before release tag is applied.

### Performance Tests
- N/A for this migration — the change is purely at the API/import level and does not alter query execution paths. If a JPA provider version upgrade is performed in tandem, a baseline performance comparison is recommended (TODO: confirm if provider upgrade is in scope).

### Coverage Target
- TODO — adopt the project's existing coverage threshold. No regression in line/branch coverage is acceptable as a result of this migration.

---

## Timeline

> Effort derived from the moderate upgrade option (~3.5 person-days total). Calendar dates are expressed as relative working days from kick-off (T+0). Assign actual dates and owners once the team is confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; impact list signed off | Phase 1 — Audit & Inventory | T+1 (0.5 days) | TODO |
| Build file updated; dependency conflict-free | Phase 2 — Dependency Upgrade | T+2 (0.5 days) | TODO |
| All source files migrated; compiles clean | Phase 3 — Import & Annotation Migration | T+3 (1 day) | TODO |
| Full test suite green on feature branch | Phase 4 — Validation & Testing | T+4 (1 day) | TODO |
| Merged to main; staging smoke test passed; release tagged | Phase 5 — Merge & Release | T+5 (0.5 days) | TODO |

---

*Document status: Draft — pending Phase 1 audit to populate TODO items with concrete file names, versions, and owners.*