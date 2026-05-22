namespace ApiGateway.Models
{
    public class AccountDTO
    {
        public string Id { get; set; } = string.Empty;
        public string Sub { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string? Email { get; set; }
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    }
}
