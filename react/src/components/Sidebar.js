import React from 'react';
import './Sidebar.css';

function Sidebar({ isOpen, onClose, onExampleQuery, a2aLogs }) {
  const exampleQueries = [
    {
      category: "Customer Info",
      icon: "👤",
      queries: [
        "Get customer 3",
        "List all active customers",
        "Show customers 2 and 4",
        "Add a new customer John Doe"
      ]
    },
    {
      category: "Support & Tickets",
      icon: "🎫",
      queries: [
        "Show open tickets",
        "Create ticket for customer 5",
        "Get ticket history for customer 2",
        "Show high priority tickets"
      ]
    },
    {
      category: "Complex Queries",
      icon: "🔍",
      queries: [
        "Customer 5 with complete ticket history",
        "Find customers named Smith",
        "Customers created in December",
        "Show customers with most tickets"
      ]
    }
  ];

  return (
    <>
      <div className={`sidebar-overlay ${isOpen ? 'active' : ''}`} onClick={onClose}></div>
      <div className={`sidebar ${isOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>Menu</h2>
          <button className="close-button" onClick={onClose}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-section">
            <h3>💡 Example Queries</h3>
            {exampleQueries.map((category, idx) => (
              <div key={idx} className="query-category">
                <div className="category-header">
                  <span className="category-icon">{category.icon}</span>
                  <span className="category-name">{category.category}</span>
                </div>
                <div className="query-list">
                  {category.queries.map((query, qIdx) => (
                    <button
                      key={qIdx}
                      className="query-button"
                      onClick={() => onExampleQuery(query)}
                    >
                      {query}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {a2aLogs.length > 0 && (
            <div className="sidebar-section">
              <h3>🤝 A2A Activity</h3>
              <div className="a2a-logs">
                {a2aLogs.slice(-5).reverse().map((log, idx) => (
                  <div key={idx} className="a2a-log-item">
                    <div className="a2a-log-query">{log.query}</div>
                    <div className="a2a-log-time">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="sidebar-section">
            <h3>ℹ️ About</h3>
            <div className="about-content">
              <p>
                <strong>Multi-Agent System</strong>
              </p>
              <p>Powered by A2A-MCP architecture with:</p>
              <ul>
                <li>🎯 Smart routing</li>
                <li>👤 Customer data management</li>
                <li>🎫 Support ticketing</li>
                <li>🔍 Complex SQL queries</li>
                <li>🤝 Agent-to-agent coordination</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default Sidebar;

