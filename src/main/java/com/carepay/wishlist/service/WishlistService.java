```java
package com.carepay.wishlist.service;

import com.carepay.wishlist.model.WishlistRequest;
import org.springframework.stereotype.Service;

@Service
public class WishlistService {

    public boolean addProductToWishlist(WishlistRequest request) {
        // Logic to add product to wishlist (interact with database)
        return true;
    }

    public boolean removeProductFromWishlist(WishlistRequest request) {
        // Logic to remove product from wishlist (interact with database)
        return true;
    }
}
```