```csharp
using Microsoft.EntityFrameworkCore;
using ApiGateway.Models;

namespace ApiGateway.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options) : base(options)
        {
        }

        public DbSet<WishlistItem> WishlistItems { get; set; }
    }
}
```

#### Define Wishlist Item Entity