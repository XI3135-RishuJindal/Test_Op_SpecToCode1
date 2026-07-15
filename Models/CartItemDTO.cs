using System.ComponentModel.DataAnnotations;

namespace ApiGateway.Models
{
    /// <summary>
    /// Represents an item in the user's shopping cart.
    /// </summary>
    public class CartItemDTO
    {
        /// <summary>
        /// The product identifier.
        /// </summary>
        [Required]
        public int ProductId { get; set; }

        /// <summary>
        /// Display name of the product.
        /// </summary>
        [Required]
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// The number of units of the product in the cart.
        /// </summary>
        [Required]
        public int Quantity { get; set; }

        /// <summary>
        /// Availability status of the item (e.g., "In Stock", "Out of Stock").
        /// </summary>
        public string Status { get; set; } = string.Empty;
    }
}