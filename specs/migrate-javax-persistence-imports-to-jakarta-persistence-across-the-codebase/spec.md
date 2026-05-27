# Spec: Migrate `javax.persistence` Imports to `jakarta.persistence`

## Summary

This spec covers the migration of all `javax.persistence` import statements and references to their `jakarta.persistence` equivalents across the codebase. The expected outcome is a codebase that is fully compatible with the Jakarta EE 9+ namespace, eliminating all remaining `javax.persistence` references and unblocking adoption of modern Jakarta Persistence-compatible runtimes and frameworks.

---

## Motivation

The Java EE to Jakarta EE transition introduced a mandatory package namespace change from `javax.*` to `jakarta.*` as of Jakarta EE 9 (released 2020). The `javax.persistence` namespace is no longer maintained or updated under the old package name.

- **EOL / Namespace freeze:** The `javax.persistence` namespace received its final release under Java EE 8. No further updates, bug fixes, or security patches are issued under this namespace.
- **Incompatibility risk:** Modern versions of Jakarta Persistence (3.0+), Hibernate 6+, EclipseLink 3+, and Spring Boot 3+ exclusively use the `jakarta.persistence` namespace. Any dependency upgrade to these versions will cause compile-time or runtime failures if `javax.persistence` imports remain.
- **Upgrade urgency:** Medium — the codebase is not yet broken, but continued use of `javax.persistence` creates a hard blocker for any future dependency upgrades to Jakarta EE 9+ compatible libraries.
- **Tech debt:** Retaining `javax.persistence` imports couples the codebase to an unmaintained namespace and defers an increasingly costly migration the longer it is postponed.

