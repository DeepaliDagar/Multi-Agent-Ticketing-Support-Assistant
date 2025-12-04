import React from 'react';
import './TypingIndicator.css';

function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div className="typing-avatar">
        <span className="avatar-icon">🤖</span>
      </div>
      <div className="typing-bubble">
        <div className="typing-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}

export default TypingIndicator;

