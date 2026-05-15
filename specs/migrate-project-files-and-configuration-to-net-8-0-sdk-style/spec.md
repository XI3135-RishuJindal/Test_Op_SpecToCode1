## Summary

This specification covers the migration of all project files and configuration in the repository to .NET 8.0, adopting SDK-style project files. The intended outcome is that all components build and run using the .NET 8.0 toolchain with project files that adhere to modern SDK-style standards, with identical or improved functional behavior.

## Motivation

Business and technical drivers for this migration include:
- .NET 8.0 is the current long-term support (LTS) version.
- Earlier non-SDK project formats are incompatible with the latest Visual Studio versions and tooling.
- Moving to SDK-style enables cleaner project files, improved build performance, lower tech debt, and easier adoption of modern tooling and features.
- Upgrade urgency is rated "medium" as per the tech analysis.

## Current State

- Nature and language of project files: unknown.
- Runtime, build tool, and framework versions: unknown.
- Existing project files are not SDK-style and are not targeting .NET 8.0.
- Specific interfaces, code elements, or configurations affected: unknown.
- N/A — not applicable to this task beyond the general need to modernize project file format and target framework.

## Proposed Changes

| Component  | Before                                                      | After                                               | Breaking? |
|------------|-------------------------------------------------------------|-----------------------------------------------------|-----------|
| Project files | Non-SDK-style (details unknown) targeting unknown framework(s) | SDK-style .NET project files targeting .NET 8.0     | Y         |
| Configurations | Legacy project and config structure (unknown specifics) | Configuration compatible with .NET 8.0 SDK-style    | Y (potentially) |
| Tooling    | Unspecified/unknown                                         | .NET 8.0 SDK and toolchain                         | Y         |

## Compatibility & Breaking Changes

| Breaking Change                                   | Migration Path                      |
|---------------------------------------------------|-------------------------------------|
| Non-SDK project files no longer supported         | TODO: Document how callers should update to SDK-style references |
| Legacy framework features not available in .NET 8 | TODO: Identify features/APIs not present in .NET 8 and provide rewrites or alternatives |
| Build toolchains and CI processes must use .NET 8 | TODO: Update project consumers to use .NET 8 SDK |
| Application runtime behavior may change           | TODO: Regression test all core workflows and update documentation |

## Acceptance Criteria

1. Given a developer machine with only .NET 8.0 SDK installed, when a clean build is run on every project, then all targets succeed without errors.
2. Given a CI environment using .NET 8.0 SDK, when the automated build and test workflow is triggered, then all jobs pass.
3. Given an inspection of every project file, when reviewed, then each is confirmed to use SDK-style and targets .NET 8.0.
4. Given supported developer tooling (e.g., Visual Studio 2022 or later), when the solution is opened, then all projects load without upgrade prompts or compatibility warnings.
5. Given the default application workflows, when executed after migration, then outputs and behaviors match pre-migration outputs, modulo intentional SDK-style effects.

## Open Questions

| # | Question                                                                       | Owner (or TODO) | Due Date (or TODO) |
|---|--------------------------------------------------------------------------------|-----------------|-------------------|
| 1 | What are the precise languages, runtimes, and frameworks in the current state? | TODO            | TODO              |
| 2 | Are there any project-specific build, deploy, or config customizations?        | TODO            | TODO              |
| 3 | What are the post-migration test and validation processes?                     | TODO            | TODO              |
| 4 | Are any external dependencies or nuget packages incompatible with .NET 8.0?    | TODO            | TODO              |
| 5 | Do consumers or downstream systems require additional migration support?        | TODO            | TODO              |