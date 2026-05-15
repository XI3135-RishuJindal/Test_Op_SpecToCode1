Architecture decisions
- Use GitHub Actions as the CI runner to ensure consistent, auditable scans on PRs, pushes, and a weekly schedule.
- Implement detection logic in a repository script (scripts/scan-dependencies.ps1) to keep YAML minimal and allow local execution.
- Centralize denylist patterns in .github/dependency-rules/payment-denylist.txt to enable governance via code review.
- Treat both direct and transitive dependencies as policy-relevant. For .NET, leverage dotnet list package --include-transitive --format json.
- Provide an explicit override via PR label allow-payment-sdks. The workflow reads labels to decide whether to fail or only warn.

Component design
- Workflow file: .github/workflows/dependency-scan.yml
  - Triggers: pull_request, push on main, schedule weekly cron.
  - Jobs:
    - backend_scan: Runs on ubuntu-latest; sets up .NET 8; executes scripts/scan-dependencies.ps1 in pwsh; uploads artifacts; conditionally fails on findings.
- Script: scripts/scan-dependencies.ps1
  - Inputs: denylist path (.github/dependency-rules/payment-denylist.txt), override flag from env (ALLOW_FAILURE=false/true), repo root.
  - Steps:
    - dotnet restore
    - dotnet list ApiGateway.cs