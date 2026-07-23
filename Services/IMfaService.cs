```csharp
using System.Threading.Tasks;

namespace ApiGateway.Services
{
    public interface IMfaService
    {
        Task<MfaVerificationResult> VerifyCodeAsync(string userId, string code);
    }
}
```