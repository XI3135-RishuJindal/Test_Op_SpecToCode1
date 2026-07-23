### User Story: Add Product to Wishlist

**What:**
This feature allows users to add products to their wishlist directly from the product page. A wishlist serves as a collection of items that users are interested in purchasing later or tracking for price changes.

**Why:**
Enabling users to add to a wishlist increases user engagement and the likelihood of future purchases by enabling users to easily revisit products they're interested in.

**Acceptance Criteria:**
- Users can add any product displayed on the product page to their wishlist.
- A confirmation message is displayed once a product is added successfully.
- Users cannot add the same product to the wishlist more than once.
- The wishlist should be saved to the user's account and persist across different sessions and devices.
- If not authenticated, users should be redirected to the login page or prompted to log in.

**Out-of-Scope:**
- Sharing wishlist with others.
- Managing multiple wishlists (e.g. categorizing wishlists).
- Notifications related to wishlist activity (such as price changes or availability alerts).

**Cross-Service Dependencies:**
- User authentication service for verifying logged-in status.
- Database storage for persisting wishlist data.