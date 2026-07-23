```java
package com.carepay.wishlist.model;

public class WishlistRequest {
    private Long userId;
    private Long productId;

    public WishlistRequest() {}

    public WishlistRequest(Long userId, Long productId) {
        this.userId = userId;
        this.productId = productId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public Long getProductId() {
        return productId;
    }

    public void setProductId(Long productId) {
        this.productId = productId;
    }
}
```