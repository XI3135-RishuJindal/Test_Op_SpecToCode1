using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;
using ApiGateway.Utilities;

namespace ApiGateway.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class TestController : ControllerBase
    {
        private readonly ILogger<TestController> _logger;

        public TestController(ILogger<TestController> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Test endpoint for layered architecture flow
        /// </summary>
        /// <param name="request">Test request containing message and optional medication data</param>
        /// <returns>Test response with processed data</returns>
        [HttpPost]
        [ProducesResponseType(typeof(TestResponse), StatusCodes.Status200OK)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status400BadRequest)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status401Unauthorized)]
        [ProducesResponseType(typeof(ErrorResponse), StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> Post([FromBody] TestRequest request)
        {
            var requestId = Guid.NewGuid().ToString();

            // Log only metadata, never raw user-provided message
            _logger.LogInformation("Processing POST /api/test with RequestId: {RequestId}", requestId);

            try
            {
                // Validate request
                if (request == null)
                {
                    _logger.LogWarning("Received null request for RequestId: {RequestId}", requestId);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidRequest",
                        Message = "Request body cannot be null",
                        StatusCode = 400
                    });
                }

                if (string.IsNullOrWhiteSpace(request.Message))
                {
                    _logger.LogWarning("Received request with empty message for RequestId: {RequestId}", requestId);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidMessage",
                        Message = "Message cannot be null or empty",
                        StatusCode = 400
                    });
                }

                // Safely log a scrubbed version only
                var safeMessage = SensitiveDataMasker.ScrubPotentialPan(request.Message);
                _logger.LogInformation("Validated request for RequestId: {RequestId}. SafeMessagePreview: {Message}", requestId, SensitiveDataMasker.Preview(safeMessage));

                // Simulate async processing
                await Task.Yield();

                // Process medication if provided
                MedicationDTO? processedMedication = null;
                if (request.Medication != null)
                {
                    // Do not log field values; just note presence
                    _logger.LogInformation("Medication payload present for RequestId: {RequestId}", requestId);

                    processedMedication = new MedicationDTO
                    {
                        Id = request.Medication.Id,
                        Name = $"{request.Medication.Name} (Processed)",
                        Description = request.Medication.Description,
                        Dosage = request.Medication.Dosage,
                        Unit = request.Medication.Unit,
                        CreatedAt = request.Medication.CreatedAt,
                        UpdatedAt = DateTime.UtcNow
                    };
                }

                var response = new TestResponse
                {
                    Status = "Success",
                    Message = safeMessage,
                    ProcessedMedication = processedMedication,
                    ProcessedAt = DateTime.UtcNow,
                    RequestId = requestId
                };

                _logger.LogInformation("Successfully processed RequestId: {RequestId}", requestId);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unhandled exception while processing RequestId: {RequestId}", requestId);
                return StatusCode(StatusCodes.Status500InternalServerError, new ErrorResponse
                {
                    Error = "InternalServerError",
                    Message = "An unexpected error occurred while processing the request",
                    StatusCode = 500
                });
            }
        }
    }
}