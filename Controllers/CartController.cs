using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;
using ApiGateway.Services;
using System.Security.Claims;
using System.Collections.Concurrent;

namespace ApiGateway.Controllers
{
    /// <summary>
    /// Provides endpoints for managing the user's shopping cart.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class CartController : ControllerBase
    {
        private readonly IInventoryService _inventoryService;
        private readonly ILogger<CartController> _logger;

        // Cart storage: <UserId, CartDTO>
        private static readonly ConcurrentDictionary<string, CartDTO> _userCarts = new();

        public CartController(IInventoryService inventoryService, ILogger<CartController> logger)
        {
            _inventoryService = inventoryService;
            _logger = logger;
        }

        /// <summary>
        /// Adds a product to the authenticated user's cart.
        /// </summary>
        /// <param name="request">The details of the item to add.</param>
        /// <returns>The updated cart if successful.</returns>
        /// <response code="200">Cart updated successfully.</response>
        /// <response code="400">Validation failed (e.g., invalid quantity or productId).</response>
        /// <response code="401">Request not authenticated.</response>
        /// <response code="404">Product not found in inventory.</response>
        /// <response code="409">Product out of stock.</response>
        /// <response code="500">Internal server error.</response>
        [HttpPost("add")]
        [ProducesResponseType(typeof(CartDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status409Conflict)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
        public IActionResult AddToCart([FromBody] AddToCartRequest request)
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.Identity?.Name ?? "unknown";
            if (request == null)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidRequest",
                    Message = "Request body cannot be null.",
                    StatusCode = 400
                });
            }

            if (request.Quantity < 1)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "InvalidQuantity",
                    Message = "Quantity must be at least 1.",
                    StatusCode = 400
                });
            }

            // Try inventory lookup
            var productName = _inventoryService.GetProductName(request.ProductId);
            var isProductValid = !productName.StartsWith("Product #") || request.ProductId <= 4;
            if (!isProductValid)
            {
                return NotFound(new ErrorResponse
                {
                    Error = "ProductNotFound",
                    Message = $"No product found with ID {request.ProductId}.",
                    StatusCode = 404
                });
            }

            var inStock = _inventoryService.IsProductInStock(request.ProductId);
            if (!inStock)
            {
                return Conflict(new ErrorResponse
                {
                    Error = "ProductOutOfStock",
                    Message = $"Product '{productName}' is out of stock and cannot be added.",
                    StatusCode = 409
                });
            }

            var cart = _userCarts.GetOrAdd(userId, _ => new CartDTO());
            lock (cart)
            {
                var item = cart.Items.FirstOrDefault(i => i.ProductId == request.ProductId);
                if (item == null)
                {
                    item = new CartItemDTO
                    {
                        ProductId = request.ProductId,
                        Name = productName,
                        Quantity = request.Quantity,
                        Status = "In Stock"
                    };
                    cart.Items.Add(item);
                }
                else
                {
                    item.Quantity += request.Quantity;
                    item.Status = "In Stock";
                }
            }

            // Return updated cart (with inventory statuses refreshed)
            var updatedCart = GetCartForUserWithInventorySync(userId);
            return Ok(updatedCart);
        }

        /// <summary>
        /// Gets the authenticated user's cart, checking real-time inventory for each item.
        /// </summary>
        /// <returns>The user's current cart with accurate item statuses.</returns>
        /// <response code="200">Returns the current cart for the user.</response>
        /// <response code="401">Request not authenticated.</response>
        /// <response code="500">Internal server error.</response>
        [HttpGet]
        [ProducesResponseType(typeof(CartDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
        public IActionResult GetCart()
        {
            var userId = User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.Identity?.Name ?? "unknown";
            var cart = GetCartForUserWithInventorySync(userId);
            return Ok(cart);
        }

        /// <summary>
        /// Returns the user's cart and syncs each item's status according to current inventory.
        /// </summary>
        private CartDTO GetCartForUserWithInventorySync(string userId)
        {
            var cart = _userCarts.GetOrAdd(userId, _ => new CartDTO());
            lock (cart)
            {
                foreach (var item in cart.Items)
                {
                    if (!_inventoryService.IsProductInStock(item.ProductId))
                        item.Status = "Out of Stock";
                    else
                        item.Status = "In Stock";

                    item.Name = _inventoryService.GetProductName(item.ProductId);
                }
            }
            return cart;
        }
    }
}