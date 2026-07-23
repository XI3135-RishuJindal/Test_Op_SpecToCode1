```javascript
import React from 'react';
import UserProvider from './context/UserContext';
import ProductPage from './components/ProductPage';

function App() {
  const demoProduct = {
    id: 1,
    name: 'Sample Product',
    description: 'This is a sample product description.'
  };

  return (
    <UserProvider>
      <div className="App">
        <ProductPage product={demoProduct} />
      </div>
    </UserProvider>
  );
}

export default App;
```