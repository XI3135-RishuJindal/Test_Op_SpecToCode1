using ApiGateway.Models;
using System.Threading;
using System.Threading.Tasks;

namespace ApiGateway.Interfaces
{
    public interface IJitProvisioningService
    {
        Task<ProvisioningResponse> ProvisionAsync(string sub, ProvisioningRequest request, CancellationToken cancellationToken);
    }
}
