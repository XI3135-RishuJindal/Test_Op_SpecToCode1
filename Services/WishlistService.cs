```csharp
using ApiGateway.Data;

namespace ApiGateway.Services
{
    public class WishlistService
    {
        private readonly ApplicationDbContext _context;

        public WishlistService(ApplicationDbContext context)
        {
            _context = context;
        }

        public bool AddProductToWishlist(string userId, int productId)
        {
            if (_context.WishlistItems.Any(x => x.UserId == userId && x.ProductId == productId))
            {
                return false;
            }

            var wishlistItem = new WishlistItem
            {
                UserId = userId,
                ProductId = productId
            };

            _context.WishlistItems.Add(wishlistItem);
            _context.SaveChanges();

            return true;
        }
    }
}
```

#### Integration Test for Wishlist Feature