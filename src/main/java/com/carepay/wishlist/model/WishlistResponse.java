```java
package com.carepay.wishlist.model;

public class WishlistResponse {
    private String message;

    public WishlistResponse(String message) {
        this.message = message;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
```