## Plan to Deliver "Add Product to Cart"

### Architecture Decisions
- Implement a new CartController in Controllers/CartController.cs.
- Use a CartItemDTO and CartDTO in Models/ to represent cart items and the full cart.
- The cart will be stored in-memory, keyed by user identifier (from JWT), using a simple singleton or static dictionary.
- Add an IInventoryService interface (Models/ or Services/, relocate later if needed) with a basic InMemoryInventoryService for simulating product availability. All add/view actions will check live inventory using this service.
- Secure all endpoints (JWT authentication required).
- Expose endpoints:
    - POST /api/cart/add — add product to cart
    - GET /api/cart — get current cart for user (with inventory status check on each item)
- Extend error handling using the existing ErrorResponse model.
- Enable Swagger docs for these endpoints.

### API Contracts
- **POST /api/cart/add**
    - Request: { "productId": int, "quantity": int }
    - Response: { cart: CartDTO }
- **GET /api/cart**
    - Response: { cart: CartDTO }

### File/Repo Changes
- Add: Controllers/CartController.cs
- Add: Models/CartItemDTO.cs and Models/CartDTO.cs
- Add: Models/AddToCartRequest.cs for incoming add requests
- Add: Services/IInventoryService.cs, Services/InMemoryInventoryService.cs
- Add: Utility for in-memory user cart storage (internal static dictionary or single class)
- Update: Program.cs for DI (add inventory service as singleton).
- Add: Tests/Controllers/CartControllerTests.cs with unit tests for logic and acceptance criteria.

## Notes
- Mock product/inventory for demo; real API version TBC.
- Ensure consistent error/result response format.
- Document endpoints in Swagger.