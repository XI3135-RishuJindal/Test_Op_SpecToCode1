using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using ApiGateway.Models;

namespace ApiGateway.Controllers
{
    /// <summary>
    /// Provides RESTful endpoints for managing a user's personal wishlist.
    /// </summary>
    /// <remarks>
    /// All endpoints require a valid JWT bearer token issued by <see cref="AuthController"/>.
    /// The authenticated user's identity is extracted from the <c>NameIdentifier</c> claim
    /// so that each user can only access and modify their own wishlist items.
    ///
    /// Storage strategy (current implementation):
    ///   Items are held in a static, in-process dictionary keyed by user ID.
    ///   This is intentionally lightweight for the API Gateway layer; a production
    ///   deployment should replace <see cref="_store"/> with an injected repository
    ///   backed by a persistent data store (e.g. SQL Server, Cosmos DB).
    ///
    /// Accessibility / usability compliance:
    ///   The API surface follows REST conventions so that any accessible front-end
    ///   (screen-reader-friendly SPA, mobile app, etc.) can consume it uniformly.
    ///   Response shapes are kept flat and self-describing to ease client rendering.
    ///
    /// Scalability notes:
    ///   - The static dictionary must be replaced with a distributed cache or database
    ///     before horizontal scaling.
    ///   - All operations are O(n) over a user's items; an indexed store is recommended
    ///     once per-user item counts exceed a few hundred.
    /// </remarks>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    [Produces("application/json")]
    public class WishlistController : ControllerBase
    {
        // ---------------------------------------------------------------------------
        // In-memory store (replace with a proper repository in production)
        // Key: userId, Value: dictionary of itemId -> WishlistItemDTO
        // ---------------------------------------------------------------------------
        private static readonly Dictionary<string, Dictionary<Guid, WishlistItemDTO>> _store =
            new(StringComparer.OrdinalIgnoreCase);

        private static readonly object _lock = new();

        private readonly ILogger<WishlistController> _logger;

        /// <summary>
        /// Initialises a new instance of <see cref="WishlistController"/>.
        /// </summary>
        /// <param name="logger">Structured logger injected by the DI container.</param>
        public WishlistController(ILogger<WishlistController> logger)
        {
            _logger = logger;
        }

        // ---------------------------------------------------------------------------
        // Helper: resolve the current user's ID from the JWT claims
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Extracts the authenticated user's identifier from the current JWT claims.
        /// </summary>
        /// <returns>The user ID string, or <c>null</c> if the claim is absent.</returns>
        private string? GetCurrentUserId() =>
            User.FindFirstValue(ClaimTypes.NameIdentifier);

        // ---------------------------------------------------------------------------
        // GET api/wishlist
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Retrieves all wishlist items belonging to the authenticated user.
        /// </summary>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>200 OK – array of <see cref="WishlistItemDTO"/> (may be empty).</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        /// </list>
        /// </returns>
        /// <response code="200">Returns the user's wishlist items.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        [HttpGet]
        [ProducesResponseType(typeof(IEnumerable<WishlistItemDTO>), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        public IActionResult GetAll()
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation("GET /api/wishlist requested by user {UserId}", userId);

            lock (_lock)
            {
                var items = _store.TryGetValue(userId!, out var userItems)
                    ? userItems.Values.OrderByDescending(i => i.CreatedAt)
                    : Enumerable.Empty<WishlistItemDTO>();

                return Ok(items);
            }
        }

        // ---------------------------------------------------------------------------
        // GET api/wishlist/{id}
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Retrieves a single wishlist item by its unique identifier.
        /// </summary>
        /// <param name="id">The <see cref="Guid"/> identifier of the wishlist item.</param>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>200 OK – the requested <see cref="WishlistItemDTO"/>.</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        ///   <item><description>404 Not Found – item does not exist or belongs to another user.</description></item>
        /// </list>
        /// </returns>
        /// <response code="200">Returns the requested wishlist item.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        /// <response code="404">Item not found for the authenticated user.</response>
        [HttpGet("{id:guid}")]
        [ProducesResponseType(typeof(WishlistItemDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
        public IActionResult GetById(Guid id)
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation("GET /api/wishlist/{ItemId} requested by user {UserId}", id, userId);

            lock (_lock)
            {
                if (!_store.TryGetValue(userId!, out var userItems) ||
                    !userItems.TryGetValue(id, out var item))
                {
                    _logger.LogWarning("Wishlist item {ItemId} not found for user {UserId}", id, userId);
                    return NotFound(new ErrorResponse
                    {
                        Error = "ItemNotFound",
                        Message = $"Wishlist item '{id}' was not found.",
                        StatusCode = 404
                    });
                }

                return Ok(item);
            }
        }

        // ---------------------------------------------------------------------------
        // POST api/wishlist
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Adds a new item to the authenticated user's wishlist.
        /// </summary>
        /// <param name="request">
        /// The wishlist item to create. The <c>Id</c>, <c>UserId</c>, <c>CreatedAt</c>,
        /// and <c>UpdatedAt</c> fields are set server-side and any client-supplied values
        /// for those fields are ignored.
        /// </param>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>201 Created – the newly created <see cref="WishlistItemDTO"/>.</description></item>
        ///   <item><description>400 Bad Request – validation failure (e.g. missing <c>Name</c>).</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        /// </list>
        /// </returns>
        /// <response code="201">Item created successfully.</response>
        /// <response code="400">Request body failed validation.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        [HttpPost]
        [ProducesResponseType(typeof(WishlistItemDTO), StatusCodes.Status201Created)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        public IActionResult Create([FromBody] WishlistItemDTO request)
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation("POST /api/wishlist requested by user {UserId}", userId);

            // Validate required fields
            if (string.IsNullOrWhiteSpace(request.Name))
            {
                _logger.LogWarning("Create wishlist item failed: Name is required. User {UserId}", userId);
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Name' field is required and cannot be empty.",
                    StatusCode = 400
                });
            }

            if (request.Name.Length > 200)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Name' field must not exceed 200 characters.",
                    StatusCode = 400
                });
            }

