namespace ApiGateway.Options
{
    public class AuthorizationOptions
    {
        public string DefaultRole { get; set; } = "viewer";
        public string UnknownRoleBehavior { get; set; } = "apply-default"; // Options: "apply-default", "deny"
        public Dictionary<string, string[]> RoleMappings { get; set; } = new();
        public Dictionary<string, string[]> Roles { get; set; } = new();
    }
}