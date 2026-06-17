using System.ComponentModel.DataAnnotations;

namespace ApiGateway.Models
{
    /// <summary>
    /// Represents a request to register an account using an email address.
    /// </summary>
    /// <remarks>
    /// The <c>Email</c> field must contain a syntactically valid email address compliant with RFC 5322. 
    /// This model is used by the <c>POST /api/auth/register</c> endpoint to initiate the email verification workflow.
    /// </remarks>
    public class RegisterEmailRequest
    {
        /// <summary>
        /// The email address to register.
        /// </summary>
        /// <example>user@example.com</example>
        [Required]
        public string Email { get; set; } = string.Empty;
    }
}