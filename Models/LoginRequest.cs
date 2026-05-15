namespace ApiGateway.Models
{
    /// <summary>
    /// Login request model used to request a JWT.
    /// </summary>
    public class LoginRequest
    {
        public string Username { get; set; } = string.Empty;

        // Never log or persist this value; used only for demo auth flow.
        public string Password { get; set; } = string.Empty;
    }
}