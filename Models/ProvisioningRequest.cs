using System.ComponentModel.DataAnnotations;

namespace ApiGateway.Models
{
    public class ProvisioningRequest
    {
        [Required]
        public string ExternalUserId { get; set; } = string.Empty;

        [Required]
        [EmailAddress]
        public string Email { get; set; } = string.Empty;

        [Required]
        public string PlanCode { get; set; } =