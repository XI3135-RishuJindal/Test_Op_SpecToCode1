```javascript
'use strict';

// Seeder script to populate the wishlists table with initial data

module.exports = {
    up: async (queryInterface, Sequelize) => {
        await queryInterface.bulkInsert('wishlists', [
            {
                userId: 1,
                productId: 2
            },
            {
                userId: 1,
                productId: 3
            },
            {
                userId: 2,
                productId: 1
            }
        ], {});
    },

    down: async (queryInterface, Sequelize) => {
        await queryInterface.bulkDelete('wishlists', null, {});
    }
};
```