```csharp
using ApiGateway.Models;
using System.Threading.Tasks;

namespace ApiGateway.Services
{
    public interface IUserService
    {
        Task<User?> GetUserByEmailAsync(string email);
    }
}
```