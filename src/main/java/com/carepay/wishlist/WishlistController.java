```java
package com.carepay.wishlist;

import com.carepay.wishlist.service.WishlistService;
import com.carepay.wishlist.model.WishlistResponse;
import com.carepay.wishlist.model.WishlistRequest;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/wishlist")
public class WishlistController {

    @Autowired
    private WishlistService wishlistService;

    @PostMapping("/add")
    public ResponseEntity<WishlistResponse> addProductToWishlist(@RequestBody WishlistRequest request) {
        if (wishlistService.addProductToWishlist(request)) {
            return new ResponseEntity<>(new WishlistResponse("Product added to wishlist"), HttpStatus.OK);
        }
        return new ResponseEntity<>(new WishlistResponse("Product could not be added"), HttpStatus.BAD_REQUEST);
    }

    @DeleteMapping("/remove")
    public ResponseEntity<WishlistResponse> removeProductFromWishlist(@RequestBody WishlistRequest request) {
        if (wishlistService.removeProductFromWishlist(request)) {
            return new ResponseEntity<>(new WishlistResponse("Product removed from wishlist"), HttpStatus.OK);
        }
        return new ResponseEntity<>(new WishlistResponse("Product could not be removed"), HttpStatus.BAD_REQUEST);
    }
}
```