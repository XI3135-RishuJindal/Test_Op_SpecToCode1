namespace ApiGateway.Models
{
    /// <summary>
    /// Internal representation of a cart item, used by CartStore.
    /// </summary>
    internal class InternalCartItem
    {
        public int ProductId { get; set; }
        public int Quantity { get; set; }
    }
}