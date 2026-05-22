using System.Security.Cryptography;
using System.Text;

namespace ApiGateway.Services.Audit
{
    public static class PiiRedactor
    {
        public static string Pseudonymize(string stableIdentifier, string salt)
        {
            using var sha256 = SHA256.Create();
            var compounded = salt + stableIdentifier;
            var hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(compounded));
            return Convert.ToBase64String(hash);
        }

        public static string MaskIp(string ip)
        {
            // Simple example: Mask last octet of IPv4
            if (ip.Contains('.'))
            {
                var parts = ip.Split('.');
                if(parts.Length == 4)
                {
                    parts[3] = "0";
                    return string.Join('.', parts);
                }
            }
            return ip; // Return as is for IPv6 or malformed
        }

        public static string Hash(string input)
        {
            using var sha256 = SHA256.Create();
            var hash = sha256.ComputeHash(Encoding.UTF8.GetBytes(input));
            return Convert.ToBase64String(hash);
        }
    }
}