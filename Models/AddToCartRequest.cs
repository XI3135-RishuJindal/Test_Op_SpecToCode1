using System.ComponentModel.DataAnnotations;

namespace ApiGateway.Models
{
    /// <summary>
    /// Request body for adding a product to a user's cart.
    /// </summary>
    public class AddToCartRequest
    {
        /// <summary>
        /// The unique identifier of the product to add.
        /// </summary>
        [Required]
        public int ProductId { get; set; }

        /// <summary>
        /// The quantity of the product to add.
        /// </summary>
        [Required]
        [Range(1, int.MaxValue, ErrorMessage = "Quantity must be at least 1.")]
        public int Quantity { get; set; }
    }
}