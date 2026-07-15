using System.Collections.Concurrent;

namespace ApiGateway.Services
{
    /// <summary>
    /// Simple in-memory implementation of the inventory service.
    /// </summary>
    public class InMemoryInventoryService : IInventoryService
    {
        private readonly ConcurrentDictionary<int, (string Name, int Stock)> _inventory = new();

        public InMemoryInventoryService()
        {
            // Initialize sample inventory.
            _inventory[1] = ("Wireless Mouse", 25);
            _inventory[2] = ("Mechanical Keyboard", 0);
            _inventory[3] = ("Monitor 24 Inch", 10);
            _inventory[4] = ("USB Cable", 100);
        }

        public bool IsProductInStock(int productId)
        {
            if (_inventory.TryGetValue(productId, out var item))
                return item.Stock > 0;
            return false;
        }

        public string GetProductName(int productId)
        {
            if (_inventory.TryGetValue(productId, out var item))
                return item.Name;
            return $"Product #{productId}";
        }
    }
}