import React from 'react';
import { FiX, FiHelpCircle, FiInfo } from 'react-icons/fi';
import './Sidebar.css';

const Sidebar = ({ isOpen, onClose }) => {
  const exampleQuestions = [
    "How do I reset my KSU password?",
    "What are the IT department admission requirements?",
    "How do I connect to KSU Wi-Fi?",
    "What courses are offered in the IT program?",
    "How do I contact the IT service desk?",
    "What software is available for students?",
  ];

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}
      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <h2>Quick Help</h2>
          <button className="close-button" onClick={onClose} aria-label="Close sidebar">
            <FiX size={20} />
          </button>
        </div>
        
        <div className="sidebar-content">
          <section className="sidebar-section">
            <h3 className="section-title">
              <FiHelpCircle size={18} />
              Example Questions
            </h3>
            <div className="example-questions">
              {exampleQuestions.map((question, index) => (
                <button
                  key={index}
                  className="example-question"
                  onClick={() => {
                    // This will be handled by parent component
                    window.dispatchEvent(new CustomEvent('exampleQuestion', { detail: question }));
                    onClose();
                  }}
                >
                  {question}
                </button>
              ))}
            </div>
          </section>
          
          <section className="sidebar-section">
            <h3 className="section-title">
              <FiInfo size={18} />
              About
            </h3>
            <div className="about-content">
              <p>
                This chatbot helps KSU IT Department students find answers to questions 
                about IT services, programs, and resources.
              </p>
              <p>
                All answers are based on official KSU documentation and include source citations.
              </p>
            </div>
          </section>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;

