using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using Moq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using ApiGateway.Controllers;
using ApiGateway.Models;
using Xunit;

namespace ApiGateway.Tests.Controllers
{
    /// <summary>
    /// Unit tests for <see cref="WishlistController"/>.
    ///
    /// Test strategy:
    ///   - Each test is fully isolated: a fresh controller instance is created per test
    ///     so the static in-memory store is reset via a unique userId per test run.
    ///   - A deterministic userId is injected through a mocked <see cref="ClaimsPrincipal"/>
    ///     so tests do not depend on JWT infrastructure.
    ///   - Tests cover the happy path and the most important error paths for every endpoint.
    ///
    /// Acceptance criteria covered:
    ///   AC1 – Users can view their current wishlist items (GetAll, GetById).
    ///   AC2 – Users can add new items (Create).
    ///   AC3 – Users can remove existing items (Delete).
    ///   AC4 – Users can modify details of wishlist items (Update, MarkPurchased).
    /// </summary>
    public class WishlistControllerTests
    {
        // -----------------------------------------------------------------------
        // Helpers
        // -----------------------------------------------------------------------

        /// <summary>
        /// Creates a <see cref="WishlistController"/> whose <c>User</c> property is
        /// populated with a <see cref="ClaimsPrincipal"/> carrying the supplied userId.
        /// </summary>
        private static WishlistController CreateController(string userId)
        {
            var logger = new Mock<ILogger<WishlistController>>();
            var controller = new WishlistController(logger.Object);

            var claims = new[]
            {
                new Claim(ClaimTypes.NameIdentifier, userId),
                new Claim(ClaimTypes.Name, $"user_{userId}")
            };
            var identity  = new ClaimsIdentity(claims, "TestAuth");
            var principal = new ClaimsPrincipal(identity);

            controller.ControllerContext = new ControllerContext
            {
                HttpContext = new DefaultHttpContext { User = principal }
            };

            return controller;
        }

        /// <summary>
        /// Builds a minimal valid <see cref="WishlistItemDTO"/> for use in POST/PUT tests.
        /// </summary>
        private static WishlistItemDTO ValidItem(string name = "Test Item") =>
            new WishlistItemDTO
            {
                Name        = name,
                Description = "A test wishlist item",
                Priority    = 2,
                Tags        = new List<string> { "electronics" }
            };

        // -----------------------------------------------------------------------
        // GetAll
        // -----------------------------------------------------------------------

        /// <summary>AC1 – GetAll returns an empty list when the user has no items.</summary>
        [Fact]
        public void GetAll_ReturnsEmptyList_WhenNoItemsExist()
        {
            var controller = CreateController(Guid.NewGuid().ToString());

            var result = controller.GetAll() as OkObjectResult;

            Assert.NotNull(result);
            Assert.Equal(200, result!.StatusCode);
            var items = result.Value as IEnumerable<WishlistItemDTO>;
            Assert.NotNull(items);
            Assert.Empty(items!);
        }

        /// <summary>AC1 – GetAll returns all items belonging to the authenticated user.</summary>
        [Fact]
        public void GetAll_ReturnsItems_AfterCreation()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            controller.Create(ValidItem("Item A"));
            controller.Create(ValidItem("Item B"));

            var result = controller.GetAll() as OkObjectResult;

            Assert.NotNull(result);
            var items = (result!.Value as IEnumerable<WishlistItemDTO>)!.ToList();
            Assert.Equal(2, items.Count);
        }

        /// <summary>AC1 – GetAll does not return items belonging to a different user.</summary>
        [Fact]
        public void GetAll_DoesNotReturnOtherUsersItems()
        {
            var userA = Guid.NewGuid().ToString();
            var userB = Guid.NewGuid().ToString();

            CreateController(userA).Create(ValidItem("User A Item"));

            var resultB = CreateController(userB).GetAll() as OkObjectResult;
            var items   = (resultB!.Value as IEnumerable<WishlistItemDTO>)!.ToList();

            Assert.Empty(items);
        }

        // -----------------------------------------------------------------------
        // GetById
        // -----------------------------------------------------------------------

