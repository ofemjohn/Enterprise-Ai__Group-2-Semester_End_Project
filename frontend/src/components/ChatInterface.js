import React, { useState, useRef, useEffect } from 'react';
import { BsRobot } from 'react-icons/bs';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Message from './Message';
import InputArea from './InputArea';
import './ChatInterface.css';

const ChatInterface = () => {
  // Generate a unique conversation ID for this session
  const [conversationId] = useState(() => {
    // Generate a simple ID (in production, use a proper UUID library)
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  });
  
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: "Hello! I'm the KSU IT Chatbot. I can help you find information about IT services, courses, admission requirements, and more. What would you like to know?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Listen for example questions from sidebar
  useEffect(() => {
    const handleExampleQuestion = (event) => {
      setInput(event.detail);
      inputRef.current?.focus();
    };

    window.addEventListener('exampleQuestion', handleExampleQuestion);
    return () => window.removeEventListener('exampleQuestion', handleExampleQuestion);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/v1/chat', {
        message: userMessage.content,
        conversation_id: conversationId, // Send conversation ID to maintain context
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.data.answer,
        sources: response.data.sources || [],
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Sorry, I encountered an error. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: 'Sorry, I encountered an error processing your request. Please try again or rephrase your question.',
        isError: true,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-messages">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        {isLoading && (
          <div className="message message-bot loading-message">
            <div className="message-avatar">
              <BsRobot size={20} />
            </div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <InputArea
        input={input}
        setInput={setInput}
        onSend={handleSend}
        onKeyPress={handleKeyPress}
        isLoading={isLoading}
        inputRef={inputRef}
      />
    </div>
  );
};

export default ChatInterface;

