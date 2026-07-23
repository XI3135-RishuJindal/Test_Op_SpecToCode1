```java
package com.carepay.api.controller;

import com.carepay.api.service.WishlistService;
import com.carepay.api.security.AuthService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.access.prepost.PreAuthorize;

@RestController
@RequestMapping("/api/wishlist")
public class WishlistController {

    @Autowired
    private WishlistService wishlistService;

    @Autowired
    private AuthService authService;

    // Endpoint to add a product to the wishlist
    @PreAuthorize("isAuthenticated()")
    @PostMapping("/add")
    public ResponseEntity<?> addProductToWishlist(@RequestParam Long productId) {
        if (authService.isAuthenticated()) {
            wishlistService.addProductToWishlist(productId);
            return ResponseEntity.ok("Product added to wishlist");
        } else {
            return ResponseEntity.status(401).body("User must be logged in to perform this action");
        }
    }
}
```