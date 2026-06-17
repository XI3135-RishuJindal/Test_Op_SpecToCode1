using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;

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
            _logger.LogInformation("Processing POST request to /api/test with RequestId: {RequestId}", requestId);

            try
            {
                // Simulate async pipeline step for consistency
                await Task.Yield();

                // Validate request
                if (request == null)
                {
                    _logger.LogWarning("Received null request for RequestId: {RequestId}", requestId);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidRequest",
                        Message = "Request body cannot be null",
                        StatusCode = StatusCodes.Status400BadRequest
                    });
                }

                if (string.IsNullOrWhiteSpace(request.Message))
                {
                    _logger.LogWarning("Received request with empty message for RequestId: {RequestId}", requestId);
                    return BadRequest(new ErrorResponse
                    {
                        Error = "InvalidMessage",
                        Message = "Message cannot be null or empty",
                        StatusCode = StatusCodes.Status400BadRequest
                    });
                }

                // Log request details
                _logger.LogInformation("Processing request with message: {Message}, RequestId: {RequestId}", request.Message, requestId);

                // Process medication if provided
                MedicationDTO? processedMedication = null;
                if (request.Medication != null)
                {
                    _logger.LogInformation("Processing medication data for RequestId: {RequestId}", requestId);

                    processedMedication = new MedicationDTO
                    {
                        Id = request.Medication.Id,
                        Name = request.Medication.Name?.Trim() ?? string.Empty,
                        Description = request.Medication.Description?.Trim() ?? string.Empty,
                        Dosage = request.Medication.Dosage,
                        Unit = request.Medication.Unit?.Trim() ?? string.Empty,
                        CreatedAt = request.Medication.CreatedAt == default ? DateTime.UtcNow : request.Medication.CreatedAt,
                        UpdatedAt = DateTime.UtcNow
                    };
                }

                var response = new TestResponse
                {
                    Status = "Success",
                    Message = $"Processed: {request.Message.Trim()}",
                    ProcessedMedication = processedMedication,
                    ProcessedAt = DateTime.UtcNow,
                    RequestId = requestId
                };

                _logger.LogInformation("Successfully processed RequestId: {RequestId}", requestId);
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error processing RequestId: {RequestId}", requestId);
                return StatusCode(StatusCodes.Status500InternalServerError, new ErrorResponse
                {
                    Error = "InternalServerError",
                    Message = "An unexpected error occurred while processing the request.",
                    StatusCode = StatusCodes.Status500InternalServerError,
                    Details = ex.Message
                });
            }
        }
    }
}