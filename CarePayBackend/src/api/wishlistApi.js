```javascript
import axios from 'axios';

export const addToWishlist = async (productId) => {
  const response = await axios.post('/api/wishlist/add', { productId });
  return response.data;
};
```