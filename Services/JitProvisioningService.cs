using ApiGateway.Interfaces;
using ApiGateway.Models;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace ApiGateway.Services
{
    public class JitProvisioningService : IJitProvisioningService
    {
        private readonly IAccountRepository _accountRepository;
        private readonly IIdempotencyCoordinator _idempotencyCoordinator;
        private readonly ILogger<JitProvisioningService> _logger;
        private readonly TimeSpan _waitTimeout;

        public JitProvisioningService(
            IAccountRepository accountRepository,
            IIdempotencyCoordinator idempotencyCoordinator,
            IOptions<ProvisioningOptions> options,
            ILogger<JitProvisioningService> logger)
        {
            _accountRepository = accountRepository;
            _idempotencyCoordinator = idempotencyCoordinator;
            _logger = logger;
            _waitTimeout = TimeSpan.FromSeconds(options.Value.Idempotency.WaitTimeoutSeconds);
        }

        public async Task<ProvisioningResponse> ProvisionAsync(string sub, ProvisioningRequest request, CancellationToken cancellationToken)
        {
            var existingAccount = await _accountRepository.GetBySubAsync(sub);
            if (existingAccount != null)
            {
                _logger.LogInformation("Account retrieval successful for sub: {Sub}", sub);
                return new ProvisioningResponse { Account = existingAccount, Created = false };
            }

            return await _idempotencyCoordinator.RunSingleFlightAsync(sub, async () =>
            {
                existingAccount = await _accountRepository.GetBySubAsync(sub);  // Double-check

                if (existingAccount != null)
                {
                    _logger.LogInformation("Detected existing account for sub: {Sub}", sub);
                    return new ProvisioningResponse { Account = existingAccount, Created = false };
                }

                var account = new AccountDTO
                {
                    Id = Guid.NewGuid().ToString(),
                    Sub = sub,
                    Username = request.DisplayName ?? "User_" + sub.Substring(0, 6),
                    Email = request.Email,
                    CreatedAt = DateTime.UtcNow
                };

                var createdAccount = await _accountRepository.CreateAsync(account);
                _logger.LogInformation("Account creation successful for sub: {Sub}", sub);
                return new ProvisioningResponse { Account = createdAccount, Created = true };

            }, _waitTimeout);
        }
    }
}
