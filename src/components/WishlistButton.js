```javascript
import React, { useState } from 'react';
import { addToWishlist } from '../api/wishlist';

const WishlistButton = ({ product }) => {
    const [status, setStatus] = useState(null);

    const handleAddToWishlist = async () => {
        try {
            await addToWishlist(product.id);
            setStatus('success');
        } catch (error) {
            setStatus('error');
        }
    };

    return (
        <div>
            <button onClick={handleAddToWishlist}>
                Add to Wishlist
            </button>
            {status === 'success' && <p>Added to wishlist!</p>}
            {status === 'error' && <p>Failed to add to wishlist</p>}
        </div>
    );
};

export default WishlistButton;
```