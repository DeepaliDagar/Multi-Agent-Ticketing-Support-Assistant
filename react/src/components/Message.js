import React from 'react';
import './Message.css';
import ReactMarkdown from 'react-markdown';

function Message({ message }) {
  const { text, sender, timestamp, agent, a2a_count } = message;
  
  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const getAgentIcon = (agentName) => {
    const icons = {
      'customer_data': '👤',
      'customer_data_agent': '👤',
      'support': '🎫',
      'support_agent': '🎫',
      'sql': '🔍',
      'fallback_sql_generator_agent': '🔍',
      'router': '🎯',
      'system': '🤖',
      'error': '❌',
      'unknown': '🤖'
    };
    return icons[agentName] || '🤖';
  };

  const getAgentName = (agentName) => {
    const names = {
      'customer_data': 'Customer Data',
      'customer_data_agent': 'Customer Data',
      'support': 'Support',
      'support_agent': 'Support',
      'sql': 'SQL Generator',
      'fallback_sql_generator_agent': 'SQL Generator',
      'router': 'Router',
      'system': 'System',
      'error': 'Error',
      'unknown': 'Assistant'
    };
    return names[agentName] || 'Assistant';
  };

  return (
    <div className={`message ${sender === 'user' ? 'message-user' : 'message-bot'}`}>
      {sender === 'bot' && (
        <div className="message-avatar">
          <span className="avatar-icon">{getAgentIcon(agent)}</span>
        </div>
      )}
      
      <div className="message-content">
        {sender === 'bot' && agent && agent !== 'system' && (
          <div className="message-agent">
            <span className="agent-name">{getAgentName(agent)}</span>
            {a2a_count > 0 && (
              <span className="a2a-badge" title="Agent-to-Agent interactions">
                🤝 {a2a_count} A2A
              </span>
            )}
          </div>
        )}
        
        <div className="message-bubble">
          {sender === 'bot' ? (
            <ReactMarkdown className="markdown-content">
              {text}
            </ReactMarkdown>
          ) : (
            <p>{text}</p>
          )}
        </div>
        
        <div className="message-time">{formatTime(timestamp)}</div>
      </div>
      
      {sender === 'user' && (
        <div className="message-avatar">
          <span className="avatar-icon">👨‍💻</span>
        </div>
      )}
    </div>
  );
}

export default Message;

