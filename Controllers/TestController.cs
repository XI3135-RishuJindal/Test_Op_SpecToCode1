using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Models;
using System.ComponentModel.DataAnnotations;

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

                // Log request details
                _logger.LogInformation("Processing request with message: {Message}, RequestId: {RequestId}", 
                    request.Message, requestId);

                // Process medication if provided
                MedicationDTO? processedMedication = null;
                if (request.Medication != null)
                {
                    _logger.LogInformation("Processing medication data for RequestId: {RequestId}", requestId);
                    
                    // Simulate processing - in a real scenario, this would route to backend services
                    processedMedication = new MedicationDTO
                    {
                        Id = request.Medication.Id,
                        Name = request.Medication.Name,
                        Description = request.Medication.Description,
                        Dosage = request.Medication.Dosage,
                        Unit = request.Medication.Unit,
                        CreatedAt = request.Medication.CreatedAt,
                        UpdatedAt = DateTime.UtcNow
                    };
                }

                // Create response
                var response = new TestResponse
                {
                    Status = "Success",
                    Message = $"Request processed successfully: {request.Message}",
                    ProcessedMedication = processedMedication,
                    ProcessedAt = DateTime.UtcNow,
                    RequestId = requestId
                };

                _logger.LogInformation("Successfully processed request with RequestId: {RequestId}", requestId);

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing request with RequestId: {RequestId}", requestId);
                
                return StatusCode(500, new ErrorResponse
                {
                    Error = "InternalServerError",
                    Message = "An error occurred while processing the request",
                    StatusCode = 500,
                    Details = ex.Message
                });
            }
        }
    }
}