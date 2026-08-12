using ApiGateway.Models;
using System.Collections.Concurrent;

namespace ApiGateway.Services
{
    /// <summary>
    /// Thread-safe, in-memory implementation of <see cref="IWishlistService"/>.
    /// Suitable for development and testing; replace with a persistent store for production.
    /// </summary>
    public class InMemoryWishlistService : IWishlistService
    {
        // Keyed by userId → (itemId → WishlistItemDTO)
        private readonly ConcurrentDictionary<string, ConcurrentDictionary<int, WishlistItemDTO>> _store = new();
        private int _nextId = 1;

        /// <inheritdoc/>
        public IEnumerable<WishlistItemDTO> GetItems(string userId)
        {
            return _store.TryGetValue(userId, out var items)
                ? items.Values.ToList()
                : Enumerable.Empty<WishlistItemDTO>();
        }

        /// <inheritdoc/>
        public WishlistItemDTO? GetItem(string userId, int itemId)
        {
            if (_store.TryGetValue(userId, out var items) && items.TryGetValue(itemId, out var item))
                return item;
            return null;
        }

        /// <inheritdoc/>
        public WishlistItemDTO AddItem(string userId, WishlistItemDTO item)
        {
            var userItems = _store.GetOrAdd(userId, _ => new ConcurrentDictionary<int, WishlistItemDTO>());
            item.Id = Interlocked.Increment(ref _nextId);
            item.CreatedAt = DateTime.UtcNow;
            userItems[item.Id] = item;
            return item;
        }

        /// <inheritdoc/>
        public WishlistItemDTO? UpdateItem(string userId, int itemId, WishlistItemDTO updated)
        {
            if (!_store.TryGetValue(userId, out var items) || !items.ContainsKey(itemId))
                return null;

            updated.Id = itemId;
            updated.UpdatedAt = DateTime.UtcNow;
            items[itemId] = updated;
            return updated;
        }

        /// <inheritdoc/>
        public bool RemoveItem(string userId, int itemId)
        {
            if (_store.TryGetValue(userId, out var items))
                return items.TryRemove(itemId, out _);
            return false;
        }
    }
}
