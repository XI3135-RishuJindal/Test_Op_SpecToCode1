using ApiGateway.Interfaces;
using ApiGateway.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Linq;
using System.Threading.Tasks;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/provisioning")]
    public class ProvisioningController : ControllerBase
    {
        private readonly IJitProvisioningService _jitProvisioningService;

        public ProvisioningController(IJitProvisioningService jitProvisioningService)
        {
            _jitProvisioningService = jitProvisioningService;
        }

        [HttpPost("jit")]
        [Authorize]
        public async Task<IActionResult> JitProvisioning(ProvisioningRequest request)
        {
            var sub = User.Claims.FirstOrDefault(c => c.Type == JwtRegisteredClaimNames.Sub)?.Value;
            if (string.IsNullOrWhiteSpace(sub))
                return BadRequest(new ErrorResponse { Error = "MissingSubClaim", Message = "JWT must include sub claim", StatusCode = StatusCodes.Status400BadRequest });

            var (account, created) = await _jitProvisioningService.ProvisionAsync(sub, request, HttpContext.RequestAborted);
            if (created)
                return CreatedAtAction(nameof(GetAccountBySub), new { sub = account.Sub }, new ProvisioningResponse { Account = account, Created = true });

            return Ok(new ProvisioningResponse { Account = account, Created = false });
        }

        [HttpGet("accounts/{sub}")]
        [Authorize]
        public async Task<IActionResult> GetAccountBySub(string sub)
        {
            var account = await _jitProvisioningService.GetAccountBySubAsync(sub);
            if (account == null)
                return NotFound(new ErrorResponse { Error = "AccountNotFound", Message = "No account found for the specified sub", StatusCode = StatusCodes.Status404NotFound });

            return Ok(account);
        }
    }
}
