```javascript
// Routes for managing user wishlists

const express = require('express');
const router = express.Router();
const wishlistController = require('../controllers/wishlistController');

// Add a product to a user's wishlist
router.post('/add', wishlistController.addToWishlist);

// Remove a product from a user's wishlist
router.delete('/remove', wishlistController.removeFromWishlist);

module.exports = router;
```