using System.Collections.Generic;

namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a user's shopping cart.
    /// </summary>
    public class CartDTO
    {
        /// <summary>
        /// The items currently in the user's cart.
        /// </summary>
        public List<CartItemDTO> Items { get; set; } = new();

        /// <summary>
        /// The total count of distinct products in the cart.
        /// </summary>
        public int TotalItems => Items?.Count ?? 0;

        /// <summary>
        /// The total quantity of all products in the cart.
        /// </summary>
        public int TotalQuantity => Items?.Sum(x => x.Quantity) ?? 0;
    }
}