# Proposal: Upgrade Java 8 to Java 21 and Spring Boot to 3.3.0

## Purpose and Business Value
The primary purpose of this upgrade is to modernize the codebase by transitioning from Java 8 to Java 21, which will provide support for the latest language features, and improve performance and security. Additionally, upgrading Spring Boot to the latest stable release (3.3.0) is crucial for ensuring continued support and security. This upgrade addresses critical vulnerabilities and enhances the overall maintainability of the system.

## In-Scope
- Upgrade Java runtime from version 8 to 21.
- Upgrade Spring Boot framework from 2.3.12.RELEASE to 3.3.0.
- Update Log4j and Jackson Databind dependencies to secure versions.
- Improve the test coverage to enhance code reliability.

## Out-of-Scope
- Complete re-architecture to microservices.
- Implementation of Docker containerization and advanced CI/CD practices.

## Responsibilities
- Ensure compatibility of existing codebase with Java 21 language features.
- Ensure that the latest security patches are applied through dependency upgrades.
- Maintain or improve the current system's performance post-upgrade.

## Impacted/Depending Systems and Data Stores
- Source code and build scripts.
- Existing test suites and build processes.
- Maven dependency management.

## Acceptance Criteria
- The application runs successfully on Java 21 with Spring Boot 3.3.0 without runtime errors.
- All critical security vulnerabilities addressed, notably CVE-2021-44228.
- Comprehensive tests cover new and existing functionality, passing with no failures.
- Build processes are updated and compatible with modern Java features.