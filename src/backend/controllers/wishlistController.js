```javascript
const Wishlist = require('../models/Wishlist');

exports.addProductToWishlist = async (req, res) => {
  try {
    const { userId } = req.user;
    const { productId } = req.body;

    const existingItem = await Wishlist.findOne({ userId, productId });
    if (existingItem) {
      return res.status(400).json({ message: 'Product already in wishlist' });
    }

    const newItem = new Wishlist({ userId, productId });
    await newItem.save();

    res.status(200).json({ message: 'Product added to wishlist' });
  } catch (error) {
    res.status(500).json({ message: 'Server error' });
  }
};
```