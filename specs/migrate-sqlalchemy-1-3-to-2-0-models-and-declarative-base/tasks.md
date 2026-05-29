# Tasks: Migrate SQLAlchemy 1.3 → 2.0 — Models and Declarative Base

## Prerequisites

- [ ] [XS] Confirm Python environment has `pip` and `virtualenv` (or equivalent) available and that the project's virtual environment is active before beginning any dependency changes
- [ ] [XS] Verify current installed SQLAlchemy version is 1.3.x by running `pip show sqlalchemy` and record the exact version in a migration notes file (e.g., `MIGRATION_NOTES.md`)
- [ ] [XS] Confirm access to the project repository with write permissions and the ability to open pull requests against the main branch
- [ ] [S] Install SQLAlchemy 2.0 migration tooling — specifically `sqlalchemy-migrate` audit utilities and the `python -W error::DeprecationWarning` flag approach — to surface 1.x legacy patterns before touching code

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated migration branch (e.g., `migrate/sqlalchemy-2.0`) from the current default branch before making any changes
- [ ] [S] Audit all files that import from `sqlalchemy` or `sqlalchemy.ext.declarative` using `grep -rn "from sqlalchemy\|import sqlalchemy"` across the codebase and record every affected module in `MIGRATION_NOTES.md`
- [ ] [S] Capture a full test baseline by running the existing test suite (unit + integration) on the `1.3.x` install and saving the output (pass/fail counts, coverage report) to `baseline_test_results.txt` for regression comparison
- [ ] [XS] Pin SQLAlchemy to `>=1.4,<2.0` in `requirements.txt` (or `pyproject.toml` / `setup.cfg` — whichever is present) as an intermediate step, since 1.4 is the bridge release that surfaces 2.0 deprecation warnings without breaking existing code
- [ ] [S] Run the full test suite under SQLAlchemy 1.4 with `SQLALCHEMY_WARN_20=1` environment variable set and capture all emitted `RemovedIn20Warning` deprecation warnings to `deprecation_warnings.txt` — this becomes the authoritative work list for Phase 2

---

## Phase 2 — Core Upgrade

- [ ] [M] Replace all uses of `from sqlalchemy.ext.declarative import declarative_base` with `from sqlalchemy.orm import DeclarativeBase` (new 2.0 base class pattern) in every model file identified in Phase 1, and define a single project-level `Base` subclass (e.g., in `models/base.py` or equivalent)
- [ ] [M] Migrate all ORM model classes to inherit from the new `DeclarativeBase`-derived `Base` class, removing any legacy `Base = declarative_base()` call sites across all model files
- [ ] [M] Replace all `Column` declarations using the legacy positional type syntax with the 2.0 `mapped_column()` function and add `Mapped[<type>]` type annotations to every column attribute in all model classes (e.g., `id: Mapped[int] = mapped_column(primary_key=True)`)
- [ ] [M] Update all `relationship()` declarations in model files to use `Mapped[<RelatedType>]` annotations (e.g., `children: Mapped[List["Child"]] = relationship()`) and remove any `backref` string arguments in favour of explicit `back_populates`
- [ ] [S] Replace all `Session.execute(query)` calls that use the legacy `Query` API (i.e., `session.query(Model).filter(...)`) with the 2.0 `select()` construct style (`session.execute(select(Model).where(...))`) in every service or repository module identified in the audit
- [ ] [S] Remove all remaining uses of the legacy `Query` object (`.query()` accessor on `Session`) and replace with `select()` statements in any remaining data-access modules
- [ ] [S] Update `engine` and `Session` creation code — replace `engine = create_engine(url)` patterns that rely on deprecated keyword arguments, and replace `Session(bind=engine)` with `sessionmaker(bind=engine)` or the 2.0 `Session(engine)` form as appropriate in the database setup module (e.g., `db.py`, `database.py`, or `session.py`)
- [ ] [XS] Bump SQLAlchemy from `>=1.4,<2.0` to `>=2.0,<3.0` in `requirements.txt` (or `pyproject.toml` / `setup.cfg`) once all code changes above are complete
- [ ] [S] Run the full test suite immediately after the version bump and fix any remaining `AttributeError` or `ArgumentError` exceptions caused by removed 1.x APIs not caught by the 1.4 deprecation warnings

---

## Phase 3 — Testing & Validation

- [ ] [M] Execute the full test suite (unit + integration) against SQLAlchemy 2.0 and compare pass/fail counts and any new failures against `baseline_test_results.txt` captured in Phase 1
- [ ] [S] Write or update integration tests that exercise the `Base` metadata (e.g., `Base.metadata.create_all(engine)`) and at least one round-trip `INSERT`/`SELECT` per migrated model to confirm schema creation and ORM mapping are correct under 2.0
- [ ] [S] Verify that no `RemovedIn20Warning` or `LegacyAPIWarning` warnings remain by running the test suite with `-W error::sqlalchemy.exc.RemovedIn20Warning` and confirming zero warnings in the output
- [ ] [XS] Confirm test coverage has not regressed below the baseline percentage recorded in Phase 1 using the project's existing coverage tooling (e.g., `pytest-cov`)

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or `.gitlab-ci.yml` — whichever is present) to install SQLAlchemy `>=2.0` in the test job's dependency installation step and remove any `SQLALCHEMY_WARN_20=1` environment variable that was added temporarily
- [ ] [XS] If a `Dockerfile` or container image definition exists and pins SQLAlchemy explicitly, update that pin to `sqlalchemy>=2.0` in the relevant `RUN pip install` or `requirements*.txt` reference within the image build context

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `MIGRATION_NOTES.md` (or `CHANGELOG.md`) with a summary of all breaking changes addressed, the new `DeclarativeBase` pattern adopted, and any model-level API changes that downstream contributors need to be aware of
- [ ] [XS] Update any inline docstrings or module-level comments in model files that reference SQLAlchemy 1.x API patterns (e.g., references to `declarative_base`, `Query`, or `backref`) to reflect the 2.0 equivalents
- [ ] [S] Conduct a staged rollout by merging the migration branch to a staging or pre-production environment first, verifying database schema creation and query behaviour against a real database instance before merging to the main branch