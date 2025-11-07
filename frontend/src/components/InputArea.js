import React from 'react';
import { FiSend } from 'react-icons/fi';
import { AiOutlineLoading3Quarters } from 'react-icons/ai';
import './InputArea.css';

const InputArea = ({ input, setInput, onSend, onKeyPress, isLoading, inputRef }) => {
  // Auto-resize textarea
  const handleChange = (e) => {
    setInput(e.target.value);
    // Auto-resize
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 150)}px`;
    }
  };

  return (
    <div className="input-area">
      <div className="input-container">
        <textarea
          ref={inputRef}
          value={input}
          onChange={handleChange}
          onKeyPress={onKeyPress}
          placeholder="Ask me anything about KSU IT services, courses, or resources..."
          className="input-field"
          rows={1}
          disabled={isLoading}
        />
        <button
          onClick={onSend}
          disabled={!input.trim() || isLoading}
          className="send-button"
          aria-label="Send message"
        >
          {isLoading ? (
            <AiOutlineLoading3Quarters size={20} className="spinner" />
          ) : (
            <FiSend size={20} />
          )}
        </button>
      </div>
      <div className="input-footer">
        <p className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};

export default InputArea;

