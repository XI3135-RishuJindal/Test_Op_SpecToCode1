```csharp
using Xunit;
using Moq;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using ApiGateway.Controllers;
using ApiGateway.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace ApiGateway.Tests.Controllers
{
    public class WishlistControllerTests
    {
        private readonly Mock<ILogger<WishlistController>> _loggerMock;
        private readonly WishlistController _wishlistController;

        public WishlistControllerTests()
        {
            _loggerMock = new Mock<ILogger<WishlistController>>();
            _wishlistController = new WishlistController(_loggerMock.Object);
        }

        [Fact]
        public async Task GetAllItems_ShouldReturnOkResultWithItems()
        {
            // Act
            var result = await _wishlistController.GetAllItems();

            // Assert
            var okResult = Assert.IsType<OkObjectResult>(result);
            var returnValue = Assert.IsType<List<WishlistItem>>(okResult.Value);
            Assert.NotEmpty(returnValue);
        }

        [Fact]
        public async Task AddItem_ShouldReturnCreatedResult_WithItem()
        {
            // Arrange
            var newItem = new WishlistItem { Id = 123, Name = "New Item", Description = "Test description" };

            // Act
            var result = await _wishlistController.AddItem(newItem);

            // Assert
            var createdResult = Assert.IsType<CreatedAtActionResult>(result);
            Assert.Equal("GetItem", createdResult.ActionName);
            var returnValue = Assert.IsType<WishlistItem>(createdResult.Value);
            Assert.Equal(newItem.Id, returnValue.Id);
        }

        [Fact]
        public async Task RemoveItem_ShouldReturnNoContent_WhenItemExists()
        {
            // Arrange
            var itemId = 123;

            // Act
            var result = await _wishlistController.RemoveItem(itemId);

            // Assert
            Assert.IsType<NoContentResult>(result);
        }

        [Fact]
        public async Task RemoveItem_ShouldReturnNotFound_WhenItemDoesNotExist()
        {
            // Arrange
            var itemId = 999;

            // Act
            var result = await _wishlistController.RemoveItem(itemId);

            // Assert
            Assert.IsType<NotFoundResult>(result);
        }

        [Fact]
        public async Task RearrangeItems_ShouldReturnOkResult_WhenRearrangementSuccessful()
        {
            // Arrange
            var newOrder = new List<int> { 2, 1, 3 };

            // Act
            var result = await _wishlistController.RearrangeItems(newOrder);

            // Assert
            Assert.IsType<OkResult>(result);
        }

        [Fact]
        public async Task RearrangeItems_ShouldReturnBadRequest_WhenOrderInvalid()
        {
            // Arrange
            var newOrder = new List<int> { 1, 2 }; // Incomplete order

            // Act
            var result = await _wishlistController.RearrangeItems(newOrder);

            // Assert
            Assert.IsType<BadRequestResult>(result);
        }
    }
}
```