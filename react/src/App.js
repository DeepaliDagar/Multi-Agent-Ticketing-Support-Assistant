import React, { useState, useEffect } from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';
import ChatInput from './components/ChatInput';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import { sendMessage } from './services/api';

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "👋 Hi! I'm your AI assistant powered by a multi-agent ticket management system. I can help you with:\n\n• Customer information\n• Support tickets\n• Analytical queries on database\n\nHow can I help you today?",
      sender: 'bot',
      timestamp: new Date(),
      agent: 'system'
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [a2aLogs, setA2aLogs] = useState([]);

  const handleSendMessage = async (text) => {
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      text,
      sender: 'user',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send to backend
      const response = await sendMessage(text);
      
      // Add bot response
      const botMessage = {
        id: messages.length + 2,
        text: response.response || response.message || 'I apologize, but I encountered an issue processing your request.',
        sender: 'bot',
        timestamp: new Date(),
        agent: response.primary_agent || 'unknown',
        a2a_count: response.a2a_count || 0
      };
      
      setMessages(prev => [...prev, botMessage]);
      
      // Update A2A logs if available
      if (response.a2a_summary) {
        setA2aLogs(prev => [...prev, {
          query: text,
          summary: response.a2a_summary,
          timestamp: new Date()
        }]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: messages.length + 2,
        text: '❌ Sorry, I encountered an error. Please make sure the backend server is running.',
        sender: 'bot',
        timestamp: new Date(),
        agent: 'error'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: 1,
        text: "👋 Hi! I'm your AI assistant powered by a multi-agent ticket management system. How can I help you today?",
        sender: 'bot',
        timestamp: new Date(),
        agent: 'system'
      }
    ]);
    setA2aLogs([]);
  };

  const handleExampleQuery = (query) => {
    handleSendMessage(query);
    setSidebarOpen(false);
  };

  return (
    <div className="app">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="app-container">
        <Sidebar 
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onExampleQuery={handleExampleQuery}
          a2aLogs={a2aLogs}
        />
        
        <div className="chat-container">
          <ChatWindow 
            messages={messages} 
            isLoading={isLoading}
          />
          <ChatInput 
            onSend={handleSendMessage}
            disabled={isLoading}
            onClear={handleClearChat}
          />
        </div>
      </div>
    </div>
  );
}

export default App;

