# Proposal: Upgrade Java to 21

## Purpose and Business Value
This proposal outlines the necessary steps to upgrade the project's Java version from 8 to 21. The primary goal is to ensure that the application is running on a supported and up-to-date platform, enhancing security, performance, and compatibility with modern frameworks such as Spring Boot 3.3.x.

## In-Scope
- Upgrade Java from version 8 to 21.
- Upgrade Spring Boot from 2.3.12.RELEASE to 3.3.x.
- Upgrade critical dependencies, notably Log4j and Jackson Databind, to remove vulnerabilities and ensure compatibility.
- Perform necessary code refactoring to accommodate the upgrades.

## Out-of-Scope
- Full re-architecture to microservices.
- Containerization and orchestration with Docker and Kubernetes.

## Responsibilities
- Ensure compatibility with new Java and Spring Boot versions.
- Address known security vulnerabilities.
- Update application dependencies and perform testing to ensure stability.

## Impacted/Depending Systems and Data Stores
- Source code and associated libraries.
- No impact on the H2 database external connections.

## Acceptance Criteria
- All existing functionality remains stable post-upgrade.
- No known vulnerabilities are present after the upgrade.
- Successfully built and tested with the updated runtime and dependencies.
```

```markdown