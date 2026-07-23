namespace ApiGateway.Services
{
    /// <summary>
    /// Interface for inventory checks.
    /// </summary>
    public interface IInventoryService
    {
        /// <summary>
        /// Checks if the specified product is in stock.
        /// </summary>
        /// <param name="productId">ID of the product.</param>
        /// <returns>True if in stock; otherwise, false.</returns>
        bool IsProductInStock(int productId);

        /// <summary>
        /// Gets the display name for the product.
        /// </summary>
        /// <param name="productId">ID of the product.</param>
        /// <returns>Display name.</returns>
        string GetProductName(int productId);
    }
}