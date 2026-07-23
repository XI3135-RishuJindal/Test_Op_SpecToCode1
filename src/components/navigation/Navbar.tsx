import React from 'react';
import { NavLink } from 'react-router-dom';

const linkStyle: React.CSSProperties = {
  padding: '0.5rem 0.75rem',
  textDecoration: 'none',
  color: 'inherit',
};

const activeStyle: React.CSSProperties = {
  fontWeight: 600,
  borderBottom: '2px solid currentColor',
};

const Navbar: React.FC = () => {
  return (
    <nav
      aria-label="Primary"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.75rem 1rem',
        borderBottom: '1px solid #e5e7eb',
      }}
    >
      <NavLink to="/" style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })} end>
        Home
      </NavLink>
      <NavLink
        to="/settings"
        style={({ isActive }) => ({ ...linkStyle, ...(isActive ? activeStyle : {}) })}
      >
        Settings
      </NavLink>
    </nav>
  );
};

export default Navbar;