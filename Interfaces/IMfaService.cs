```csharp
using System.Threading.Tasks;

namespace ApiGateway
{
    public interface IMfaService
    {
        Task<MfaResult> InitiateMfaSetupAsync(string username, string method);
    }

    public class MfaResult
    {
        public bool Success { get; set; }
        public string ErrorMessage { get; set; } = string.Empty;
    }
}
```