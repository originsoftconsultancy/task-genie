import React, { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import CampaignShowcase from '../components/CampaignShowcase';
import './Chat.css';

/**
 * Generate a single response from Ollama
 */
const generateSingleResponse = async (message, progressCallback, format = 'text') => {
  const systemMessage = "You are a helpful assistant that responds in clear, concise text.";
  const model = 'llama3.2:1b';
  const messages = [
    { "role": "system", "content": systemMessage },
    { "role": "user", "content": message }
  ];

  try {
    console.log('Sending request to local Ollama model:', message);

    const response = await fetch('http://192.168.0.104:5000/process_prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: message
      }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    // Remove accumulated response since we're creating separate messages
    // let accumulatedResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      console.log(chunk);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (!line) continue;

        try {
          const json = JSON.parse(line);
          if (json.message && json.message.type) {
            const content = json.message.content;
            const type = json.message.type;
            
            // Handle each message type as a separate message
            if (type === "text") {
              // Create a new message for text
              progressCallback(content, 'text');
            }
            else if (type === 'file') {
              // Extract filename from URL and create a file message
              const fileUrl = content;
              const fileName = fileUrl.substring(fileUrl.lastIndexOf('/')+1);
              progressCallback(fileUrl, 'file', fileName);
            }
            else if (type === 'image') {
              // Create an image message
              progressCallback(content, 'image');
            }
            else if (type === 'table') {
              // Create a table message
              progressCallback(content, 'table');
            }
          }
        } catch (e) {
          console.error('Error parsing JSON from stream:', e);
        }
      }
    }

    return 'Response complete';
  } catch (error) {
    console.error('Error calling Ollama API:', error);
    throw error;
  }
};

// Simulate delay for demo purposes
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Main Chat component
 */
