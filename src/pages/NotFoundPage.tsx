import React from 'react';
import Navbar from '../components/navigation/Navbar';

const NotFoundPage: React.FC = () => {
  return (
    <div>
      <Navbar />
      <main role="main" aria-label="Not found" style={{ padding: '1rem' }}>
        <h1>404</h1>
        <p>The page you are looking for does not exist.</p>
      </main>
    </div>
  );
};

export default NotFoundPage;