> **Note:** Specific CVE identifiers, runtime versions, and build tool versions were not provided in the tech analysis. See [Open Questions](#open-questions).

---

## Current State

The codebase currently uses the `javax.persistence` package namespace throughout its persistence layer. The following categories of references are affected:

**Import statements and annotations in use (representative, not exhaustive):**

| Category | Current Reference |
|---|---|
| Core annotations | `javax.persistence.Entity`, `javax.persistence.Table`, `javax.persistence.Id`, `javax.persistence.GeneratedValue`, `javax.persistence.Column` |
| Relationship annotations | `javax.persistence.OneToMany`, `javax.persistence.ManyToOne`, `javax.persistence.ManyToMany`, `javax.persistence.OneToOne`, `javax.persistence.JoinColumn`, `javax.persistence.JoinTable` |
| Lifecycle & fetch | `javax.persistence.FetchType`, `javax.persistence.CascadeType`, `javax.persistence.GenerationType` |
| EntityManager API | `javax.persistence.EntityManager`, `javax.persistence.EntityManagerFactory`, `javax.persistence.Persistence` |
| Query API | `javax.persistence.Query`, `javax.persistence.TypedQuery`, `javax.persistence.NamedQuery`, `javax.persistence.NamedQueries` |
| Transaction | `javax.persistence.EntityTransaction` |
| Embeddable / inheritance | `javax.persistence.Embeddable`, `javax.persistence.Embedded`, `javax.persistence.MappedSuperclass`, `javax.persistence.Inheritance`, `javax.persistence.InheritanceType` |
| Locking | `javax.persistence.LockModeType`, `javax.persistence.Version` |
| Persistence unit config | `persistence.xml` referencing `javax.persistence` schema namespace and provider class names |
| Criteria API | `javax.persistence.criteria.*` |
| Metamodel | `javax.persistence.metamodel.*` |

> **TODO:** A full inventory of affected classes, configuration keys, and schema elements requires a codebase scan. Specific class names, config file locations, and persistence unit names are not available from the provided context.

---

## Proposed Changes

### Summary Table

| Component | Before | After | Breaking? |
|---|---|---|---|
| Entity class imports | `javax.persistence.*` | `jakarta.persistence.*` | Y |
| Repository / DAO class imports | `javax.persistence.EntityManager` etc. | `jakarta.persistence.EntityManager` etc. | Y |
| Criteria API imports | `javax.persistence.criteria.*` | `jakarta.persistence.criteria.*` | Y |
| Metamodel imports | `javax.persistence.metamodel.*` | `jakarta.persistence.metamodel.*` | Y |
| `persistence.xml` XML namespace | `xmlns="http://java.sun.com/xml/ns/persistence"` or `http://xmlns.jcp.org/xml/ns/persistence` | `https://jakarta.ee/xml/ns/persistence` | Y |
| `persistence.xml` schema version | `version="2.x"` | `version="3.0"` or `version="3.1"` | Y |
| JPA provider configuration | `javax.persistence.*` property keys in `persistence.xml` or equivalent config | `jakarta.persistence.*` property keys | Y |
| Build dependency declarations | `javax.persistence:javax.persistence-api` or `org.hibernate:hibernate-core` (pre-6) | `jakarta.persistence:jakarta.persistence-api` or equivalent Jakarta-compatible artifact | Y |

### What Is Removed
- All `import javax.persistence.*` and specific `javax.persistence.<Type>` import statements.
- All `javax.persistence.*` property key strings in configuration files.
- The `javax.persistence` API dependency artifact from the build configuration.

### What Is Added
- Equivalent `import jakarta.persistence.*` and specific `jakarta.persistence.<Type>` import statements replacing every removed import on a one-for-one basis.
- `jakarta.persistence.*` property key strings in configuration files where applicable.
- The `jakarta.persistence-api` dependency artifact (version TODO) in the build configuration.

> **Note:** No new persistence behaviour is introduced. This migration is a namespace-only change; the JPA API surface is functionally equivalent between `javax.persistence` and `jakarta.persistence` at the targeted version.

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `javax.persistence` imports no longer compile against `jakarta.persistence-api` | All entity, repository, and service classes that import `javax.persistence` types will fail to compile | Replace every `javax.persistence` import with the corresponding `jakarta.persistence` import on a one-for-one basis |
| `persistence.xml` XML namespace change | Persistence unit configuration will be rejected by Jakarta-compliant providers if the old namespace is retained | Update the `xmlns` and `xsi:schemaLocation` attributes in `persistence.xml` to the Jakarta EE 9+ namespace URI |
| `persistence.xml` property key prefix change | Properties prefixed with `javax.persistence.` (e.g., JDBC URL, DDL generation) will be ignored by Jakarta-only providers | Rename all `javax.persistence.*` property keys to `jakarta.persistence.*` equivalents |
| JPA provider artifact change | The old `javax.persistence-api` artifact will conflict with or be absent from Jakarta-compatible provider classpaths | Remove the old artifact dependency; add the `jakarta.persistence-api` artifact at the appropriate version |
| Hibernate / EclipseLink version alignment | If the JPA provider is upgraded alongside this migration (e.g., Hibernate 5 → 6), additional provider-specific breaking changes may apply | TODO — provider-specific migration paths depend on the current provider version, which was not supplied in the tech analysis |
| Spring / framework integration | Spring Boot 2.x uses `javax.persistence`; Spring Boot 3.x uses `jakarta.persistence` | TODO — framework version alignment path depends on current Spring/framework version, not provided |
| Third-party libraries that expose `javax.persistence` types in their APIs | Callers passing or receiving `javax.persistence` types from third-party APIs will break if those libraries are not also migrated | TODO — requires audit of third-party library versions in the dependency tree |

---

## Acceptance Criteria

1. **Given** the migrated codebase, **when** a full compilation is performed, **then** zero compilation errors or warnings referencing `javax.persistence` are produced.

2. **Given** the migrated codebase, **when** a static search for the string `javax.persistence` is executed across all source files and configuration files, **then** zero occurrences are found.

3. **Given** the migrated codebase, **when** a static search for the string `jakarta.persistence` is executed across all source files that previously contained `javax.persistence` references, **then** every previously identified `javax.persistence` reference has a corresponding `jakarta.persistence` replacement.

4. **Given** the migrated `persistence.xml` (or equivalent configuration), **when** the file is validated against the Jakarta Persistence 3.x XML schema, **then** validation passes with no errors.

5. **Given** the migrated codebase, **when** all existing unit tests are executed, **then** the test suite passes with no regressions compared to the pre-migration baseline (same number of passing tests, no new failures).

6. **Given** the migrated codebase, **when** all existing integration tests that exercise persistence operations (persist, find, merge, remove, query) are executed, **then** all tests pass with no regressions.

7. **Given** a running application instance built from the migrated codebase, **when** a basic CRUD operation is performed against the configured data store, **then** the operation completes successfully and data is persisted and retrieved correctly.

8. **Given** the build dependency configuration, **when** the dependency tree is inspected, **then** no artifact providing the `javax.persistence` API namespace appears on the compile or runtime classpath.

9. **Given** the migrated codebase, **when** a CI pipeline build is executed from a clean state, **then** the build completes successfully end-to-end with no `javax.persistence`-related errors.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the current runtime and its version (e.g., Spring Boot 2.x, Quarkus, Jakarta EE server)? This determines whether additional framework-level namespace changes are required alongside the import migration. | TODO | TODO |
| 2 | What is the current JPA provider and version (e.g., Hibernate 5.x, EclipseLink 2.x)? This determines whether a provider upgrade is required concurrently and what additional breaking changes apply. | TODO | TODO |
| 3 | What is the target `jakarta.persistence-api` version (3.0, 3.1, or 3.2)? | TODO | TODO |
| 4 | What build tool is in use (Maven, Gradle, other)? This affects how dependency changes are specified and how the migration can be automated or verified. | TODO | TODO |
| 5 | Are there any third-party libraries in the dependency tree that expose `javax.persistence` types in their public APIs (e.g., shared DTOs, query result types)? If so, those libraries must be upgraded or replaced before or alongside this migration. | TODO | TODO |
| 6 | Are there any generated sources (e.g., JPA metamodel classes, code-generation tools) that emit `javax.persistence` imports? If so, the code-generation tooling must also be updated. | TODO | TODO |
| 7 | Is there a `orm.xml` or other XML mapping file in addition to `persistence.xml` that references the `javax.persistence` namespace? | TODO | TODO |
| 8 | Does the codebase include any string literals that reference `javax.persistence` property keys at runtime (e.g., passed programmatically to `EntityManagerFactory`)? These will not be caught by a simple import scan. | TODO | TODO |
| 9 | What is the agreed rollback strategy if the migration causes unforeseen runtime failures in a deployed environment? | TODO | TODO |