            if (!string.IsNullOrEmpty(request.Description) && request.Description.Length > 1000)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Description' field must not exceed 1 000 characters.",
                    StatusCode = 400
                });
            }

            if (request.Priority < 1 || request.Priority > 5)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Priority' field must be between 1 (highest) and 5 (lowest).",
                    StatusCode = 400
                });
            }

            // Build the persisted item — server controls identity and timestamps
            var newItem = new WishlistItemDTO
            {
                Id          = Guid.NewGuid(),
                UserId      = userId!,
                Name        = request.Name.Trim(),
                Description = request.Description?.Trim() ?? string.Empty,
                Url         = request.Url,
                Price       = request.Price,
                Currency    = request.Currency,
                Tags        = request.Tags ?? new List<string>(),
                Priority    = request.Priority,
                IsPurchased = false,          // new items are never pre-marked as purchased
                CreatedAt   = DateTime.UtcNow,
                UpdatedAt   = null
            };

            lock (_lock)
            {
                if (!_store.ContainsKey(userId!))
                    _store[userId!] = new Dictionary<Guid, WishlistItemDTO>();

                _store[userId!][newItem.Id] = newItem;
            }

            _logger.LogInformation(
                "Wishlist item {ItemId} created for user {UserId} with name '{Name}'",
                newItem.Id, userId, newItem.Name);

            return CreatedAtAction(nameof(GetById), new { id = newItem.Id }, newItem);
        }

        // ---------------------------------------------------------------------------
        // PUT api/wishlist/{id}
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Replaces an existing wishlist item with the supplied data.
        /// </summary>
        /// <param name="id">The <see cref="Guid"/> identifier of the item to update.</param>
        /// <param name="request">
        /// The updated wishlist item data. The <c>Id</c>, <c>UserId</c>, and <c>CreatedAt</c>
        /// fields are preserved from the original record; <c>UpdatedAt</c> is set server-side.
        /// </param>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>200 OK – the updated <see cref="WishlistItemDTO"/>.</description></item>
        ///   <item><description>400 Bad Request – validation failure.</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        ///   <item><description>404 Not Found – item does not exist or belongs to another user.</description></item>
        /// </list>
        /// </returns>
        /// <response code="200">Item updated successfully.</response>
        /// <response code="400">Request body failed validation.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        /// <response code="404">Item not found for the authenticated user.</response>
        [HttpPut("{id:guid}")]
        [ProducesResponseType(typeof(WishlistItemDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
        public IActionResult Update(Guid id, [FromBody] WishlistItemDTO request)
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation("PUT /api/wishlist/{ItemId} requested by user {UserId}", id, userId);

            // Validate required fields (same rules as Create)
            if (string.IsNullOrWhiteSpace(request.Name))
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Name' field is required and cannot be empty.",
                    StatusCode = 400
                });
            }

            if (request.Name.Length > 200)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Name' field must not exceed 200 characters.",
                    StatusCode = 400
                });
            }

            if (!string.IsNullOrEmpty(request.Description) && request.Description.Length > 1000)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Description' field must not exceed 1 000 characters.",
                    StatusCode = 400
                });
            }

            if (request.Priority < 1 || request.Priority > 5)
            {
                return BadRequest(new ErrorResponse
                {
                    Error = "ValidationError",
                    Message = "The 'Priority' field must be between 1 (highest) and 5 (lowest).",
                    StatusCode = 400
                });
            }

            lock (_lock)
            {
                if (!_store.TryGetValue(userId!, out var userItems) ||
                    !userItems.TryGetValue(id, out var existing))
                {
                    _logger.LogWarning("Update failed: item {ItemId} not found for user {UserId}", id, userId);
                    return NotFound(new ErrorResponse
                    {
                        Error = "ItemNotFound",
                        Message = $"Wishlist item '{id}' was not found.",
                        StatusCode = 404
                    });
                }

                // Preserve immutable server-side fields
                existing.Name        = request.Name.Trim();
                existing.Description = request.Description?.Trim() ?? string.Empty;
                existing.Url         = request.Url;
                existing.Price       = request.Price;
                existing.Currency    = request.Currency;
                existing.Tags        = request.Tags ?? new List<string>();
                existing.Priority    = request.Priority;
                existing.IsPurchased = request.IsPurchased;
                existing.UpdatedAt   = DateTime.UtcNow;

                _logger.LogInformation(
                    "Wishlist item {ItemId} updated for user {UserId}", id, userId);

                return Ok(existing);
            }
        }

        // ---------------------------------------------------------------------------
        // DELETE api/wishlist/{id}
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Permanently removes a wishlist item belonging to the authenticated user.
        /// </summary>
        /// <param name="id">The <see cref="Guid"/> identifier of the item to delete.</param>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>204 No Content – item deleted successfully.</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        ///   <item><description>404 Not Found – item does not exist or belongs to another user.</description></item>
        /// </list>
        /// </returns>
        /// <response code="204">Item deleted successfully.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        /// <response code="404">Item not found for the authenticated user.</response>
        [HttpDelete("{id:guid}")]
        [ProducesResponseType(StatusCodes.Status204NoContent)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
        public IActionResult Delete(Guid id)
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation("DELETE /api/wishlist/{ItemId} requested by user {UserId}", id, userId);

            lock (_lock)
            {
                if (!_store.TryGetValue(userId!, out var userItems) ||
                    !userItems.ContainsKey(id))
                {
                    _logger.LogWarning("Delete failed: item {ItemId} not found for user {UserId}", id, userId);
                    return NotFound(new ErrorResponse
                    {
                        Error = "ItemNotFound",
                        Message = $"Wishlist item '{id}' was not found.",
                        StatusCode = 404
                    });
                }

                userItems.Remove(id);

                // Clean up the user's bucket if it is now empty
                if (userItems.Count == 0)
                    _store.Remove(userId!);
            }

            _logger.LogInformation(
                "Wishlist item {ItemId} deleted for user {UserId}", id, userId);

            return NoContent();
        }

        // ---------------------------------------------------------------------------
        // PATCH api/wishlist/{id}/purchased
        // ---------------------------------------------------------------------------

        /// <summary>
        /// Marks a wishlist item as purchased (or reverts it to unpurchased).
        /// This is a convenience endpoint so clients do not need to send a full PUT
        /// payload just to toggle the purchased flag.
        /// </summary>
        /// <param name="id">The <see cref="Guid"/> identifier of the item.</param>
        /// <param name="isPurchased">
        /// <c>true</c> to mark the item as purchased; <c>false</c> to revert.
        /// </param>
        /// <returns>
        /// <list type="bullet">
        ///   <item><description>200 OK – the updated <see cref="WishlistItemDTO"/>.</description></item>
        ///   <item><description>401 Unauthorized – missing or invalid JWT token.</description></item>
        ///   <item><description>404 Not Found – item does not exist or belongs to another user.</description></item>
        /// </list>
        /// </returns>
        /// <response code="200">Purchased flag updated successfully.</response>
        /// <response code="401">Authentication token is missing or invalid.</response>
        /// <response code="404">Item not found for the authenticated user.</response>
        [HttpPatch("{id:guid}/purchased")]
        [ProducesResponseType(typeof(WishlistItemDTO), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status404NotFound)]
        public IActionResult MarkPurchased(Guid id, [FromQuery] bool isPurchased = true)
        {
            var userId = GetCurrentUserId();
            _logger.LogInformation(
                "PATCH /api/wishlist/{ItemId}/purchased?isPurchased={IsPurchased} by user {UserId}",
                id, isPurchased, userId);

            lock (_lock)
            {
                if (!_store.TryGetValue(userId!, out var userItems) ||
                    !userItems.TryGetValue(id, out var item))
                {
                    return NotFound(new ErrorResponse
                    {
                        Error = "ItemNotFound",
                        Message = $"Wishlist item '{id}' was not found.",
                        StatusCode = 404
                    });
                }

                item.IsPurchased = isPurchased;
                item.UpdatedAt   = DateTime.UtcNow;

                _logger.LogInformation(
                    "Wishlist item {ItemId} marked IsPurchased={IsPurchased} for user {UserId}",
                    id, isPurchased, userId);

                return Ok(item);
            }
        }
    }
}
