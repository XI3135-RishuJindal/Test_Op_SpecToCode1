import React from 'react';
import Navbar from '../components/navigation/Navbar';
import SettingsSidebar from '../components/settings/SettingsSidebar';

const SettingsPage: React.FC = () => {
  return (
    <div>
      <Navbar />
      <div style={{ display: 'flex', minHeight: '60vh' }}>
        <SettingsSidebar />
        <section
          role="region"
          aria-label="Settings content"
          style={{ flex: 1, padding: '1rem' }}
        >
          <h1>Settings</h1>
          <p>Select a settings category from the sidebar.</p>
        </section>
      </div>
    </div>
  );
};

export default SettingsPage;