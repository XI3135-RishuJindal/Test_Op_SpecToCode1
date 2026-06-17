```csharp
using System;
using OtpNet;

namespace ApiGateway.Services
{
    public interface IAuthenticatorAppService
    {
        string GenerateSetupCode(string accountName, string issuer);
        bool ValidateToken(string secret, string token);
    }

    public class AuthenticatorAppService : IAuthenticatorAppService
    {
        public string GenerateSetupCode(string accountName, string issuer)
        {
            var secret = KeyGeneration.GenerateRandomKey(20);
            var otpUrl = new OtpDisplayUrl(secret).GetUrlQrCode(accountName, issuer);
            return otpUrl;
        }

        public bool ValidateToken(string secret, string token)
        {
            var otp = new Totp(Base32Encoding.ToBytes(secret));
            return otp.VerifyTotp(token, out long _, VerificationWindow.RfcSpecifiedNetworkDelay);
        }
    }
}
```