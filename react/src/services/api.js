import axios from 'axios';

// Backend API URL - adjust this based on your backend setup
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Send a message to the A2A-MCP backend
 * @param {string} message - User's message
 * @returns {Promise} - Response from backend
 */
export const sendMessage = async (message) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/chat`, {
      message: message,
      thread_id: getThreadId()
    }, {
      headers: {
        'Content-Type': 'application/json'
      },
      timeout: 60000 // 60 second timeout for complex queries
    });
    
    return response.data;
  } catch (error) {
    console.error('API Error:', error);
    
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.error || 'Server error occurred');
    } else if (error.request) {
      // Request made but no response
      throw new Error('Backend server is not responding. Please make sure it\'s running on ' + API_BASE_URL);
    } else {
      // Something else happened
      throw new Error('Failed to send message: ' + error.message);
    }
  }
};

/**
 * Get or create a thread ID for conversation tracking
 * @returns {string} - Thread ID
 */
const getThreadId = () => {
  let threadId = sessionStorage.getItem('thread_id');
  if (!threadId) {
    threadId = 'thread_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('thread_id', threadId);
  }
  return threadId;
};

/**
 * Clear the current thread (start new conversation)
 */
export const clearThread = () => {
  sessionStorage.removeItem('thread_id');
};

/**
 * Get A2A communication logs
 * @returns {Promise} - A2A logs
 */
export const getA2ALogs = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/a2a/logs`, {
      timeout: 10000
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch A2A logs:', error);
    return { logs: [] };
  }
};

/**
 * Check backend health
 * @returns {Promise<boolean>} - True if backend is healthy
 */
export const checkBackendHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, {
      timeout: 5000
    });
    return response.data.status === 'ok';
  } catch (error) {
    return false;
  }
};

