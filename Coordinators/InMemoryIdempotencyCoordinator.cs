using ApiGateway.Interfaces;
using System;
using System.Collections.Concurrent;
using System.Threading.Tasks;

namespace ApiGateway.Coordinators
{
    public class InMemoryIdempotencyCoordinator : IIdempotencyCoordinator
    {
        private class InflightOperation<T>
        {
            public TaskCompletionSource<T> TaskCompletionSource { get; } = new TaskCompletionSource<T>();
            public CancellationTokenSource CancellationTokenSource { get; } = new CancellationTokenSource();

            public InflightOperation() => CancellationTokenSource.Token.Register(() => TaskCompletionSource.TrySetCanceled());
        }

        private readonly ConcurrentDictionary<string, object> _inflightOperations = new ConcurrentDictionary<string, object>();

        public async Task<T> RunSingleFlightAsync<T>(string key, Func<Task<T>> operation, TimeSpan timeout)
        {
            var inflight = (InflightOperation<T>)_inflightOperations.GetOrAdd(key, _ => new InflightOperation<T>());

            try
            {
                if (inflight.TaskCompletionSource.Task.IsCompleted)
                {
                    _inflightOperations.TryRemove(key, out _);
                }
                else
                {
                    var result = await operation();
                    inflight.TaskCompletionSource.TrySetResult(result);
                    _inflightOperations.TryRemove(key, out _);
                    return result;
                }

                return await inflight.TaskCompletionSource.Task.WaitAsync(timeout);
            }
            catch (OperationCanceledException) when (inflight.CancellationTokenSource.IsCancellationRequested)
            {
                inflight.TaskCompletionSource.TrySetCanceled();
                throw;
            }
            catch (Exception ex)
            {
                inflight.TaskCompletionSource.TrySetException(ex);
                throw;
            }
            finally
            {
                inflight.CancellationTokenSource.CancelAfter(timeout);
            }
        }
    }
}
