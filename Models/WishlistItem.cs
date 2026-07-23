```csharp
namespace ApiGateway.Models
{
    public class WishlistItem
    {
        public int Id { get; set; }
        public string UserId { get; set; }
        public int ProductId { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
```

#### Implement Wishlist Service