```javascript
import React, { useContext } from 'react';
import { UserContext } from '../context/UserContext';
import './ProductPage.css';

const ProductPage = ({ product }) => {
  const { user } = useContext(UserContext);

  const handleAddToWishlist = () => {
    // Logic to add product to wishlist
    console.log(`Product ${product.id} added to wishlist`);
  };

  return (
    <div className="product-page">
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      {user && (
        <button className="wishlist-button" onClick={handleAddToWishlist}>
          Add to Wishlist
        </button>
      )}
    </div>
  );
};

export default ProductPage;
```