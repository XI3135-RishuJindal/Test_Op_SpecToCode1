```javascript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import WishlistButton from './WishlistButton';
import { addToWishlist } from '../api/wishlist';
jest.mock('../api/wishlist');

describe('WishlistButton Component', () => {
    
    const product = { id: 1, name: 'Product 1' };

    test('renders wishlist button', () => {
        render(<WishlistButton product={product} />);
        const buttonElement = screen.getByRole('button', { name: /Add to Wishlist/i });
        expect(buttonElement).toBeInTheDocument();
    });

    test('calls addToWishlist API when clicked', async () => {
        addToWishlist.mockResolvedValueOnce({ success: true });

        render(<WishlistButton product={product} />);
        const buttonElement = screen.getByRole('button', { name: /Add to Wishlist/i });

        fireEvent.click(buttonElement);

        expect(addToWishlist).toHaveBeenCalledTimes(1);
        expect(addToWishlist).toHaveBeenCalledWith(product.id);
    });

    test('displays success message on API success', async () => {
        addToWishlist.mockResolvedValueOnce({ success: true });
        
        render(<WishlistButton product={product} />);
        const buttonElement = screen.getByRole('button', { name: /Add to Wishlist/i });

        fireEvent.click(buttonElement);

        const successMessage = await screen.findByText(/Added to wishlist!/i);
        expect(successMessage).toBeInTheDocument();
    });

    test('displays error message on API error', async () => {
        addToWishlist.mockRejectedValueOnce(new Error('Failed to add'));

        render(<WishlistButton product={product} />);
        const buttonElement = screen.getByRole('button', { name: /Add to Wishlist/i });

        fireEvent.click(buttonElement);

        const errorMessage = await screen.findByText(/Failed to add to wishlist/i);
        expect(errorMessage).toBeInTheDocument();
    });
});
```