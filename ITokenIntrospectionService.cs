using System.Threading.Tasks;

namespace ApiGateway.Services
{
    public interface ITokenIntrospectionService
    {
        Task<IntrospectionResponse> IntrospectTokenAsync(string token);
    }

    public class IntrospectionResponse
    {
        public bool Active { get; set; }
        // Other fields can be added as per RFC 7662 spec
    }
}