```javascript
// Controller for wishlist operations

const Wishlist = require('../../database/models/wishlist');

exports.addToWishlist = async (req, res) => {
    const { userId, productId } = req.body;
    try {
        await Wishlist.create({ userId, productId });
        res.status(201).json({ message: 'Product added to wishlist.' });
    } catch (error) {
        res.status(500).json({ message: 'Failed to add product to wishlist.' });
    }
};

exports.removeFromWishlist = async (req, res) => {
    const { userId, productId } = req.body;
    try {
        await Wishlist.destroy({
            where: {
                userId,
                productId
            }
        });
        res.status(200).json({ message: 'Product removed from wishlist.' });
    } catch (error) {
        res.status(500).json({ message: 'Failed to remove product from wishlist.' });
    }
};
```