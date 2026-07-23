namespace ApiGateway.Models
{
    /// <summary>
    /// Represents medication data transfer object
    /// </summary>
    public class MedicationDTO
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal Dosage { get; set; }
        public string Unit { get; set; } = string.Empty;
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }

        // Added for medication entry form mapping
        public string Frequency { get; set; } = string.Empty;
        public string Route { get; set; } = string.Empty;
    }
}