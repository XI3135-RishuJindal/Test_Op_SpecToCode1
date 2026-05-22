## Prerequisites
- N/A — not applicable to this task

## Phase 1 — Preparation
- [XS] Create feature branch jest-setup in repository root
- [S] Inventory JavaScript/TypeScript viability by verifying presence of package.json in repository root
- [XS] Detect package manager by checking for package-lock.json, yarn.lock, or pnpm-lock.yaml in repository root
- [S] Discover existing test framework by inspecting devDependencies and scripts.test in package.json
- [XS] Create docs/jest/README.md to record decisions and baseline for Jest adoption in docs/jest/README.md

## Phase 2 — Core Upgrade
- [S] Add devDependency jest and initialize basic test script in package.json (add scripts.test="jest" and scripts.test:watch="jest --watch" in package.json)
- [XS] Create Jest config with Node environment in jest.config.js at repository root (module.exports = { testEnvironment: 'node' })
- [XS] If using TypeScript (tsconfig.json exists), add devDependencies ts-jest and @types/jest and set preset: 'ts-jest' in package.json and jest.config.js
- [XS] Create a smoke test to validate Jest runs by adding __tests__/smoke.test.js with a trivial assertion in __tests__/smoke.test.js
- [XS] Ignore build and coverage artifacts by appending coverage/ and junit/ (if present) to .gitignore in .gitignore
- [XS] Add coverage scripts by adding scripts.test:coverage="jest --coverage" in package.json
- [XS] Configure Jest to ignore compiled artifacts by adding testPathIgnorePatterns: ['<rootDir>/dist/', '<rootDir>/build/'] in jest.config.js
- [S] If an existing test script uses another runner (e.g., mocha or jasmine) in package.json, add parallel script scripts.test:legacy to preserve legacy run in package.json

## Phase 3 — Testing & Validation
- [XS] Execute Jest locally and document results by recording pass/fail summary in docs/jest/README.md in docs/jest/README.md
- [XS] Adjust Jest transform defaults if TypeScript is present by adding transform for ts/tsx via ts-jest in jest.config.js
- [XS] Add basic coverage thresholds to prevent regressions by adding coverageThreshold: { global: { lines: 60, statements: 60, branches: 50, functions: 60 } } in jest.config.js
- [S] Create baseline test coverage report and persist summary numbers in docs/jest/COVERAGE_BASELINE.md in docs/jest/COVERAGE_BASELINE.md

## Phase 4 — CI/CD & Infrastructure
- N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [XS] Document how to run tests (npm/yarn/pnpm) by adding a “Testing with Jest” section in README.md
- [XS] Add a changelog entry “feat(test): add Jest and baseline config” in CHANGELOG.md
- [XS] Update contributing guidelines to require passing Jest tests before commit in CONTRIBUTING.md
- [XS] Record Jest adoption decision, trade-offs, and version in docs/jest/README.md in docs/jest/README.md