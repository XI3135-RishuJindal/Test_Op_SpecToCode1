using ApiGateway.Models;
using ApiGateway.Services;
using System.Collections.Concurrent;

namespace ApiGateway.Utility
{
    /// <summary>
    /// Thread-safe, per-user in-memory cart storage.
    /// </summary>
    public class CartStore
    {
        private readonly IInventoryService _inventoryService;
        private readonly ConcurrentDictionary<string, ConcurrentDictionary<int, InternalCartItem>> _userCarts;

        public CartStore(IInventoryService inventoryService)
        {
            _inventoryService = inventoryService;
            _userCarts = new ConcurrentDictionary<string, ConcurrentDictionary<int, InternalCartItem>>();
        }

        /// <summary>
        /// Gets the cart for a user, projecting to CartDTO with inventory-synced state.
        /// </summary>
        public CartDTO GetCart(string userId)
        {
            var result = new CartDTO();

            if (_userCarts.TryGetValue(userId, out var cartItems))
            {
                foreach (var item in cartItems.Values)
                {
                    var name = _inventoryService.GetProductName(item.ProductId) ?? string.Empty;
                    var inventoryQty = _inventoryService.GetAvailableQuantity(item.ProductId);

                    string status;
                    if (name == string.Empty)
                        status = "not_found";
                    else if (inventoryQty <= 0)
                        status = "out_of_stock";
                    else if (inventoryQty < item.Quantity)
                        status = "out_of_stock";
                    else
                        status = "available";

                    result.Items.Add(new CartItemDTO
                    {
                        ProductId = item.ProductId,
                        Name = name,
                        Quantity = item.Quantity,
                        Status = status
                    });
                }
            }

            return result;
        }

        /// <summary>
        /// Adds or updates a product in user's cart. Returns true if added, false if failed (out of stock or invalid).
        /// Enforces inventory check at time of add.
        /// </summary>
        public bool AddOrUpdateItem(string userId, int productId, int quantity)
        {
            var prodName = _inventoryService.GetProductName(productId);
            if (string.IsNullOrWhiteSpace(prodName))
                return false; // invalid product

            var available = _inventoryService.GetAvailableQuantity(productId);
            if (quantity < 1 || available < quantity)
                return false; // not enough stock

            var cart = _userCarts.GetOrAdd(userId, _ => new ConcurrentDictionary<int, InternalCartItem>());

            cart.AddOrUpdate(productId,
                k => new InternalCartItem { ProductId = productId, Quantity = quantity },
                (k, existing) =>
                {
                    existing.Quantity = quantity; // update to new quantity. Could choose to +=, here overwrite per spec.
                    return existing;
                });

            return true;
        }

        /// <summary>
        /// Removes a product from the user's cart.
        /// </summary>
        public void RemoveItem(string userId, int productId)
        {
            if (_userCarts.TryGetValue(userId, out var cart))
            {
                cart.TryRemove(productId, out _);
            }
        }

        /// <summary>
        /// Clears all items from the user's cart.
        /// </summary>
        public void ClearCart(string userId)
        {
            _userCarts.TryRemove(userId, out _);
        }
    }
}