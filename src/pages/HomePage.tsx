import React from 'react';
import Navbar from '../components/navigation/Navbar';

const HomePage: React.FC = () => {
  return (
    <div>
      <Navbar />
      <main role="main" aria-label="Main content" style={{ padding: '1rem' }}>
        <h1>Welcome</h1>
        <p>Explore core features from the navigation.</p>
      </main>
    </div>
  );
};

export default HomePage;