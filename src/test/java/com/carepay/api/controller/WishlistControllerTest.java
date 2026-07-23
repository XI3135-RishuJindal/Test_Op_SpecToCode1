```java
package com.carepay.api.controller;

import com.carepay.api.service.WishlistService;
import com.carepay.api.security.AuthService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.when;

class WishlistControllerTest {

    @Mock
    private WishlistService wishlistService;

    @Mock
    private AuthService authService;

    @InjectMocks
    private WishlistController wishlistController;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void testAddProductToWishlist_Unauthenticated() {
        when(authService.isAuthenticated()).thenReturn(false);

        ResponseEntity<?> response = wishlistController.addProductToWishlist(1L);

        assertEquals(HttpStatus.UNAUTHORIZED, response.getStatusCode());
        assertEquals("User must be logged in to perform this action", response.getBody());
    }

    @Test
    void testAddProductToWishlist_Authenticated() {
        when(authService.isAuthenticated()).thenReturn(true);

        ResponseEntity<?> response = wishlistController.addProductToWishlist(1L);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("Product added to wishlist", response.getBody());
    }
}
```