using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using Microsoft.AspNetCore.Http;
using ApiGateway.Models;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/auth")]
    public class AuthController : ControllerBase
    {
        private readonly ILogger<AuthController> _logger;
        private readonly RedirectUriWhitelistOptions _options;

        public AuthController(ILogger<AuthController> logger, IOptions<RedirectUriWhitelistOptions> options)
        {
            _logger = logger;
            _options = options.Value;
        }

        [HttpGet("authorize")]
        public IActionResult Authorize([FromQuery] string redirect_uri, [FromQuery] string state, [FromQuery] string response_type)
        {
            if (!IsUriWhitelisted(redirect_uri))
            {
                EmitAuditLog("RedirectUriNotWhitelisted", redirect_uri);
                return CreateErrorResponse("RedirectUriNotWhitelisted", "redirect_uri is not whitelisted");
            }

            // Simulate success response
            return Ok(new { Message = "Authorization request simulated successfully.", RedirectUri = redirect_uri });
        }

        [HttpGet("callback")]
        public IActionResult Callback([FromQuery] string code, [FromQuery] string state, [FromQuery] string redirect_uri)
        {
            if (!IsHttpRequestSecure())
            {
                EmitAuditLog("InsecureCallbackRejected", Request.GetDisplayUrl());
                return CreateErrorResponse("InsecureCallbackRejected", "Insecure callback request.");
            }

            if (redirect_uri != null && !IsUriWhitelisted(redirect_uri))
            {
                EmitAuditLog("RedirectUriNotWhitelisted", redirect_uri);
                return CreateErrorResponse("RedirectUriNotWhitelisted", "redirect_uri is not whitelisted");
            }

            // Simulate success response
            return Ok(new { Message = "Callback simulated successfully.", Code = code, State = state });
        }

        private bool IsUriWhitelisted(string redirectUri)
        {
            if (Uri.TryCreate(redirectUri, UriKind.Absolute, out var uriObj))
            {
                return _options.RedirectUriWhitelist.Any(whitelisted => NormalizeUri(whitelisted) == NormalizeUri(uriObj));
            }
            return false;
        }

        private bool IsHttpRequestSecure()
        {
            return Request.IsHttps ||
                   (Request.Headers["X-Forwarded-Proto"].ToString().Equals("https", StringComparison.OrdinalIgnoreCase) && _options.TrustForwardedHeaders);
        }

        private void EmitAuditLog(string reasonCode, string uri)
        {
            _logger.LogWarning("Audit Log: {ReasonCode}, URI: {Uri}, IP: {IP}", reasonCode, uri, HttpContext.Connection.RemoteIpAddress);
        }

        private ObjectResult CreateErrorResponse(string errorCode, string message)
        {
            var errorResponse = new ErrorResponse
            {
                Error = errorCode,
                Message = message,
                StatusCode = StatusCodes.Status400BadRequest,
                Timestamp = DateTime.UtcNow
            };
            return BadRequest(errorResponse);
        }

        private string NormalizeUri(Uri uri)
        {
            return uri.GetComponents(UriComponents.Scheme | UriComponents.Host | UriComponents.Port | UriComponents.Path, UriFormat.Unescaped).ToLowerInvariant();
        }

        // Overload to handle string URI input normalization
        private string NormalizeUri(string uriString)
        {
            var uri = new Uri(uriString);
            return NormalizeUri(uri);
        }
    }

    public class RedirectUriWhitelistOptions
    {
        public List<string> RedirectUriWhitelist { get; set; }
        public bool TrustForwardedHeaders { get; set; }
    }
}
