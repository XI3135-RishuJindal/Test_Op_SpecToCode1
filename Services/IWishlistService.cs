using ApiGateway.Models;

namespace ApiGateway.Services
{
    /// <summary>
    /// Defines the contract for wishlist management operations.
    /// </summary>
    public interface IWishlistService
    {
        /// <summary>Returns all wishlist items for the specified user.</summary>
        IEnumerable<WishlistItemDTO> GetItems(string userId);

        /// <summary>Returns a single wishlist item by its ID for the specified user, or null if not found.</summary>
        WishlistItemDTO? GetItem(string userId, int itemId);

        /// <summary>Adds a new item to the user's wishlist and returns the created item.</summary>
        WishlistItemDTO AddItem(string userId, WishlistItemDTO item);

        /// <summary>Updates an existing wishlist item. Returns the updated item, or null if not found.</summary>
        WishlistItemDTO? UpdateItem(string userId, int itemId, WishlistItemDTO item);

        /// <summary>Removes a wishlist item. Returns true if removed, false if not found.</summary>
        bool RemoveItem(string userId, int itemId);
    }
}
