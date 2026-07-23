```javascript
export const addToWishlist = async (productId) => {
    // Dummy implementation for mock demonstration purposes
    // Should interact with backend to add product to wishlist
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (productId) {
                resolve({ success: true });
            } else {
                reject(new Error('Failed to add'));
            }
        }, 500);
    });
};
```