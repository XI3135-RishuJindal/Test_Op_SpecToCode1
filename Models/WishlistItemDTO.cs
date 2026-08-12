namespace ApiGateway.Models
{
    /// <summary>
    /// Data Transfer Object representing a single item in a user's wishlist.
    /// Used for all CRUD operations exposed by <see cref="ApiGateway.Controllers.WishlistController"/>.
    /// </summary>
    /// <remarks>
    /// Design decisions:
    /// - <c>Id</c> is a <see cref="Guid"/> to avoid sequential-ID enumeration attacks.
    /// - <c>UserId</c> is stored on the DTO so the controller can enforce ownership checks
    ///   without an additional round-trip to a user-resolution service.
    /// - <c>Tags</c> is an optional free-form list that supports future filtering/search
    ///   without requiring a schema migration.
    /// - All timestamps are UTC to avoid timezone ambiguity across distributed deployments.
    /// </remarks>
    public class WishlistItemDTO
    {
        /// <summary>
        /// Unique identifier for the wishlist item.
        /// Generated server-side on creation; clients must not supply this value on POST.
        /// </summary>
        public Guid Id { get; set; } = Guid.NewGuid();

        /// <summary>
        /// Identifier of the authenticated user who owns this wishlist item.
        /// Populated from the JWT <c>NameIdentifier</c> claim on creation.
        /// </summary>
        public string UserId { get; set; } = string.Empty;

        /// <summary>
        /// Human-readable name of the wishlist item (required, max 200 characters).
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Optional detailed description of the wishlist item (max 1 000 characters).
        /// </summary>
        public string Description { get; set; } = string.Empty;

        /// <summary>
        /// Optional URL pointing to the item's product page or image.
        /// </summary>
        public string? Url { get; set; }

        /// <summary>
        /// Optional price or estimated cost of the item.
        /// </summary>
        public decimal? Price { get; set; }

        /// <summary>
        /// Optional currency code (ISO 4217) for <see cref="Price"/>, e.g. "USD", "EUR".
        /// </summary>
        public string? Currency { get; set; }

        /// <summary>
        /// Arbitrary tags that allow the user to categorise or filter wishlist items.
        /// </summary>
        public List<string> Tags { get; set; } = new();

        /// <summary>
        /// Priority level assigned by the user (1 = highest, 5 = lowest).
        /// Defaults to 3 (medium priority).
        /// </summary>
        public int Priority { get; set; } = 3;

        /// <summary>
        /// Indicates whether the item has been purchased / fulfilled.
        /// </summary>
        public bool IsPurchased { get; set; } = false;

        /// <summary>
        /// UTC timestamp when the item was added to the wishlist.
        /// Set server-side; clients must not supply this value.
        /// </summary>
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

        /// <summary>
        /// UTC timestamp of the most recent update to the item.
        /// Null until the item is modified for the first time.
        /// </summary>
        public DateTime? UpdatedAt { get; set; }
    }
}
