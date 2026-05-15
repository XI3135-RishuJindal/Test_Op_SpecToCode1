using System.Text.RegularExpressions;

namespace ApiGateway.Utilities
{
    /// <summary>
    /// Utility to scrub or minimize risk of logging sensitive data (e.g., PAN).
    /// Implements conservative Luhn-based masking for 13-19 digit sequences with optional separators.
    /// </summary>
    public static class SensitiveDataMasker
    {
        // Matches sequences of 13-19 digits, allowing spaces or dashes as separators.
        private static readonly Regex CandidateDigits = new Regex(@"(?<!\d)(?:\d[ -]?){13,19}(?!\d)", RegexOptions.Compiled);

        /// <summary>
        /// Scrubs PAN-like patterns from the input string using a Luhn check prior to redaction.
        /// </summary>
        public static string ScrubPotentialPan(string input)
        {
            if (string.IsNullOrEmpty(input))
            {
                return string.Empty;
            }

            return CandidateDigits.Replace(input, m =>
            {
                var digits = new string(m.Value.Where(char.IsDigit).ToArray());
                if (digits.Length >= 13 && digits.Length <= 19 && PassesLuhn(digits))
                {
                    return "[REDACTED PAN]";
                }
                return m.Value;
            });
        }

        /// <summary>
        /// Returns a safe string for logging where general user-provided input is scrubbed for PAN-like content.
        /// </summary>