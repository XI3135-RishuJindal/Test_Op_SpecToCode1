```csharp
namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for verifying MFA code
    /// </summary>
    public class MfaCodeRequest
    {
        public string UserId { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
    }
}
```