namespace ApiGateway.Models
{
    public class ProvisioningRequest
    {
        public string? DisplayName { get; set; }
        public string? Email { get; set; }
        public Dictionary<string, string>? Attributes { get; set; }
    }
}
