using System;
using System.Net.Http;
using System.Web.Http;
using System.Web.Http.Hosting;
using System.Web.Http.Testing;
using System.Threading.Tasks;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Moq;
using MyProject.Controllers;
using MyProject.Models;
using MyProject.Services;

namespace MyProject.Tests
{
    [TestClass]
    public class UsersControllerTests
    {
        private UsersController _controller;
        private Mock<IUserService> _userServiceMock;

        [TestInitialize]
        public void SetUp()
        {
            _userServiceMock = new Mock<IUserService>();
            _controller = new UsersController(_userServiceMock.Object)
            {
                Request = new HttpRequestMessage(),
                Configuration = new HttpConfiguration()
            };
        }

        [TestMethod]
        public async Task GetUser_ExistingId_ReturnsOkResult()
        {
            // Arrange
            var userId = Guid.NewGuid();
            var user = new User { Id = userId, Name = "John Doe" };
            _userServiceMock.Setup(service => service.GetUserAsync(userId)).ReturnsAsync(user);

            // Act
            var response = await _controller.GetUser(userId);

            // Assert
            Assert.IsInstanceOfType(response, typeof(OkNegotiatedContentResult<User>));
            var contentResult = response as OkNegotiatedContentResult<User>;
            Assert.AreEqual(user.Name, contentResult.Content.Name);
        }

        [TestMethod]
        public async Task GetUser_NonExistingId_ReturnsNotFoundResult()
        {
            // Arrange
            var userId = Guid.NewGuid();
            _userServiceMock.Setup(service => service.GetUserAsync(userId)).ReturnsAsync((User)null);

            // Act
            var response = await _controller.GetUser(userId);

            // Assert
            Assert.IsInstanceOfType(response, typeof(NotFoundResult));
        }

        [TestMethod]
        public async Task CreateUser_ValidUser_ReturnsCreatedAtRouteResult()
        {
            // Arrange
            var newUser = new User { Name = "Jane Doe" };
            _userServiceMock.Setup(service => service.CreateUserAsync(newUser)).ReturnsAsync(newUser);

            // Act
            var response = await _controller.CreateUser(newUser);

            // Assert
            Assert.IsInstanceOfType(response, typeof(CreatedAtRouteNegotiatedContentResult<User>));
            var createdContentResult = response as CreatedAtRouteNegotiatedContentResult<User>;
            Assert.AreEqual(newUser.Name, createdContentResult.Content.Name);
        }
    }
}