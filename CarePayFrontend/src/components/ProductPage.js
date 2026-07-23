```javascript
import React, { useState } from 'react';
import { addToWishlist } from '../api/wishlistApi';

function ProductPage({ product, user }) {
  const [inWishlist, setInWishlist] = useState(false);

  const handleAddToWishlist = async () => {
    if (!user) {
      alert('Please log in to add products to your wishlist');
      return;
    }

    try {
      await addToWishlist(product.id);
      setInWishlist(true);
    } catch (error) {
      console.error('Failed to add product to wishlist', error);
    }
  };

  return (
    <div className="product-page">
      <h1>{product.name}</h1>
      <button onClick={handleAddToWishlist} disabled={inWishlist}>
        {inWishlist ? 'Added to Wishlist' : 'Add to Wishlist'}
      </button>
    </div>
  );
}

export default ProductPage;
```