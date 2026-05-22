namespace ApiGateway.Models
{
    public class ProvisioningResponse
    {
        public AccountDTO Account { get; set; } = new AccountDTO();
        public bool Created { get; set; } = false;
    }
}
