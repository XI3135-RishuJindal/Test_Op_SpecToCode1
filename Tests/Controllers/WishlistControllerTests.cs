```csharp
using Xunit;
using Moq;
using Microsoft.AspNetCore.Mvc;
using ApiGateway.Controllers;
using ApiGateway.Models;
using ApiGateway.Services;
using System.Security.Claims;

namespace ApiGateway.Tests.Controllers
{
    public class WishlistControllerTests
    {
        private readonly Mock<WishlistService> _wishlistServiceMock;
        private readonly WishlistController _controller;

        public WishlistControllerTests()
        {
            _wishlistServiceMock = new Mock<WishlistService>();
            _controller = new WishlistController(_wishlistServiceMock.Object)
            {
                ControllerContext = new ControllerContext()
                {
                    HttpContext = new DefaultHttpContext()
                    {
                        User = new ClaimsPrincipal(new ClaimsIdentity(new Claim[]
                        {
                            new Claim(ClaimTypes.NameIdentifier, "user-id")
                        }))
                    }
                }
            };
        }

        [Fact]
        public void AddToWishlist_ReturnsOk_WhenProductIsAdded()
        {
            _wishlistServiceMock.Setup(service => service.AddProductToWishlist(It.IsAny<string>(), It.IsAny<int>())).Returns(true);

            var result = _controller.AddToWishlist(new WishlistDTO { ProductId = 1 });

            Assert.IsType<OkObjectResult>(result);
        }

        [Fact]
        public void AddToWishlist_ReturnsBadRequest_WhenProductAlreadyExists()
        {
            _wishlistServiceMock.Setup(service => service.AddProductToWishlist(It.IsAny<string>(), It.IsAny<int>())).Returns(false);

            var result = _controller.AddToWishlist(new WishlistDTO { ProductId = 1 });

            Assert.IsType<BadRequestObjectResult>(result);
        }
    }
}
```

#### Program.cs Update with DI and Context