        /// <summary>AC1 – GetById returns the correct item when it exists.</summary>
        [Fact]
        public void GetById_ReturnsItem_WhenExists()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem()) as CreatedAtActionResult)!.Value as WishlistItemDTO;

            var result = controller.GetById(created!.Id) as OkObjectResult;

            Assert.NotNull(result);
            Assert.Equal(200, result!.StatusCode);
            var item = result.Value as WishlistItemDTO;
            Assert.Equal(created.Id, item!.Id);
        }

        /// <summary>AC1 – GetById returns 404 when the item does not exist.</summary>
        [Fact]
        public void GetById_Returns404_WhenNotFound()
        {
            var controller = CreateController(Guid.NewGuid().ToString());

            var result = controller.GetById(Guid.NewGuid()) as NotFoundObjectResult;

            Assert.NotNull(result);
            Assert.Equal(404, result!.StatusCode);
        }

        // -----------------------------------------------------------------------
        // Create
        // -----------------------------------------------------------------------

        /// <summary>AC2 – Create returns 201 and the new item on success.</summary>
        [Fact]
        public void Create_Returns201_WithNewItem()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var result = controller.Create(ValidItem("New Item")) as CreatedAtActionResult;

            Assert.NotNull(result);
            Assert.Equal(201, result!.StatusCode);
            var item = result.Value as WishlistItemDTO;
            Assert.NotNull(item);
            Assert.Equal("New Item", item!.Name);
            Assert.Equal(userId, item.UserId);
            Assert.False(item.IsPurchased);
        }

        /// <summary>AC2 – Create returns 400 when Name is missing.</summary>
        [Fact]
        public void Create_Returns400_WhenNameIsEmpty()
        {
            var controller = CreateController(Guid.NewGuid().ToString());
            var request    = ValidItem();
            request.Name   = "   "; // whitespace only

            var result = controller.Create(request) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result!.StatusCode);
        }

        /// <summary>AC2 – Create returns 400 when Priority is out of range.</summary>
        [Fact]
        public void Create_Returns400_WhenPriorityOutOfRange()
        {
            var controller = CreateController(Guid.NewGuid().ToString());
            var request    = ValidItem();
            request.Priority = 0; // invalid

            var result = controller.Create(request) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result!.StatusCode);
        }

        /// <summary>AC2 – Create returns 400 when Name exceeds 200 characters.</summary>
        [Fact]
        public void Create_Returns400_WhenNameTooLong()
        {
            var controller = CreateController(Guid.NewGuid().ToString());
            var request    = ValidItem(new string('x', 201));

            var result = controller.Create(request) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result!.StatusCode);
        }

        // -----------------------------------------------------------------------
        // Update
        // -----------------------------------------------------------------------

        /// <summary>AC4 – Update returns 200 and the modified item on success.</summary>
        [Fact]
        public void Update_Returns200_WithUpdatedItem()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem("Original")) as CreatedAtActionResult)!.Value as WishlistItemDTO;

            var updateRequest = ValidItem("Updated Name");
            updateRequest.Description = "Updated description";
            updateRequest.Priority    = 1;

            var result = controller.Update(created!.Id, updateRequest) as OkObjectResult;

            Assert.NotNull(result);
            Assert.Equal(200, result!.StatusCode);
            var updated = result.Value as WishlistItemDTO;
            Assert.Equal("Updated Name", updated!.Name);
            Assert.Equal("Updated description", updated.Description);
            Assert.Equal(1, updated.Priority);
            Assert.NotNull(updated.UpdatedAt);
        }

        /// <summary>AC4 – Update returns 404 when the item does not exist.</summary>
        [Fact]
        public void Update_Returns404_WhenNotFound()
        {
            var controller = CreateController(Guid.NewGuid().ToString());

            var result = controller.Update(Guid.NewGuid(), ValidItem()) as NotFoundObjectResult;

            Assert.NotNull(result);
            Assert.Equal(404, result!.StatusCode);
        }

        /// <summary>AC4 – Update returns 400 when Name is empty.</summary>
        [Fact]
        public void Update_Returns400_WhenNameIsEmpty()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem()) as CreatedAtActionResult)!.Value as WishlistItemDTO;

            var badRequest  = ValidItem();
            badRequest.Name = string.Empty;

            var result = controller.Update(created!.Id, badRequest) as BadRequestObjectResult;

            Assert.NotNull(result);
            Assert.Equal(400, result!.StatusCode);
        }

        // -----------------------------------------------------------------------
        // Delete
        // -----------------------------------------------------------------------

        /// <summary>AC3 – Delete returns 204 and the item is no longer retrievable.</summary>
        [Fact]
        public void Delete_Returns204_AndItemIsRemoved()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem()) as CreatedAtActionResult)!.Value as WishlistItemDTO;

            var deleteResult = controller.Delete(created!.Id) as NoContentResult;
            Assert.NotNull(deleteResult);
            Assert.Equal(204, deleteResult!.StatusCode);

            // Confirm the item is gone
            var getResult = controller.GetById(created.Id) as NotFoundObjectResult;
            Assert.NotNull(getResult);
        }

        /// <summary>AC3 – Delete returns 404 when the item does not exist.</summary>
        [Fact]
        public void Delete_Returns404_WhenNotFound()
        {
            var controller = CreateController(Guid.NewGuid().ToString());

            var result = controller.Delete(Guid.NewGuid()) as NotFoundObjectResult;

            Assert.NotNull(result);
            Assert.Equal(404, result!.StatusCode);
        }

        // -----------------------------------------------------------------------
        // MarkPurchased
        // -----------------------------------------------------------------------

        /// <summary>AC4 – MarkPurchased sets IsPurchased to true.</summary>
        [Fact]
        public void MarkPurchased_SetsFlag_ToTrue()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem()) as CreatedAtActionResult)!.Value as WishlistItemDTO;

            var result = controller.MarkPurchased(created!.Id, isPurchased: true) as OkObjectResult;

            Assert.NotNull(result);
            var item = result!.Value as WishlistItemDTO;
            Assert.True(item!.IsPurchased);
            Assert.NotNull(item.UpdatedAt);
        }

        /// <summary>AC4 – MarkPurchased can revert IsPurchased to false.</summary>
        [Fact]
        public void MarkPurchased_SetsFlag_ToFalse()
        {
            var userId     = Guid.NewGuid().ToString();
            var controller = CreateController(userId);

            var created = (controller.Create(ValidItem()) as CreatedAtActionResult)!.Value as WishlistItemDTO;
            controller.MarkPurchased(created!.Id, isPurchased: true);

            var result = controller.MarkPurchased(created.Id, isPurchased: false) as OkObjectResult;

            Assert.NotNull(result);
            var item = result!.Value as WishlistItemDTO;
            Assert.False(item!.IsPurchased);
        }

        /// <summary>AC4 – MarkPurchased returns 404 when the item does not exist.</summary>
        [Fact]
        public void MarkPurchased_Returns404_WhenNotFound()
        {
            var controller = CreateController(Guid.NewGuid().ToString());

            var result = controller.MarkPurchased(Guid.NewGuid()) as NotFoundObjectResult;

            Assert.NotNull(result);
            Assert.Equal(404, result!.StatusCode);
        }
    }
}
