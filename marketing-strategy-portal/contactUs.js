import React, { useState, useRef, useEffect } from 'react';
import './ContactUs.css'; // You'll need to create this CSS file

const ContactUs = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        message: ''
    });
    
    const [chatHistory, setChatHistory] = useState([]);
    const [currentMessage, setCurrentMessage] = useState('');
    const [isGenerating, setIsGenerating] = useState(false);
    const [alternativeResponses, setAlternativeResponses] = useState([]);
    const [showResponseSelection, setShowResponseSelection] = useState(false);
    
    const chatContainerRef = useRef(null);

    // Scroll to bottom of chat when history changes
    useEffect(() => {
        if (chatContainerRef.current) {
            chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
        }
    }, [chatHistory, alternativeResponses]);

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData({
            ...formData,
            [name]: value
        });
    };

    const handleFormSubmit = (e) => {
        e.preventDefault();
        // Handle regular contact form submission
        console.log('Form submitted:', formData);
    };

    const handleMessageChange = (e) => {
        setCurrentMessage(e.target.value);
    };

    const handleSendMessage = async () => {
        if (!currentMessage.trim()) return;
        
        // Add user message to chat
        const userMessage = { sender: 'user', text: currentMessage };
        setChatHistory([...chatHistory, userMessage]);
        setCurrentMessage('');
        setIsGenerating(true);
        
        try {
            // Simulate generating two responses
            // In a real implementation, this would be an API call to your backend
            const responses = await generateResponses(currentMessage, chatHistory);
            setAlternativeResponses(responses);
            setShowResponseSelection(true);
        } catch (error) {
            console.error("Failed to generate responses:", error);
            setChatHistory([
                ...chatHistory, 
                userMessage,
                { sender: 'assistant', text: "Sorry, I couldn't generate a response. Please try again." }
            ]);
        } finally {
            setIsGenerating(false);
        }
    };

    // This function simulates the backend call to generate responses
    // In a real implementation, this would call your API
    const generateResponses = async (message, history) => {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Mock responses - replace with actual API call
        return [
            `Response 1/2:\n\nThank you for your message! I'd be happy to help with your inquiry about our services. Could you please provide more details?`,
            `Response 2/2:\n\nI've received your message and I'm ready to assist. Our team specializes in solving problems like yours. What specific information are you looking for?`
        ];
    };

    const selectResponse = (responseIndex) => {
        const selectedResponse = { 
            sender: 'assistant', 
            text: alternativeResponses[responseIndex].replace(/^Response \d\/2:\n\n/, '') 
        };
        
        setChatHistory([...chatHistory, selectedResponse]);
        setAlternativeResponses([]);
        setShowResponseSelection(false);
    };

    return (
        <div className="contact-us-container">
            <h1>Contact Us</h1>
            
            <div className="contact-sections">
                {/* Contact Form Section */}
                <div className="contact-form-section">
                    <h2>Send us a message</h2>
                    <form onSubmit={handleFormSubmit}>
                        <div className="form-group">
                            <label>Name:</label>
                            <input
                                type="text"
                                name="name"
                                value={formData.name}
                                onChange={handleFormChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Email:</label>
                            <input
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleFormChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Message:</label>
                            <textarea
                                name="message"
                                value={formData.message}
                                onChange={handleFormChange}
                                required
                            />
                        </div>
                        <button type="submit">Submit</button>
                    </form>
                </div>
                
                {/* Chat Section */}
                <div className="chat-section">
                    <h2>Chat with Me</h2>
                    <div className="chat-container" ref={chatContainerRef}>
                        {/* Display chat history */}
                        {chatHistory.map((msg, index) => (
                            <div 
                                key={index} 
                                className={`chat-message ${msg.sender === 'user' ? 'user-message' : 'assistant-message'}`}
                            >
                                <div className="message-bubble">
                                    {msg.text}
                                </div>
                            </div>
                        ))}
                        
                        {/* Display loading indicator */}
                        {isGenerating && (
                            <div className="chat-message assistant-message">
                                <div className="message-bubble loading">
                                    Generating responses...
                                </div>
                            </div>
                        )}
                        
                        {/* Display alternative responses for selection */}
                        {showResponseSelection && (
                            <div className="response-alternatives">
                                <div className="response-prompt">Please select a response:</div>
                                {alternativeResponses.map((response, index) => (
                                    <div 
                                        key={index} 
                                        className="response-option"
                                        onClick={() => selectResponse(index)}
                                    >
                                        {response}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                    
                    {/* Message input */}
                    <div className="chat-input-container">
                        <input
                            type="text"
                            value={currentMessage}
                            onChange={handleMessageChange}
                            placeholder="Type your message here..."
                            disabled={isGenerating || showResponseSelection}
                        />
                        <button 
                            onClick={handleSendMessage}
                            disabled={isGenerating || showResponseSelection || !currentMessage.trim()}
                        >
                            Send
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ContactUs; 