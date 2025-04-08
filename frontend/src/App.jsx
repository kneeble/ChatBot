import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    const userMessage = { text: input, sender: 'user', timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await axios.post(
        '/generate',
        { prompt: input },
        { responseType: 'text' }
      );

      let botMessage = { text: '', sender: 'bot', timestamp: new Date() };
      setMessages(prev => [...prev, botMessage]);

      for (let i = 0; i < response.data.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 20));
        botMessage.text += response.data[i];
        setMessages(prev => [...prev.slice(0, -1), { ...botMessage }]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: 'Failed to fetch response', 
        sender: 'bot', 
        timestamp: new Date() 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>NextGen Advanced AI</h1>
        <div className="status-indicator">
          <span className="status-dot"></span>
          <span>Connected</span>
        </div>
      </header>

      <div className="chat-container">
        <div className="messages-wrapper">
          {messages.map((msg, i) => (
            <div 
              key={i} 
              className={`message ${msg.sender}`}
            >
              <div className="message-content">
                {msg.text}
              </div>
              <div className="message-timestamp">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Message NextGen"
          disabled={isLoading}
        />
        <button 
          onClick={sendMessage}
          disabled={isLoading}
          className="send-button"
        >
          {isLoading ? (
            <div className="spinner"></div>
          ) : (
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9" stroke="currentColor" strokeWidth="2"/>
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export default App;