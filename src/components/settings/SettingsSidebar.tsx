import React from 'react';
import { NavLink } from 'react-router-dom';

const itemStyle: React.CSSProperties = {
  display: 'block',
  padding: '0.5rem 0.75rem',
  textDecoration: 'none',
  color: 'inherit',
};

const activeItemStyle: React.CSSProperties = {
  fontWeight: 600,
  backgroundColor: '#f3f4f6',
  borderRadius: 6,
};

const SettingsSidebar: React.FC = () => {
  return (
    <aside
      aria-label="Settings navigation"
      style={{
        width: 240,
        borderRight: '1px solid #e5e7eb',
        padding: '1rem',
      }}
    >
      <nav aria-label="Settings sections" style={{ display: 'grid', gap: 4 }}>
        <NavLink
          to="/settings/profile"
          style={({ isActive }) => ({ ...itemStyle, ...(isActive ? activeItemStyle : {}) })}
        >
          Profile
        </NavLink>
        <NavLink
          to="/settings/account"
          style={({ isActive }) => ({ ...itemStyle, ...(isActive ? activeItemStyle : {}) })}
        >
          Account
        </NavLink>
        <NavLink
          to="/settings/security"
          style={({ isActive }) => ({ ...itemStyle, ...(isActive ? activeItemStyle : {}) })}
        >
          Security
        </NavLink>
        <NavLink
          to="/settings/notifications"
          style={({ isActive }) => ({ ...itemStyle, ...(isActive ? activeItemStyle : {}) })}
        >
          Notifications
        </NavLink>
        <NavLink
          to="/settings/integrations"
          style={({ isActive }) => ({ ...itemStyle, ...(isActive ? activeItemStyle : {}) })}
        >
          Integrations
        </NavLink>
      </nav>
    </aside>
  );
};

export default SettingsSidebar;