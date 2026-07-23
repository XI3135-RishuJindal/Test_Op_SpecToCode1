```javascript
const express = require('express');
const router = express.Router();
const { addProductToWishlist } = require('../controllers/wishlistController');
const { authenticateUser } = require('../middleware/authMiddleware');

router.post('/wishlist/add', authenticateUser, async (req, res) => {
  try {
    const { productId } = req.body;
    const userId = req.user.id;
    await addProductToWishlist(userId, productId);
    res.status(200).send({ message: 'Product added to wishlist successfully' });
  } catch (error) {
    res.status(500).send({ error: 'Failed to add product to wishlist' });
  }
});

module.exports = router;
```