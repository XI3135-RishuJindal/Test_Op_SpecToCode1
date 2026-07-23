```javascript
const Wishlist = require('../models/Wishlist');

exports.addProductToWishlist = async (userId, productId) => {
  const wishlist = await Wishlist.findOne({ userId });

  if (!wishlist) {
    return await Wishlist.create({ userId, products: [productId] });
  }

  if (!wishlist.products.includes(productId)) {
    wishlist.products.push(productId);
    await wishlist.save();
  }
};
```