using System.Collections.Frozen;

namespace ApiGateway.Services
{
    /// <summary>
    /// Service responsible for checking passwords against a curated list of
    /// commonly-used (and therefore easily-guessable) passwords.
    /// Implements OWASP guidance: reject passwords that appear in known-bad lists.
    /// </summary>
    public interface ICommonPasswordService
    {
        /// <summary>Returns true when the supplied password is considered common / weak.</summary>
        bool IsCommonPassword(string password);
    }

    public sealed class CommonPasswordService : ICommonPasswordService
    {
        // A representative set of the most frequently breached passwords.
        // In a production system this list would be loaded from a file or a
        // dedicated service (e.g. HaveIBeenPwned k-anonymity API).
        private static readonly FrozenSet<string> _commonPasswords = new HashSet<string>(
            StringComparer.OrdinalIgnoreCase)
        {
            "password", "password1", "password123", "Password1", "Password123",
            "123456", "1234567", "12345678", "123456789", "1234567890",
            "qwerty", "qwerty123", "qwertyuiop",
            "abc123", "abcdef", "abcd1234",
            "letmein", "welcome", "welcome1",
            "monkey", "dragon", "master",
            "iloveyou", "sunshine", "princess",
            "admin", "admin123", "administrator",
            "login", "passw0rd", "p@ssword",
            "p@ssw0rd", "P@ssword1", "P@ssw0rd",
            "football", "baseball", "soccer",
            "shadow", "superman", "batman",
            "trustno1", "hello123", "charlie",
            "donald", "michael", "jessica",
            "111111", "222222", "123123",
            "654321", "000000", "696969",
            "zxcvbn", "zxcvbnm", "asdfgh",
            "test", "test123", "testing",
        }.ToFrozenSet(StringComparer.OrdinalIgnoreCase);

        /// <inheritdoc />
        public bool IsCommonPassword(string password)
        {
            if (string.IsNullOrEmpty(password))
                return false;

            return _commonPasswords.Contains(password);
        }
    }
}
