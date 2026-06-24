```csharp
namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a login request
    /// </summary>
    public class LoginRequest
    {
        public string Username { get; set; } = string.Empty;
        public string Password { get; set; } = string.Empty;
    }
}
```