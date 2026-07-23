namespace ApiGateway.Models
{
    /// <summary>
    /// Strongly-typed options class that binds to the "PasswordPolicy" section
    /// in appsettings.json.  Register via
    ///   builder.Services.Configure&lt;PasswordPolicyOptions&gt;(
    ///       builder.Configuration.GetSection("PasswordPolicy"));
    /// and inject IOptions&lt;PasswordPolicyOptions&gt; wherever the policy is enforced.
    /// </summary>
    public class PasswordPolicyOptions
    {
        /// <summary>Configuration section key used in appsettings.json.</summary>
        public const string SectionName = "PasswordPolicy";

        /// <summary>Minimum required password length (default: 12 per spec).</summary>
        public int MinimumLength { get; set; } = 12;

        /// <summary>Password must contain at least one uppercase letter.</summary>
        public bool RequireUppercase { get; set; } = true;

        /// <summary>Password must contain at least one lowercase letter.</summary>
        public bool RequireLowercase { get; set; } = true;

        /// <summary>Password must contain at least one numeric digit.</summary>
        public bool RequireDigit { get; set; } = true;

        /// <summary>Password must contain at least one special character.</summary>
        public bool RequireSpecialCharacter { get; set; } = true;

        /// <summary>
        /// Number of days before a password expires and the user is prompted
        /// to change it (default: 90 per spec).
        /// </summary>
        public int ExpirationDays { get; set; } = 90;

        /// <summary>
        /// List of commonly-used passwords that are rejected regardless of
        /// whether they meet the complexity requirements.
        /// Populated from appsettings.json "PasswordPolicy:CommonPasswords".
        /// </summary>
        public List<string> CommonPasswords { get; set; } = new();
    }
}
