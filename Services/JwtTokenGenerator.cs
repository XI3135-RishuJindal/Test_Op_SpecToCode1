using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using ApiGateway.Models;
using Microsoft.IdentityModel.Tokens;

namespace ApiGateway.Services
{
    /// <summary>
    /// Generates signed JWTs for SSO-authenticated users using the same JWT configuration
    /// (issuer, audience, signing key) already used by the existing JwtBearer middleware.
    /// </summary>
    public class JwtTokenGenerator : IJwtTokenGenerator
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<JwtTokenGenerator> _logger;

        // Token lifetime in hours – consistent with the existing AuthController behaviour.
        private const int TokenLifetimeHours = 1;

        public JwtTokenGenerator(IConfiguration configuration, ILogger<JwtTokenGenerator> logger)
        {
            _configuration = configuration;
            _logger = logger;
        }

        /// <inheritdoc/>
        public string GenerateToken(UserProfile user, ExternalIdentity externalIdentity, out DateTime expiresAt)
        {
            var key = Encoding.UTF8.GetBytes(
                _configuration["Jwt:Key"] ?? "default-secret-key-for-development");

            expiresAt = DateTime.UtcNow.AddHours(TokenLifetimeHours);

            var claims = new List<Claim>
            {
                new Claim(ClaimTypes.NameIdentifier, user.UserId),
                new Claim(ClaimTypes.Name, user.Name ?? user.Email ?? user.UserId),
                new Claim("provider", externalIdentity.Provider),
                new Claim("provider_user_id", externalIdentity.ProviderUserId),
            };

            if (!string.IsNullOrWhiteSpace(user.Email))
                claims.Add(new Claim(ClaimTypes.Email, user.Email));

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),
                Expires = expiresAt,
                Issuer = _configuration["Jwt:Issuer"],
                Audience = _configuration["Jwt:Audience"],
                SigningCredentials = new SigningCredentials(
                    new SymmetricSecurityKey(key),
                    SecurityAlgorithms.HmacSha256Signature)
            };

            var handler = new JwtSecurityTokenHandler();
            var token = handler.CreateToken(tokenDescriptor);
            var tokenString = handler.WriteToken(token);

            _logger.LogInformation(
                "JwtTokenGenerator: issued token for user {UserId} via provider {Provider}, expires {ExpiresAt:u}",
                user.UserId, externalIdentity.Provider, expiresAt);

            return tokenString;
        }
    }
}
