namespace ApiGateway.Models
{
    /// <summary>
    /// Request model for the test endpoint
    /// </summary>
    public class TestRequest
    {
        public string Message { get; set; } = string.Empty;
        public MedicationDTO? Medication { get; set; }
        public Dictionary<string, object>? AdditionalData { get; set; }
    }
}