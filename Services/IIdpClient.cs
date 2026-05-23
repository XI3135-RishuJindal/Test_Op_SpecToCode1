using System.Threading;
using System.Threading.Tasks;

namespace ApiGateway.Services
{
    /// <summary>
    /// Interface representing the IdP client abstraction.
    /// </summary>
    public interface IIdpClient
    {
        /// <summary>
        /// Token introspection operation.
        /// </summary>
        Task<IntrospectionResponse> IntrospectTokenAsync(string token, CancellationToken cancellationToken);
        
        /// <summary>
        /// Back-channel logout acknowledgement.
        /// </summary>
        Task AcknowledgeLogoutAsync(string sessionId, CancellationToken cancellationToken);

        /// <summary>
        /// Claims fetching operation.
        /// </summary>
        Task<ClaimsResponse> FetchClaimsAsync(string token, CancellationToken cancellationToken);
    }
}

// Placeholder classes for the response types
public class IntrospectionResponse { }
public class ClaimsResponse { }