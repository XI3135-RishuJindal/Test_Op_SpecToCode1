namespace ApiGateway.Models.Audit
{
    /// <summary>
    /// Represents the result of an audit emission.
    /// </summary>
    public class EmissionResult
    {
        public bool IsSuccessful { get; set; }
        public int? HttpStatusCode { get; set; }
        public string? ErrorMessage { get; set; }
    }
}