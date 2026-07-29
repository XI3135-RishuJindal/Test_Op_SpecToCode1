```csharp
using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class WishlistController : ControllerBase
    {
        private readonly ILogger<WishlistController> _logger;

        public WishlistController(ILogger<WishlistController> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Gets all wishlist items for the user
        /// </summary>
        /// <returns>A list of wishlist items</returns>
        [HttpGet]
        public async Task<IActionResult> GetWishlist()
        {
            _logger.LogInformation("Fetching wishlist items");
            // Logic to fetch wishlist items from the service
            return Ok(new { Items = new string[] { "Item1", "Item2" } });
        }

        /// <summary>
        /// Adds a new item to the wishlist
        /// </summary>
        /// <param name="item"></param>
        /// <returns>ActionResult</returns>
        [HttpPost]
        public async Task<IActionResult> AddToWishlist([FromBody] string item)
        {
            _logger.LogInformation("Adding item to wishlist: {Item}", item);
            // Logic to add item to wishlist
            return Ok();
        }

        /// <summary>
        /// Removes an item from the wishlist by ID
        /// </summary>
        /// <param name="id"></param>
        /// <returns>ActionResult</returns>
        [HttpDelete("{id}")]
        public async Task<IActionResult> RemoveFromWishlist(int id)
        {
            _logger.LogInformation("Removing item from wishlist with ID: {Id}", id);
            // Logic to remove item
            return Ok();
        }

        /// <summary>
        /// Reorders items in the wishlist
        /// </summary>
        /// <param name="itemOrder"></param>
        /// <returns>ActionResult</returns>
        [HttpPut("reorder")]
        public async Task<IActionResult> ReorderWishlist([FromBody] int[] itemOrder)
        {
            _logger.LogInformation("Reordering wishlist items");
            // Logic for reordering items
            return Ok();
        }
    }
}
```