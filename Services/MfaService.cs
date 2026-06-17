using System.Security.Cryptography;
using System.Text;

namespace ApiGateway.Services
{
    /// <summary>
    /// TOTP-based MFA service.
    ///
    /// Implements RFC 6238 (TOTP) on top of RFC 4226 (HOTP) using HMAC-SHA1,
    /// a 30-second time step, and 6-digit codes — the same parameters used by
    /// Google Authenticator, Authy, and most other authenticator apps.
    ///
    /// NOTE: Secrets are stored in-memory for demonstration purposes.
    ///       In production, persist them encrypted in a database or secrets vault.
    /// </summary>
    public class MfaService : IMfaService
    {
        // In-memory store: username → Base32 shared secret
        // Replace with a persistent, encrypted store in production.
        private readonly Dictionary<string, string> _secretStore = new(StringComparer.OrdinalIgnoreCase);

        private const int TimeStepSeconds = 30;
        private const int CodeDigits = 6;
        // Allow ±1 time step to tolerate minor clock skew between client and server
        private const int AllowedWindowSteps = 1;

        /// <inheritdoc />
        public (string SharedSecret, string QrCodeUri) GenerateSecret(string username, string issuer)
        {
            // Generate 20 random bytes (160 bits) — the recommended TOTP secret length
            var secretBytes = RandomNumberGenerator.GetBytes(20);
            var base32Secret = Base32Encode(secretBytes);

            // Build the standard otpauth URI understood by all authenticator apps
            var encodedIssuer = Uri.EscapeDataString(issuer);
            var encodedUser = Uri.EscapeDataString(username);
            var qrCodeUri =
                $"otpauth://totp/{encodedIssuer}:{encodedUser}" +
                $"?secret={base32Secret}&issuer={encodedIssuer}&algorithm=SHA1&digits={CodeDigits}&period={TimeStepSeconds}";

            return (base32Secret, qrCodeUri);
        }

        /// <inheritdoc />
        public void StoreSecret(string username, string secret)
        {
            _secretStore[username] = secret;
        }

        /// <inheritdoc />
        public bool ValidateCode(string username, string code)
        {
            if (!_secretStore.TryGetValue(username, out var base32Secret))
                return false;

            if (string.IsNullOrWhiteSpace(code) || code.Length != CodeDigits)
                return false;

            if (!long.TryParse(code, out _))
                return false;

            var secretBytes = Base32Decode(base32Secret);
            var currentStep = DateTimeOffset.UtcNow.ToUnixTimeSeconds() / TimeStepSeconds;

            // Check current step and ±AllowedWindowSteps to handle clock skew
            for (var delta = -AllowedWindowSteps; delta <= AllowedWindowSteps; delta++)
            {
                var expected = ComputeTotp(secretBytes, currentStep + delta);
                if (expected == code)
                    return true;
            }

            return false;
        }

        // -----------------------------------------------------------------------
        // TOTP / HOTP helpers
        // -----------------------------------------------------------------------

        private static string ComputeTotp(byte[] secret, long timeStep)
        {
            // Convert time step to big-endian 8-byte array (RFC 4226 §5.2)
            var stepBytes = BitConverter.GetBytes(timeStep);
            if (BitConverter.IsLittleEndian)
                Array.Reverse(stepBytes);

            using var hmac = new HMACSHA1(secret);
            var hash = hmac.ComputeHash(stepBytes);

            // Dynamic truncation (RFC 4226 §5.3)
            var offset = hash[^1] & 0x0F;
            var truncated =
                ((hash[offset] & 0x7F) << 24) |
                ((hash[offset + 1] & 0xFF) << 16) |
                ((hash[offset + 2] & 0xFF) << 8) |
                (hash[offset + 3] & 0xFF);

            var otp = truncated % (int)Math.Pow(10, CodeDigits);
            return otp.ToString().PadLeft(CodeDigits, '0');
        }

        // -----------------------------------------------------------------------
        // Base32 helpers (RFC 4648, no padding required by authenticator apps)
        // -----------------------------------------------------------------------

        private static readonly char[] Base32Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567".ToCharArray();

        private static string Base32Encode(byte[] data)
        {
            var sb = new StringBuilder((data.Length * 8 + 4) / 5);
            int buffer = 0, bitsLeft = 0;

            foreach (var b in data)
            {
                buffer = (buffer << 8) | b;
                bitsLeft += 8;
                while (bitsLeft >= 5)
                {
                    bitsLeft -= 5;
                    sb.Append(Base32Alphabet[(buffer >> bitsLeft) & 0x1F]);
                }
            }

            if (bitsLeft > 0)
                sb.Append(Base32Alphabet[(buffer << (5 - bitsLeft)) & 0x1F]);

            return sb.ToString();
        }

        private static byte[] Base32Decode(string base32)
        {
            base32 = base32.TrimEnd('=').ToUpperInvariant();
            var output = new byte[base32.Length * 5 / 8];
            int buffer = 0, bitsLeft = 0, index = 0;

            foreach (var c in base32)
            {
                var value = Array.IndexOf(Base32Alphabet, c);
                if (value < 0) continue; // skip unknown chars

                buffer = (buffer << 5) | value;
                bitsLeft += 5;
                if (bitsLeft >= 8)
                {
                    bitsLeft -= 8;
                    output[index++] = (byte)((buffer >> bitsLeft) & 0xFF);
                }
            }

            return output[..index];
        }
    }
}
