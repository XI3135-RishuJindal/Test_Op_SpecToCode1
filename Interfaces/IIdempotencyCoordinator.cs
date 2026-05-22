using System;
using System.Threading.Tasks;

namespace ApiGateway.Interfaces
{
    public interface IIdempotencyCoordinator
    {
        Task<T> RunSingleFlightAsync<T>(string key, Func<Task<T>> operation, TimeSpan timeout);
    }
}
