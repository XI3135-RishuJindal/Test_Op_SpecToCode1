```csharp
namespace ApiGateway.Models
{
    /// <summary>
    /// SSO Request model containing details for IdP interaction
    /// </summary>
    public class SSORequest
    {
        public string Provider { get; set; } = string.Empty;
        public string RedirectUri { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
    }
}
```