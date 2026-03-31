namespace ApiGateway.Models
{
    /// <summary>
    /// Response model for the test endpoint
    /// </summary>
    public class TestResponse
    {
        public string Status { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public MedicationDTO? ProcessedMedication { get; set; }
        public DateTime ProcessedAt { get; set; } = DateTime.UtcNow;
        public string RequestId { get; set; } = string.Empty;
    }
}