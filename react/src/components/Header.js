import React from 'react';
import './Header.css';

function Header({ onToggleSidebar }) {
  return (
    <header className="header">
      <div className="header-content">
        <button className="menu-button" onClick={onToggleSidebar}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </button>
        
        <div className="header-title">
          <div className="logo">
            <span className="logo-icon">🤖</span>
            <span className="logo-text">A2A-MCP</span>
          </div>
          <div className="header-subtitle">Multi-Agent Support Assistant</div>
        </div>
        
        <div className="header-status">
          <div className="status-indicator"></div>
          <span className="status-text">Online</span>
        </div>
      </div>
    </header>
  );
}

export default Header;

