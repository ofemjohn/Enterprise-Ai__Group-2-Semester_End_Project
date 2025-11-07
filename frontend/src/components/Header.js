import React from 'react';
import { FiMenu, FiX } from 'react-icons/fi';
import './Header.css';

const Header = ({ onMenuClick, sidebarOpen }) => {
  return (
    <header className="header">
      <div className="header-content">
        <button 
          className="menu-button"
          onClick={onMenuClick}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
        
        <div className="header-brand">
          <div className="logo-container">
            {/* KSU Logo - Replace with actual logo */}
            <div className="logo-placeholder">
              <span className="logo-text">KSU</span>
            </div>
          </div>
          <div className="brand-text">
            <h1 className="brand-title">KSU IT Chatbot</h1>
            <p className="brand-subtitle">Kennesaw State University</p>
          </div>
        </div>
        
        <div className="header-status">
          <div className="status-indicator">
            <span className="status-dot"></span>
            <span className="status-text">Online</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

