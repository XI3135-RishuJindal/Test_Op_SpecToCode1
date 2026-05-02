# Design Document for ASP.NET Web API Upgrade

## Architecture Overview
### Before
The existing architecture of the ASP.NET Web API consists of a monolithic application built on an older version of the ASP.NET framework. The application is hosted on IIS with a traditional deployment model and relies on outdated libraries which may lead to maintenance challenges and security vulnerabilities.

### After
Post-upgrade, the architectural design will take advantage of the latest ASP.NET Core features, providing improved performance, cross-platform capabilities, and better support for microservices. The application will utilize middleware for processing requests, make use of dependency injection natively, and operate in a cloud or containerized environment (Docker/Kubernetes) for increased scalability and flexibility.

## Migration Strategy
The chosen migration approach is the **strangler fig** pattern. We will gradually replace parts of the legacy application with new components built using the latest version of ASP.NET Core. This allows for a controlled migration with minimal downtime. Legacy APIs will run alongside the new API, and functionality will be migrated iteratively.

## Component Changes
- **Controllers**: Convert existing API controllers to ASP.NET Core controllers to leverage dependency injection and middleware capabilities.
- **Data Access Layer**: Upgrade to Entity Framework Core for better performance and feature support compared to the previous ORM.
- **Routing**: Implement endpoint routing available in ASP.NET Core to modernize the routing approach.
- **Configuration**: Migrate to the new configuration system using appsettings.json rather than web.config.
  
All these changes aim to enhance maintainability, performance, and future-proofing of the application.

## Dependency Upgrade Plan
| dependency            | current version | target version | migration notes                                   |
|-----------------------|-----------------|----------------|--------------------------------------------------|
| Microsoft.AspNet.WebApi | 5.2.7          | 6.0.0         | Transition to ASP.NET Core version and modify APIs accordingly. |
| Newtonsoft.Json       | 8.0.3           | 13.0.1        | Update for compatibility with new ASP.NET Core JSON serialization. |
| EntityFramework       | 6.2.0           | 6.4.4         | Upgrade to EF Core for improved data access.    |
| Microsoft.AspNetCore.Mvc | N/A          | 6.0.0         | Introduce ASP.NET Core MVC to replace existing Web API. |

## CI/CD Pipeline Changes
- **Build Process**: Update build scripts to utilize `dotnet build` instead of MSBuild for creating .NET Core applications.
- **Testing**: Integrate xUnit as the testing framework instead of the legacy framework used in the earlier version.
- **Deployment**: Set up Azure DevOps or GitHub Actions to enable automated deployments to the containerized environment.

## Infrastructure Changes
- **Docker**: Introduce Docker to containerize the ASP.NET Core application, allowing for easier deployment and management.
- **Kubernetes**: Set up Kubernetes for orchestration to manage its deployment, scaling, and operation.
- **Cloud Resources**: Transition from traditional IIS hosting to Azure App Services or other cloud solutions to provide scalability and ease of management.

## Rollback Plan
In case the upgrade fails:
1. Redeploy the old version of the application from the last stable production build.
2. Restore database backups if needed to maintain data integrity until the migration is resolved.
3. Update routing rules to redirect traffic back to the legacy application endpoints.

## Testing Strategy
- **Unit Testing**: Implement unit tests for each new controller and service to ensure functionality is intact post-migration.
- **Integration Testing**: Develop tests that validate the integration of new components with existing databases and middleware.
- **Regression Testing**: Carry out automated regression tests to ensure that the existing functionality remains unaffected.
- **Performance Testing**: Conduct performance benchmarks to verify that the new version meets or exceeds the current performance metrics.