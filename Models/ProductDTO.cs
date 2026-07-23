namespace ApiGateway.Models
{
    /// <summary>
    /// Represents product data transfer object for inventory and cart operations.
    /// </summary>
    public class ProductDTO
    {
        /// <summary>
        /// Gets or sets the unique product identifier.
        /// </summary>
        public int ProductId { get; set; }

        /// <summary>
        /// Gets or sets the display name of the product.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Gets or sets an optional product description.
        /// </summary>
        public string? Description { get; set; }

        /// <summary>
        /// Gets or sets the per-unit price.
        /// </summary>
        public decimal Price { get; set; }

        /// <summary>
        /// Gets or sets the unit of measurement (e.g., "pcs", "bottle").
        /// </summary>
        public string Unit { get; set; } = string.Empty;
    }
}