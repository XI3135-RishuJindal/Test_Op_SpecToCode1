```javascript
import React, { useState } from 'react';
import { addToWishlist, viewWishlist } from '../api/wishlistApi';

const ProductPage = ({ product, user }) => {
  const [isInWishlist, setIsInWishlist] = useState(false);

  const handleAddToWishlist = async () => {
    try {
      await addToWishlist(product.id);
      setIsInWishlist(true);
      alert('Product added to wishlist!');
    } catch (error) {
      alert('There was an error adding the product to your wishlist. Please try again.');
    }
  };

  return (
    <div className="product-page">
      <h1>{product.name}</h1>
      <p>{product.description}</p>

      {user && (
        <button onClick={handleAddToWishlist} title="Add to wishlist">
          <i className={`heart-icon ${isInWishlist ? 'added' : ''}`}></i> Add to Wishlist
        </button>
      )}

      <button onClick={viewWishlist}>
        View Wishlist
      </button>
    </div>
  );
};

export default ProductPage;
```