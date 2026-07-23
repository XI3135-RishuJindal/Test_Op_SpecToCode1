```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;
using System.Security.Claims;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class WishlistController : ControllerBase
    {
        private readonly WishlistService _wishlistService;

        public WishlistController(WishlistService wishlistService)
        {
            _wishlistService = wishlistService;
        }

        /// <summary>
        /// Adds a product to the user's wishlist.
        /// </summary>
        /// <param name="wishlistItem">Details of the product to add to the wishlist.</param>
        /// <returns>A confirmation of the product being added.</returns>
        [HttpPost]
        public IActionResult AddToWishlist([FromBody] WishlistDTO wishlistItem)
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);

            if (!_wishlistService.AddProductToWishlist(userId, wishlistItem.ProductId))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "DuplicateProduct",
                    Message = "The product is already in the wishlist."
                });
            }

            return Ok(new { Message = "Product added to wishlist successfully." });
        }
    }
}
```

#### Define Data Transfer Object for Wishlist