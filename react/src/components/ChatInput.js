import React, { useState } from 'react';
import './ChatInput.css';

function ChatInput({ onSend, disabled, onClear }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const exampleQueries = [
    "Get customer 3",
    "Show me open tickets",
    "Find customers named John"
  ];

  return (
    <div className="chat-input-container">
      <div className="example-queries">
        {exampleQueries.map((query, index) => (
          <button
            key={index}
            className="example-query-btn"
            onClick={() => !disabled && onSend(query)}
            disabled={disabled}
          >
            {query}
          </button>
        ))}
      </div>
      
      <form onSubmit={handleSubmit} className="chat-input-form">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here... (Shift+Enter for new line)"
          disabled={disabled}
          rows={1}
        />
        <div className="input-actions">
          <button
            type="button"
            className="clear-button"
            onClick={onClear}
            disabled={disabled}
            title="Clear chat"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
          <button
            type="submit"
            className="send-button"
            disabled={disabled || !input.trim()}
          >
            {disabled ? (
              <div className="loading-spinner"></div>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}

export default ChatInput;

