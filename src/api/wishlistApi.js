```javascript
export const addToWishlist = async (productId) => {
  const response = await fetch(`/api/wishlist/add`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ productId }),
  });

  if (!response.ok) {
    throw new Error('Failed to add product to wishlist');
  }

  return response.json();
};

export const viewWishlist = () => {
  window.location.href = '/wishlist';
};
```