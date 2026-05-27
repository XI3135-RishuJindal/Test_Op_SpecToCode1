# Tasks: Migrate `javax.persistence` → `jakarta.persistence`

> **Scope:** Replace all `javax.persistence` import statements and references with `jakarta.persistence` equivalents across the codebase. No runtime, build tool, or framework specifics were provided in the tech analysis — tasks are scoped strictly to what is known.

---

## Prerequisites

- [ ] [XS] Confirm the target Jakarta Persistence API version (e.g., `jakarta.persistence-api 3.x`) is available in the project's dependency registry before any code changes begin
- [ ] [XS] Verify that every developer and CI agent has read/write access to the repository and can open pull requests against the main integration branch
- [ ] [XS] Confirm a full test suite (unit + integration) exists and is runnable locally, so a pre-migration baseline can be captured

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated migration branch (e.g., `migrate/javax-to-jakarta-persistence`) from the current default branch
- [ ] [S] Run a full-codebase grep/search for all occurrences of `javax.persistence` (imports, fully-qualified references, string literals, XML/config files) and record the count as the migration baseline — save output to `migration-baseline.txt` in the branch root
- [ ] [XS] Run the existing test suite on the migration branch before any changes and record pass/fail counts as the pre-migration baseline in `migration-baseline.txt`
- [ ] [XS] Confirm no other in-flight branches modify the same persistence-annotated classes to avoid merge conflicts during the migration window

---

## Phase 2 — Core Upgrade

- [ ] [M] Replace all `import javax.persistence.*` and explicit `import javax.persistence.<Type>` statements with `import jakarta.persistence.*` / `import jakarta.persistence.<Type>` across every source file identified in the Phase 1 grep output
- [ ] [S] Replace all fully-qualified `javax.persistence.<Type>` references (i.e., usages not covered by import statements, such as in annotations with string values or reflection calls) with their `jakarta.persistence.<Type>` equivalents across the codebase
- [ ] [S] Update any `persistence.xml`, `orm.xml`, or equivalent JPA configuration files that reference `javax.persistence` namespace URIs or schema locations to use the `jakarta.persistence` equivalents
- [ ] [XS] Search for `javax.persistence` in any string literals (e.g., `Class.forName("javax.persistence.Entity")`, log messages, or constants) and update each occurrence to `jakarta.persistence`
- [ ] [XS] Verify no residual `javax.persistence` references remain by re-running the grep from Phase 1 and confirming zero matches — document result in `migration-baseline.txt`

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite (unit + integration) on the migration branch and compare pass/fail counts against the pre-migration baseline recorded in `migration-baseline.txt`
- [ ] [S] Investigate and resolve any test failures introduced by the import migration (e.g., classpath issues, missing `jakarta.persistence` provider on the test classpath)
- [ ] [XS] Confirm zero occurrences of `javax.persistence` remain in compiled class files or test output by inspecting build artifacts (e.g., `javap` spot-check or equivalent)

---

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task. No CI/CD pipeline, Docker, or IaC details were provided in the tech analysis, and the migration is limited to source-level import changes.

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry describing the `javax.persistence` → `jakarta.persistence` migration, the files affected (count from baseline), and the Jakarta Persistence API version now in use
- [ ] [XS] Open the migration pull request against the default branch, referencing `migration-baseline.txt` and the zero-match grep result as evidence of completeness
- [ ] [XS] After merge, monitor the first post-merge CI run and any staging deployment for `ClassNotFoundException` or `NoClassDefFoundError` related to `javax.persistence` or `jakarta.persistence` and resolve immediately if found