const Chat = () => {
  // State for managing messages and UI
  const [messages, setMessages] = useState([
    { id: 1, text: "Hello! I'm your AI assistant. How can I help you today?", sender: "ai" }
  ]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [messageIdCounter, setMessageIdCounter] = useState(2);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Refs for UI manipulation
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
    if (inputRef.current && !loading) {
      inputRef.current.focus();
    }
  }, [messages, loading]);

  // Toggle sidebar visibility
  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  // Handle sending a new message
  const handleSendMessage = async (e) => {
    if (e) e.preventDefault();

    if (inputText.trim() === '' || loading) return;

    // Add user message
    const userMessageId = messageIdCounter;
    const newUserMessage = {
      id: userMessageId,
      text: inputText,
      sender: "user"
    };

    setMessages(prev => [...prev, newUserMessage]);
    setMessageIdCounter(prev => prev + 1);
    setInputText('');
    setLoading(true);

    try {
      // Generate text response
      console.log("Generating text response...");
      await generateSingleResponse(
        newUserMessage.text,
        (content, type = 'text', meta = null) => {
          // Create a new message for each response
          const newResponseId = messageIdCounter + Math.random(); // Ensure unique ID
          
          setMessages(prev => [...prev, {
            id: newResponseId,
            text: content,
            type: type,
            meta: meta,
            sender: "ai",
            isTyping: false
          }]);
          
          setMessageIdCounter(prev => prev + 1);
        },
        'text'
      );

    } catch (error) {
      console.error('Error generating response:', error);

      // Add error message
      setMessages(prev => [...prev, {
        id: messageIdCounter,
        text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        sender: "ai",
        isTyping: false
      }]);
      setMessageIdCounter(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  // Render response content with proper formatting
  const renderResponseContent = (content, type, meta) => {
    if (!content) return null;

    // Handle different types of content
    switch(type) {
      case 'image':
        return (
          <div className="image-container">
            <img src={content} alt="Generated image" className="chat-image" />
          </div>
        );
        
      case 'file':
        // Extract filename from URL or use meta if available
        const fileName = meta || content.substring(content.lastIndexOf('/')+1);
        return (
          <div className="file-container">
            <a href={content} target="_blank" rel="noopener noreferrer" className="pdf-button">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <polyline points="14 2 14 8 20 8" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Download {fileName}</span>
            </a>
          </div>
        );
        
      case 'table':
        // Parse CSV content
        const rows = content.split('\n');
        return (
          <div className="table-container">
            <table className="message-table">
              <thead>
                <tr>
                  {rows[0].split(',').map((header, i) => (
                    <th key={i}>{header}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.slice(1).map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {row.split(',').map((cell, cellIndex) => (
                      <td key={cellIndex}>{cell}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
        
      case 'text':
      default:
        // Regular text formatting with line breaks
        return content.split('\n').map((line, i) => (
          <React.Fragment key={i}>
            {line}
            {i < content.split('\n').length - 1 && <br />}
          </React.Fragment>
        ));
    }
  };

  // Handle quick prompts
  const handleQuickPrompt = (prompt) => {
    setInputText(prompt);
    inputRef.current?.focus();
  };

  return (
    <div className="chat-screen">
      <Header />
      <main className="chat-main-content">
        <div className="chat-layout">
          <button
            className={`sidebar-toggle ${!isSidebarOpen ? 'sidebar-closed' : ''}`}
            onClick={toggleSidebar}
            title={isSidebarOpen ? "Hide Campaigns" : "Show Campaigns"}
            aria-label={isSidebarOpen ? "Hide campaigns sidebar" : "Show campaigns sidebar"}
          >
            <span className="toggle-icon">{isSidebarOpen ? "❮" : "❯"}</span>
            <span className="toggle-text">{isSidebarOpen ? "Hide" : "Show"}</span>
          </button>

          <div className={`chat-sidebar ${isSidebarOpen ? '' : 'hidden'}`}>
            <CampaignShowcase />
          </div>

          <div className={`chat-section ${isSidebarOpen ? '' : 'expanded'}`}>
            <div className="chat-container">
              <h1 className="chat-title">Chat with Me</h1>

              <div className="chat-window">
                <div className="messages-container">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'}`}
                    >
                      {message.sender === 'ai'
                        ? renderResponseContent(message.text, message.type, message.meta)
                        : message.text
                      }
                      {message.sender === 'ai' && message.isTyping &&
                        <span className="typing-indicator">
                          <span className="dot"></span>
                          <span className="dot"></span>
                          <span className="dot"></span>
                        </span>
                      }
                    </div>
                  ))}

                  <div ref={messagesEndRef} />
                </div>

                <div className="chat-input-container">
                  <form onSubmit={handleSendMessage} className="message-form">
                    <div className="input-wrapper">
                      <input
                        ref={inputRef}
                        type="text"
                        value={inputText}
                        onChange={(e) => setInputText(e.target.value)}
                        placeholder="Type your question here..."
                        className="message-input"
                        disabled={loading}
                      />
                      <button
                        type="submit"
                        className="send-button"
                        disabled={inputText.trim() === '' || loading}
                      >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </button>
                    </div>

                    <div className="quick-prompts">
                      <button
                        type="button"
                        className="prompt-button"
                        onClick={() => handleQuickPrompt("Can you explain how machine learning works?")}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM13 17H11V11H13V17ZM13 9H11V7H13V9Z" fill="currentColor" />
                        </svg>
                        Machine Learning
                      </button>
                      <button
                        type="button"
                        className="prompt-button"
                        onClick={() => handleQuickPrompt("What's the best way to learn programming?")}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M20 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6C22 4.9 21.1 4 20 4ZM20 18H4V6H20V18Z" fill="currentColor" />
                          <path d="M8.5 13.5L6.5 15.5L8.5 17.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M15.5 13.5L17.5 15.5L15.5 17.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          <path d="M13 11L11 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Learn Programming
                      </button>
                      <button
                        type="button"
                        className="prompt-button"
                        onClick={() => handleQuickPrompt("Compare React vs Angular vs Vue")}
                      >
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 6H20M4 12H20M4 18H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Compare Frameworks
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Chat; 