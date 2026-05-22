using ApiGateway.Models;
using System.Threading.Tasks;

namespace ApiGateway.Interfaces
{
    public interface IAccountRepository
    {
        Task<AccountDTO?> GetBySubAsync(string sub);
        Task<AccountDTO> CreateAsync(AccountDTO account);
    }
}
