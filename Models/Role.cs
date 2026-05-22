namespace ApiGateway.Models
{
    public class Role
    {
        public string Name { get; set; } = string.Empty;
        public string[] Permissions { get; set; } = Array.Empty<string>();
    }
}