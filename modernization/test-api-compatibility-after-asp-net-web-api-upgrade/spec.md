# Software Modernization Specification Document

## Current State
- **Interfaces**: The current API interface is built using ASP.NET Web API version 5.2. It exposes REST endpoints that utilize JSON for data exchange and includes custom header handling for authentication.
- **APIs**: The existing API endpoints include:
  - `GET /api/products`
  - `POST /api/products`
  - `GET /api/products/{id}`
  - `PUT /api/products/{id}`
  - `DELETE /api/products/{id}`
- **Data Models**: The data models are defined using C# classes, e.g., `Product` with properties like `Id`, `Name`, and `Price`.
- **Key Behaviours**: Current behaviors include authorization via legacy token methods, lack of asynchronous programming models, and limited exception handling mechanisms.

## Target State
- **Interfaces**: After the upgrade to ASP.NET Web API version 6.0, interfaces will be based on the newer ASP.NET Core framework, utilizing attribute routing and improved middleware support.
- **APIs**: The API endpoints will remain largely the same, but enhanced with:
  - Improved performance due to built-in support for asynchronous actions.
  - Change in routing attributes to utilize `[Route]` instead of conventional routing.
- **Data Models**: Data models will be migrated to use new features in C# 8.0, such as nullable reference types.
- **Key Behaviours**: The new version will include modern authentication methods (e.g., JWT), enhanced exception handling with middleware, and improved logging capabilities.

## Compatibility & Breaking Changes
1. **Routing Changes**: 
   - **Breaking Change**: Legacy routing syntax will no longer be recognized.
   - **Migration Path**: Update routes in controllers from traditional routing attributes to attribute-based routing with `[Route("api/[controller]")]`.

2. **Authentication Changes**:
   - **Breaking Change**: Legacy token authentication will be replaced by JWT.
   - **Migration Path**: Update to utilize the new `JwtBearerDefaults.AuthenticationScheme`.

3. **Return Types**:
   - **Breaking Change**: The return types will be migrated from standard `IHttpActionResult` to `ActionResult<T>`.
   - **Migration Path**: Modify all action methods to return the appropriate `ActionResult<T>` type.

## Key Flows (before vs after)
1. **Getting a Product**:
   - **Before**: 
     1. Client sends `GET /api/products/1`.
     2. API retrieves the product from the database.
     3. Returns product data in JSON format.
   - **After**: 
     1. Client sends `GET /api/products/{id}`.
     2. API retrieves the product using async method.
     3. Returns product data in JSON format with improved error handling.

2. **Creating a Product**:
   - **Before**:
     1. Client sends `POST /api/products` with product data.
     2. API processes data synchronously.
   - **After**:
     1. Client sends `POST /api/products` with product data.
     2. API processes data asynchronously, handling validation and response.

## Data Model Changes
- **Product Class**: 
  - **Before**:
    ```csharp
    public class Product {
        public int Id { get; set; }
        public string Name { get; set; }
        public decimal Price { get; set; }
    }
    ```
  - **After**:
    ```csharp
    public class Product {
        public int Id { get; set; }
        public string? Name { get; set; } // Nullable reference type
        public decimal Price { get; set; }
    }
    ```

## Configuration Changes
- **Environment Variables**: 
  - **Before**: 
    - `AUTH_TOKEN_SECRET`
  - **After**:
    - `JWT_SECRET`
  
- **Feature Flags**: 
  - **N/A — not applicable to this task**

- **Config Files**:
  - **Before**: `Web.config` 
  - **After**: `appsettings.json` to manage configurations and secrets.

