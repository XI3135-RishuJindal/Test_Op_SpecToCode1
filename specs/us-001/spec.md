# US-001: Add Product to Cart

## Overview
As a shopper, I want to add products to my cart and see it updated immediately, so that I have a smooth and accurate shopping experience.

## Functional Specification

### Narrative
Shoppers can add a quantity of a specific, available product to their cart using an API endpoint. The cart reflects the updated contents without delay. If the product is out of stock, it must not be added and the user is notified. At any time, when viewing the cart, product quantities and availability are kept accurate via real-time inventory lookups.

### Acceptance Criteria

1. **Success:** When the user adds a product (in stock) with a specified quantity via the API, that item appears in their cart and the cart state is returned promptly in API response.
2. **Out of Stock:** When the user tries to add a product that is out of stock, the item is not added to the cart, and an error message is returned.
3. **Cart View:** When the cart is viewed, it accurately reflects all added items, with correct product details, quantities, and up-to-date availability.
4. **Inventory Sync:** If the cart is viewed after product inventory changes (e.g., item becomes out of stock), the cart contents are automatically updated or flagged (e.g., with "out of stock" status).
5. **API Error Handling:** All error scenarios (e.g., invalid productId, invalid quantity, unauthenticated/unauthorized) return a structured error response.

### Success Metrics
- Cart operations must provide user feedback in less than 500ms.
- Cart and inventory must remain in sync.

### Out of Scope
- Persistent cart storage (use in-memory for now, database integration future).
- Guest/anonymous user carts (require authenticated user).
- Discount/coupon logic.
- UI code (API only, not front-end logic).

### Cross-Service Dependencies
- Inventory service or an inventory API for real-time product availability checks. If not yet available, use an inventory mock/interface to allow rapid development and future integration.