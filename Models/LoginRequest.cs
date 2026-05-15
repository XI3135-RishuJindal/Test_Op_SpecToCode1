namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a login request for token generation
    /// </summary>
    public class LoginRequest
    {
        public string Username { get; set; } = string.Empty;

        // Note: In a real application, do not log or echo passwords.
        public string Password { get; set; } = string.Empty;
    }
}