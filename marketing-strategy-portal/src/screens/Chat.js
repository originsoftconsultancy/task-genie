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
    let accumulatedResponse = '';

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
          if (json.message && json.message.type == "text") {
            accumulatedResponse += json.message.content + '\n';
            progressCallback(accumulatedResponse);
          }
          else if (json.message && json.message.type == 'image') {
            accumulatedResponse += json.message.content + '\n';
            progressCallback(accumulatedResponse);
          }
          
          
        } catch (e) {
          console.error('Error parsing JSON from stream:', e);
        }
      }
    }

    return accumulatedResponse;
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

    // Add empty AI message immediately with a typing indicator
    const aiMessageId = messageIdCounter + 1;
    setMessages(prev => [...prev, {
      id: aiMessageId,
      text: "", // Start with empty text
      sender: "ai",
      isTyping: true // Flag to show typing indicator
    }]);
    setMessageIdCounter(prev => prev + 2);

    try {
      // Generate text response
      console.log("Generating text response...");
      await generateSingleResponse(
        newUserMessage.text,
        (accumulatedText) => {
          // Update the AI message with accumulated text in real-time
          setMessages(prev =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, text: accumulatedText, isTyping: true }
                : msg
            )
          );
        },
        'text'
      );

      // Mark message as complete (remove typing indicator)
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId
            ? { ...msg, isTyping: false }
            : msg
        )
      );

    } catch (error) {
      console.error('Error generating response:', error);

      // Update AI message to show error
      setMessages(prev =>
        prev.map(msg =>
          msg.id === aiMessageId
            ? {
              ...msg,
              text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
              isTyping: false
            }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  // Render response content with proper formatting to handle both text and images
  const renderResponseContent = (content, type) => {
    if (!content) return null;

    // Regular text formatting with line breaks, but detect and render images
    const lines = content.split('\n');
    
    return (
      <div>
        {lines.map((line, i) => {
          // Check if the line looks like an image URL (data URI or ends with image extension)
          const isImageUrl = line.startsWith('data:image') || 
                            /\.(jpeg|jpg|gif|png|webp|svg)(\?.*)?$/i.test(line) ||
                            line.includes('image');
          
          if (isImageUrl) {
            // Render as an image
            return (
              <div key={i} className="">
                <img src={line} alt="Generated content" className="chat-image" style={{width: '80%', margin: '20px 0px'}}/>
              </div>
            );
          } else {
            // Render as text
            return (
              <React.Fragment key={i}>
                {line}
                {i < lines.length - 1 && <br />}
              </React.Fragment>
            );
          }
        })}
      </div>
    );
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
                        ? renderResponseContent(message.text, message.type)
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