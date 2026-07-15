XI3135-RishuJindal/Test_Op_SpecToCode1

Controllers & Models:
- [ ] add Controllers/CartController.cs: implement endpoints POST /api/cart/add, GET /api/cart, handle success/error per spec
- [ ] add Models/CartItemDTO.cs: cart item (productId, name, quantity, status)
- [ ] add Models/CartDTO.cs: list of CartItemDTOs and summary
- [ ] add Models/AddToCartRequest.cs: request model for add endpoint

Inventory & Cart Logic:
- [ ] add Services/IInventoryService.cs: contract for inventory lookups
- [ ] add Services/InMemoryInventoryService.cs: simulate inventory/availability
- [ ] add CartStore (internal class or static utility) for per-user in-memory cart storage; plug in inventory service

Wiring & Setup:
- [ ] update Program.cs: register inventory service for DI
- [ ] ensure Models/ErrorResponse.cs is reused for all exceptional scenarios
- [ ] add Swagger docs/comments to new endpoints

Testing:
- [ ] add Tests/Controllers/CartControllerTests.cs: test all acceptance criteria (in-stock, out of stock, cart reflection of inventory change, error paths)
- [ ] update README.md with new endpoint details if needed