To implement the "Add Product to Wishlist" feature, the following steps and decisions are necessary:

1. **Architecture Decisions:**
   - Implement a new `WishlistController` in the ApiGateway for handling wishlist actions.
   - Incorporate wishlist operations in a new model `WishlistDTO` to represent wishlist objects.
   - Use existing authentication mechanisms to ensure only authenticated users can add items to their wishlist.

2. **API Contract:**
   - A new endpoint `/api/wishlist` with POST method to add products to the user's wishlist.
   - Endpoint parameters include user identification from authentication token and the product ID.

3. **Data Model Changes:**
   - Introduce a new database table to map user IDs to product IDs and store timestamp for when a product was added.

4. **Code Changes:**
   - Create `WishlistController.cs` in `Controllers/`.
   - Add `WishlistDTO.cs` in `Models/`.
   - Modify `Program.cs` to register new services for wishlist operations.
   - Include tests for the new controller in `Tests/Controllers/WishlistControllerTests.cs`.

5. **Review and Validation:**
   - Conduct thorough code review for adherence to coding standards and security practices.
   - Perform functionality testing to validate that all acceptance criteria are met.