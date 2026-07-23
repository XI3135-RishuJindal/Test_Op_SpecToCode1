using System.Collections.Concurrent;

namespace ApiGateway.Services
{
    /// <summary>
    /// Thread-safe in-memory store for shopping carts, keyed by user id.
    /// </summary>
    public class CartStore
    {
        /// <summary>
        /// Represents items in a cart: productId -> quantity.
        /// </summary>
        private ConcurrentDictionary<string, ConcurrentDictionary<int, int>> _cartData =
            new ConcurrentDictionary<string, ConcurrentDictionary<int, int>>();

        /// <summary>
        /// Gets the cart dictionary for a user. Initializes if it does not exist.
        /// </summary>
        /// <param name="userId">User identity string (should be unique per user, e.g., subject from JWT).</param>
        /// <returns>The user's cart (mutable dictionary of productId to quantity).</returns>
        public ConcurrentDictionary<int, int> GetOrCreateUserCart(string userId)
        {
            return _cartData.GetOrAdd(userId, _ => new ConcurrentDictionary<int, int>());
        }

        /// <summary>
        /// Clears the cart for a given user.
        /// </summary>
        public void ClearCart(string userId)
        {
            _cartData.TryRemove(userId, out _);
        }

        /// <summary>
        /// Removes a product from a user's cart.
        /// </summary>
        public void RemoveProduct(string userId, int productId)
        {
            if (_cartData.TryGetValue(userId, out var items))
            {
                items.TryRemove(productId, out _);
            }
        }

        /// <summary>
        /// Gets a snapshot of all user carts (for diagnostics or admin).
        /// </summary>
        public IDictionary<string, IDictionary<int, int>> GetAllCartsSnapshot()
        {
            return _cartData.ToDictionary(
                kvp => kvp.Key,
                kvp => (IDictionary<int, int>)kvp.Value.ToDictionary(x => x.Key, x => x.Value)
            );
        }
    }
}