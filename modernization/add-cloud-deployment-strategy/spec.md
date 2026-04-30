# Software Modernization Specification Document

## Current State
- **Existing Interfaces:** The current system lacks any defined cloud interfaces; all operations are performed on-premise.
- **APIs:** APIs are primarily RESTful services hosted on local servers, with limited scalability and high maintenance overhead.
- **Data Models:** The data is stored in a monolithic structure with no cloud-native configurations.
- **Key Behaviours:** The application deploys on-site and uses traditional load balancers without cloud elasticity or automatic scaling capabilities.

## Target State
- **Existing Interfaces:** Interfaces will be transitioned to cloud-native APIs that support REST and GraphQL, enhancing responsiveness and scalability.
- **APIs:** APIs will be hosted on cloud platforms (AWS, Azure, GCP) taking advantage of managed services for scalability.
- **Data Models:** The data model will be restructured to utilize cloud-based storage solutions (e.g., AWS S3, Azure Blob) to leverage distributed architecture.
- **Key Behaviours:** The application will utilize cloud orchestration tools (like Kubernetes) for load balancing, auto-scaling, and resilience, with APIs having clear documentation and service level agreements.

## Compatibility & Breaking Changes
- **Breaking Change 1:** Change from on-premise REST services to cloud-hosted API endpoints.
  - **Migration Path:** Transition API calls to reference new cloud endpoints. Update authentication mechanisms to handle cloud security protocols such as OAuth2.
  
- **Breaking Change 2:** Shift from monolithic data stores to cloud-native databases.
  - **Migration Path:** Migrate existing database data to a cloud database service (e.g., Amazon RDS, Azure SQL). Utilize ETL (Extract, Transform, Load) processes to ensure data integrity during migration.

## Key Flows (before vs after)
1. **Flow 1 - User Authentication:**
   - **Before:** User sends login credentials to on-premise server.
   - **After:** User sends login credentials to cloud API endpoint, which validates against a cloud-based user store.

2. **Flow 2 - Data Retrieval:**
   - **Before:** Request to retrieve data hits the local database server.
   - **After:** Request is routed to a cloud API that fetches data from a cloud database service.

3. **Flow 3 - Deployment Process:**
   - **Before:** Manual deployment to on-prem servers.
   - **After:** Automated CI/CD pipeline in the cloud using cloud services like AWS CodePipeline or Azure DevOps for seamless deployments.

## Data Model Changes
- **Current Data Model:** Monolithic relational database schema.
- **Target Data Model:**
  - **Table:** Users  
    - Fields: `user_id`, `username`, `password_hash`, `email`, `created_at`  
  - **Modified Table:** Products  
    - Fields: `product_id`, `name`, `description`, `price`, `available_stock` (now stored in a cloud database like Amazon DynamoDB or Azure Cosmos DB for scalability).

## Configuration Changes
- **Environment Variables:**
  - **NEW:** `CLOUD_PROVIDER` to specify which cloud service provider is in use (e.g., AWS, Azure).
  - **NEW:** `API_ENDPOINT` to define the base URL for cloud-hosted APIs.

- **Feature Flags:**
  - **NEW:** `ENABLE_CLOUD_DEPLOYMENT` flag to toggle cloud-based services.
  
- **Config Files:**
  - **NEW:** `cloud-config.yml` to include configurations specific to cloud deployment settings, such as regions, services, and access keys.