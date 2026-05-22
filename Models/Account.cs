namespace ApiGateway.Models
{
    public class Account
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string SubjectId { get; set; } = string.Empty;
        public string Username { get; set; } = string.Empty;
        public string[] Roles { get; set; } = Array.Empty<string>();
        public string[] Permissions { get; set; } = Array.Empty<string>();
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
    }
}