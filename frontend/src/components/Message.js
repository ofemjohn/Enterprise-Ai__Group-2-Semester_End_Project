import React, { useState } from 'react';
import { BsRobot, BsPerson } from 'react-icons/bs';
import { FiExternalLink, FiCopy, FiCheck } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Message.css';

const Message = ({ message }) => {
  const [copied, setCopied] = useState(false);
  const isUser = message.type === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-bot'} ${message.isError ? 'message-error' : ''}`}>
      <div className="message-avatar">
        {isUser ? <BsPerson size={20} /> : <BsRobot size={20} />}
      </div>
      <div className="message-content-wrapper">
        <div className="message-content">
          {!isUser && !message.isError ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              className="markdown-content"
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <p>{message.content}</p>
          )}
        </div>
        
        {message.sources && message.sources.length > 0 && (
          <div className="message-sources">
            <div className="sources-header">
              <span className="sources-title">Sources:</span>
              <button
                className="copy-button"
                onClick={handleCopy}
                title="Copy answer"
              >
                {copied ? <FiCheck size={14} /> : <FiCopy size={14} />}
              </button>
            </div>
            <div className="sources-list">
              {message.sources.map((source, index) => (
                <a
                  key={index}
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                >
                  <FiExternalLink size={14} />
                  <span className="source-url">{source.url}</span>
                </a>
              ))}
            </div>
          </div>
        )}
        
        <div className="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
};

export default Message;

