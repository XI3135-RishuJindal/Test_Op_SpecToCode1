# Software Modernization Design Document

## Architecture Overview
### Before
The current architecture consists of an ASP.NET Web API application that may be using an older version of .NET Framework. The application is deployed on traditional servers but lacks modern deployment mechanisms such as containers or cloud resources.

### After
The updated architecture will utilize the latest stable version of ASP.NET Core Web API. This will allow for improved performance, features, and deployment options including Docker containers and potential orchestration through Kubernetes, providing greater scalability and flexibility across cloud resources.

## Migration Strategy
The chosen migration approach is the **strangler fig** pattern. This approach allows for gradually transitioning components of the application to the new framework while keeping the existing application operational until all pieces are converted. This reduces the risk associated with a big-bang migration.

## Component Changes
1. **API Controllers**: Refactor controllers to inherit from `ControllerBase` instead of `ApiController` for improved attributes and routing. The route attributes may also need to be updated to align with new conventions in ASP.NET Core.
   
2. **Middleware**: Implement new middleware for cross-cutting concerns such as error handling and logging that are more robust in ASP.NET Core.
   
3. **Dependency Injection**: Register services with the built-in dependency container which may involve reconfiguring service lifetimes (transient, scoped, singleton).

4. **Configuration**: Transition from XML-based configuration to a more modern options pattern using `IConfiguration`, allowing for easier integration with cloud-native services.

## Dependency Upgrade Plan

| Dependency          | Current Version | Target Version | Migration Notes                       |
|---------------------|------------------|-----------------|---------------------------------------|
| Microsoft.AspNet.WebApi | 5.x              | 6.x             | Refactor API controllers and services according to ASP.NET Core conventions. |
| Newtonsoft.Json    | 12.x             | 13.x            | Update code to handle any breaking changes in serialization/deserialization features.  |
| Entity Framework    | 6.x              | 7.x             | Update to the latest version of Entity Framework Core, requiring DbContext and repository logic updates. |

## CI/CD Pipeline Changes
- Update the build pipeline to target .NET 6, which may involve modifying YAML configurations for Azure DevOps or similar CI/CD tools.
- Introduce container build steps for Docker to package the application for deployment.
- Implement automated testing stages to ensure code quality during the transition, integrating tests early in the CI/CD pipeline.

## Infrastructure Changes
- Introduce Docker to containerize the application, ensuring consistency in development and production environments.
- Consider using Kubernetes for orchestration if necessary, potentially transitioning from traditional server deployments to cloud hosting on platforms like AWS or Azure.

## Rollback Plan
If the upgrade fails, revert to the previous version of the application by:
1. Restoring the previous application code from version control.
2. Redeploying the old version using the existing infrastructure.
3. Implementing any necessary hotfixes to stabilize the environment before retrying the upgrade.

## Testing Strategy
- **Unit Tests**: Update existing unit tests to reflect changes in the API structure and ensure core functionality works as intended.
- **Integration Tests**: Create new integration tests for the updated middleware and services to validate that components interact correctly.
- **Regression Tests**: Conduct regression testing to ensure that existing features function correctly without introducing new defects post-migration.
- **Performance Tests**: Evaluate performance of the new version under load to compare against benchmarks set by the old version.