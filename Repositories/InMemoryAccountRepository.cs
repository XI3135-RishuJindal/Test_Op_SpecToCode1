using ApiGateway.Interfaces;
using ApiGateway.Models;
using System.Collections.Concurrent;

namespace ApiGateway.Repositories
{
    public class InMemoryAccountRepository : IAccountRepository
    {
        private readonly ConcurrentDictionary<string, AccountDTO> _accounts = new ConcurrentDictionary<string, AccountDTO>();

        public Task<AccountDTO?> GetBySubAsync(string sub)
        {
            _accounts.TryGetValue(sub, out var account);
            return Task.FromResult(account);
        }

        public Task<AccountDTO> CreateAsync(AccountDTO account)
        {
            if (_accounts.TryAdd(account.Sub, account))
            {
                return Task.FromResult(account);
            }

            throw new InvalidOperationException("Account already exists.");
        }
    }
}
