import React, { useState, useRef, useEffect } from 'react';
import Header from '../components/Header';
import CampaignShowcase from '../components/CampaignShowcase';
import './Chat.css';

/**
 * Generate a single response from Ollama
 */
const generateSingleResponse = async (message, progressCallback, format = 'text') => {
  let systemMessage = "You are a helpful assistant";
  if (format === 'table') {
    systemMessage = "You are a helpful assistant that includes your initial explanation followed by a comprehensive markdown table summarizing the key points. Use | for columns and - for row separators.";
  } else if (format === 'pdf') {
    systemMessage = "You are a helpful assistant that provides a detailed response formatted with rich markdown including headings, lists, and where appropriate, tables. This will be converted to a downloadable PDF.";
  } else {
    systemMessage = "You are a helpful assistant that responds in clear, concise text.";
  }

  const model = 'llama3.2:1b';
  const messages = [
    { "role": "system", "content": systemMessage },
    { "role": "user", "content": message }
  ];

  try {
    console.log('Sending request to local Ollama model:', message, 'format:', format);

    const response = await fetch('http://192.168.1.106:5000/process_prompt', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: message
      }),
    });

    //model: model,
    //messages: messages,
    //stream: true

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let accumulatedResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (!line) continue;

        try {
          const json = JSON.parse(line);
          if (json.message && json.message.content) {
            accumulatedResponse += json.message.content;
            progressCallback(json.message.content);
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
 * Generate all three response formats (text, table, pdf)
 */
const generateTripleResponses = async (message, progressCallbacks) => {
  try {
    // Generate first response - text
    const response1 = await generateSingleResponse(message, progressCallbacks.first || (() => { }), 'text');

    // Generate second response - table
    //const response2 = await generateSingleResponse(message, progressCallbacks.second || (() => { }), 'table');

    // Generate third response - markdown for PDF
    //const response3 = await generateSingleResponse(message, progressCallbacks.third || (() => { }), 'pdf');

    return {
      first: response1,
      //second: response2,
      //third: response3
    };
  } catch (error) {
    console.error('Error generating triple responses:', error);
    throw error;
  }
};

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
  const [currentGenerationStep, setCurrentGenerationStep] = useState(0); // 0: none, 1: text, 2: table, 3: pdf
  const [generatedResponses, setGeneratedResponses] = useState({
    text: null,
    table: null,
    pdf: null
  });
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
    setCurrentGenerationStep(1); // Start with text generation
    setGeneratedResponses({
      text: null,
      table: null,
      pdf: null
    });

    try {
      // Generate text response first
      console.log("Generating text response...");
      const textResponse = await generateSingleResponse(
        newUserMessage.text,
        (text) => {
          setGeneratedResponses(prev => ({ ...prev, text }));
        },
        'text'
      );

      // Add text response to messages
      const textMessageId = messageIdCounter + 1;
      setMessages(prev => [...prev, {
        id: textMessageId,
        text: textResponse,
        sender: "ai",
        type: "text"
      }]);
      setMessageIdCounter(prev => prev + 2);

      // Generate table response next
      setCurrentGenerationStep(2);
      console.log("Generating table response...");
      const tableResponse = await generateSingleResponse(
        newUserMessage.text,
        (text) => {
          setGeneratedResponses(prev => ({ ...prev, table: text }));
        },
        'table'
      );

      // Add table response to messages
      const tableMessageId = messageIdCounter + 3;
      setMessages(prev => [...prev, {
        id: tableMessageId,
        text: tableResponse,
        sender: "ai",
        type: "table"
      }]);
      setMessageIdCounter(prev => prev + 4);

      // Generate PDF response last
      setCurrentGenerationStep(3);
      console.log("Generating PDF response...");
      const pdfResponse = await generateSingleResponse(
        newUserMessage.text,
        (text) => {
          setGeneratedResponses(prev => ({ ...prev, pdf: text }));
        },
        'pdf'
      );

      // Create downloadable PDF (in a real app, this would convert markdown to PDF)
      // Here we'll just save the markdown as a text file as a placeholder
      const pdfBlob = new Blob([pdfResponse], { type: 'text/markdown' });
      const pdfUrl = URL.createObjectURL(pdfBlob);

      // Add PDF response message with download link
      setMessages(prev => [...prev, {
        id: messageIdCounter + 5,
        text: "I've prepared a detailed PDF document based on your query. Click the button below to download it.",
        sender: "ai",
        type: "pdf",
        pdfUrl: pdfUrl,
        fileName: `response-${Date.now()}.md`
      }]);
      setMessageIdCounter(prev => prev + 6);

      // Reset generation step
      setCurrentGenerationStep(0);

    } catch (error) {
      console.error('Error generating response:', error);

      // Add error message to chat
      setMessages(prev => [...prev, {
        id: messageIdCounter + 1,
        text: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        sender: "ai"
      }]);
      setCurrentGenerationStep(0);
    } finally {
      setLoading(false);
    }
  };

  // Render response content with proper formatting
  const renderResponseContent = (content, type) => {
    if (!content) return null;

    // Special case for PDF download button
    if (type === "pdf") {
      const message = content;
      return (
        <>
          <p>{message.text}</p>
          <div className="pdf-download">
            <a
              href={message.pdfUrl}
              download={message.fileName}
              className="pdf-download-button"
            >
              Download PDF
            </a>
          </div>
        </>
      );
    }

    // Check if the response contains table markdown
    if (content.includes('|') && content.includes('---')) {
      // Parse markdown table and render it as a formatted table
      const lines = content.split('\n');
      const tableStartIndex = lines.findIndex(line => line.includes('|') && line.includes('-'));

      if (tableStartIndex > 0) {
        // There's text before the table
        const textPart = lines.slice(0, tableStartIndex - 1).join('\n');
        const tableLines = lines.slice(tableStartIndex - 1);

        // Headers are one line before the separator
        const headers = tableLines[0].split('|').filter(cell => cell.trim());

        // Rows start after the separator
        const rows = tableLines.slice(2).map(line =>
          line.split('|').filter(cell => cell.trim())
        ).filter(row => row.length > 1); // Filter out any lines that don't look like table rows

        return (
          <>
            {/* Render text part */}
            {textPart.split('\n').map((line, i) => (
              <React.Fragment key={`text-${i}`}>
                {line}
                {i < textPart.split('\n').length - 1 && <br />}
              </React.Fragment>
            ))}

            {/* Render table part */}
            <div className="markdown-table">
              <div className="table-header">
                {headers.map((header, i) => (
                  <div key={i} className="table-cell">{header.trim()}</div>
                ))}
              </div>
              {rows.map((row, i) => (
                <div key={i} className="table-row">
                  {row.map((cell, j) => (
                    <div key={j} className="table-cell">{cell.trim()}</div>
                  ))}
                </div>
              ))}
            </div>
          </>
        );
      }
    }

    // Regular text formatting with line breaks
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
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
                        ? (message.type === "pdf"
                          ? renderResponseContent(message, "pdf")
                          : renderResponseContent(message.text, message.type))
                        : message.text
                      }
                      {message.sender === 'ai' && message.id === messages[messages.length - 1].id && loading &&
                        <span className="typing-indicator">
                          <span className="dot"></span>
                          <span className="dot"></span>
                          <span className="dot"></span>
                        </span>
                      }
                    </div>
                  ))}

                  {loading && currentGenerationStep > 0 && (
                    <div className="generation-status">
                      <div className="generation-step">
                        <div className={`step-indicator ${currentGenerationStep >= 1 ? 'active' : ''}`}>1</div>
                        <div className="step-label">Generating text response...</div>
                        {currentGenerationStep === 1 && (
                          <div className="preview-content">
                            {generatedResponses.text || (
                              <span className="typing-indicator">
                                <span className="dot"></span>
                                <span className="dot"></span>
                                <span className="dot"></span>
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="generation-step">
                        <div className={`step-indicator ${currentGenerationStep >= 2 ? 'active' : ''}`}>2</div>
                        <div className="step-label">Generating text+table response...</div>
                        {currentGenerationStep === 2 && (
                          <div className="preview-content">
                            {generatedResponses.table || (
                              <span className="typing-indicator">
                                <span className="dot"></span>
                                <span className="dot"></span>
                                <span className="dot"></span>
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="generation-step">
                        <div className={`step-indicator ${currentGenerationStep >= 3 ? 'active' : ''}`}>3</div>
                        <div className="step-label">Creating PDF document...</div>
                        {currentGenerationStep === 3 && (
                          <div className="preview-content">
                            {generatedResponses.pdf ? "PDF is ready!" : (
                              <span className="typing-indicator">
                                <span className="dot"></span>
                                <span className="dot"></span>
                                <span className="dot"></span>
                              </span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

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