```csharp
namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for SSO linking
    /// </summary>
    public class SsoRequest
    {
        public string Email { get; set; } = string.Empty;
    }
}
```