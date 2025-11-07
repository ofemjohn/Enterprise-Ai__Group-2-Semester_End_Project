# KSU IT Department RAG Chatbot - Report Template

**Course**: [Course Name]  
**Group**: 2  
**Members**: John Ofem, Kamran Hall, Lhakpa Sherpa, Namita Velagapudi  
**Date**: [Submission Date]

---

## Table of Contributions

| Member | Contribution Area | Key Responsibilities |
|--------|------------------|---------------------|
| John Ofem | Data Collection & Processing | Web crawler development, data pipeline, embedding setup |
| Kamran Hall | Frontend Development | React interface, UI/UX design, user interaction |
| Lhakpa Sherpa | RAG Pipeline & Backend | LLM integration, retrieval system, API development |
| Namita Velagapudi | Testing & Documentation | Test cases, evaluation, report coordination, analysis |

*Note: All members contributed to all aspects of the project, with primary ownership as indicated above.*

---

## 1. Executive Summary

[~300 words]

**Template Points:**
- Brief overview of the project (KSU IT RAG Chatbot)
- Problem being solved (students need quick access to IT department information)
- Approach taken (RAG system with web crawling, embeddings, vector search, LLM)
- Key findings (accuracy, limitations, ethical considerations)
- Main conclusion

**Example Opening:**
> This project presents a Retrieval-Augmented Generation (RAG) chatbot designed to assist students in the Kennesaw State University IT Department by providing accurate, source-cited answers to questions about IT services, programs, and resources. The system combines web crawling, semantic search, and large language models to deliver contextual responses with verifiable citations...

---

## 2. Introduction & Problem Statement

[~600-800 words]

### 2.1 Problem Definition
- Students in KSU IT Department struggle to find information quickly
- Official documentation is scattered across multiple websites
- IT support staff are overwhelmed with repetitive questions
- Need for 24/7 accessible information source

### 2.2 Significance
- Improves student experience and self-service capability
- Reduces burden on IT support staff
- Demonstrates practical application of LLMs in enterprise IT
- Addresses information retrieval challenges

### 2.3 Why LLMs?
- Natural language understanding for student queries
- Ability to synthesize information from multiple sources
- Provides conversational interface
- Can cite sources for accountability

### 2.4 Challenges Addressed
- Information accuracy and verifiability
- Hallucination prevention through RAG
- Source attribution
- Privacy and data security

---

## 3. Proposed Solution / System Overview

[~800-1000 words]

### 3.1 System Architecture

```
┌─────────────┐
│   Student   │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  React Frontend │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  FastAPI Backend│
└──────┬──────────┘
       │
       ▼
┌─────────────────┐      ┌──────────────┐
│  RAG Service    │◄────►│ Vector DB    │
│  - Retrieval    │      │  (Pinecone)  │
│  - Generation   │      │  (Cloud)     │
└─────────────────┘      └──────────────┘
       │
       ▼
┌─────────────────┐
│  LLM (HF/OpenAI)│
└─────────────────┘
```

### 3.2 Components

1. **Data Collection Layer**
   - Web crawler using Playwright
   - Text extraction with Trafilatura
   - Domain filtering (campus.kennesaw.edu, www.kennesaw.edu, bookstore.kennesaw.edu)
   - Sequential processing to avoid over-crawling
   - URL filtering to skip filter/query parameter pages

2. **Data Processing Layer**
   - Text chunking
   - Embedding generation (Hugging Face)
   - Vector database storage

3. **RAG Pipeline**
   - Query embedding
   - Semantic search
   - Context retrieval
   - LLM generation with citations

4. **API Layer**
   - RESTful endpoints
   - Chat interface
   - Error handling

5. **Frontend**
   - React-based chat interface
   - Source citation display
   - Responsive design

### 3.3 How It Solves the Problem
- Provides instant access to IT department information
- Reduces need for manual search
- Cites sources for verification
- Available 24/7
- Natural language interface

---

## 4. Design & Methodology

[~1000-1200 words]

### 4.1 Technology Stack

**Backend:**
- FastAPI (Python web framework)
- Hugging Face Transformers (embeddings)
- Pinecone (cloud vector database for team collaboration)
- Playwright (web scraping)

**Frontend:**
- React (JavaScript framework)
- Axios (API client)
- CSS/Modern UI libraries

**AI/ML:**
- Sentence Transformers (embedding model)
- OpenAI GPT or Hugging Face LLM

### 4.2 Development Process

1. **Phase 1: Data Collection**
   - Developed web crawler using Playwright and Trafilatura
   - Implemented BFS-based crawling with depth control (max depth 2)
   - Sequential processing of entry points to ensure data persistence
   - URL filtering to avoid crawling filter/query parameter combinations
   - Extracted content from KSU IT websites and processed into JSONL format
   
   **Crawling Results:**
   - **Total pages visited**: 1,671
   - **Successfully extracted**: 1,423 pages
   - **Errors**: 200 (mostly PDF downloads and timeouts)
   - **Output file**: `data/raw/kennesaw_uits.jsonl` (1,423 records)
   
   **Data Sources Captured:**
   - **IT Department Website** (www.kennesaw.edu/ccse/academics/information-technology/): 
     - Programs (BS in IT, BAS in IT, MS in IT, MS in Cybersecurity)
     - Course information and descriptions
     - Admission requirements (undergraduate and graduate)
     - Student resources and academic advising information
     - Faculty information and research areas
     - Department news and updates
   - **ServiceNow Knowledge Base**: 3 IT support articles
   - **UITS Main Hub** (campus.kennesaw.edu/offices-services/uits/):
     - Technology guides (WiFi setup, software downloads, NetID, Duo MFA)
     - IT services and project request information
     - Security resources and cybersecurity awareness
     - AI resources and guidelines
     - Training and consulting services
   - **Bookstore Day One Access**: Information about technology access programs
   - **External Resources**: Turnitin FAQ and other IT-related documentation
   
   **Crawling Strategy:**
   - Depth 0: Single pages/documents (PDFs)
   - Depth 1: Main page + direct links (self-contained content)
   - Depth 2: Main page + service pages + detail pages (comprehensive coverage)
   - Filtered out query parameter URLs (color, size, display filters) to prevent crawling thousands of unnecessary pages

2. **Phase 2: Data Processing**
   - Text chunking strategy
   - Embedding generation
   - Vector database indexing

3. **Phase 3: RAG Implementation**
   - Semantic search implementation
   - Context retrieval
   - Prompt engineering
   - Response generation

4. **Phase 4: API Development**
   - FastAPI endpoint design
   - Request/response schemas
   - Error handling

5. **Phase 5: Frontend Development**
   - React component design
   - API integration
   - UI/UX implementation

### 4.3 Key Design Decisions

- **RAG over Fine-tuning**: Chosen for source citation and updatability
- **Vector Database**: Pinecone (cloud-based) for team collaboration and scalability
- **Embedding Model**: Sentence-BERT (all-MiniLM-L6-v2) for semantic search
- **Chunking Strategy**: Overlapping chunks for context preservation

### 4.4 Workflow Diagrams

[Include actual diagrams here]

### 4.5 Code Examples

[Include key code snippets in appendix, reference here]

---

## 5. Testing / Simulation & Results

[~800-1000 words]

### 5.1 Testing Methodology

**Test Questions Created:**
1. "How do I reset my KSU password?"
2. "What IT services are available for students?"
3. "How do I access my student email?"
4. "What software is available through the IT department?"
5. [Add more test questions]

### 5.2 Test Results

| Question | Response Accuracy | Source Quality | Response Time |
|----------|------------------|----------------|---------------|
| Q1 | ✅ Accurate | 3 sources | 2.3s |
| Q2 | ✅ Accurate | 5 sources | 1.8s |
| Q3 | ✅ Accurate | 2 sources | 2.1s |
| Q4 | ⚠️ Partially accurate | 4 sources | 2.5s |
| ... | ... | ... | ... |

### 5.3 Example Interactions

**Example 1: Password Reset**
- **User Query**: "How do I reset my password?"
- **System Response**: [Include actual response]
- **Sources**: [List sources]
- **Analysis**: Response was accurate and cited official KSU resources.

### 5.4 Performance Metrics

- Average response time: [X] seconds
- Accuracy rate: [X]%
- Source citation rate: [X]%
- User satisfaction: [If measured]

### 5.5 Observations

- Strengths: [List observed strengths]
- Weaknesses: [List observed weaknesses]
- Edge cases: [Document edge cases]

---

## 6. Analysis: Strengths, Limitations, and Ethical Considerations

[~600-800 words]

### 6.1 Strengths

1. **Accuracy through RAG**
   - Grounded in actual KSU documentation
   - Source citations enable verification
   - Reduces hallucination risk

2. **Scalability**
   - Can add new documents easily
   - Vector search is efficient
   - API-based architecture

3. **User Experience**
   - Natural language interface
   - Quick responses
   - Source transparency

### 6.2 Limitations

1. **Data Dependency**
   - Only as good as crawled data
   - May miss recent updates
   - Limited to public websites

2. **LLM Limitations**
   - Potential for hallucination even with RAG
   - May misinterpret complex queries
   - Language limitations

3. **Technical Constraints**
   - Requires internet connection
   - API costs (if using paid services)
   - Response time variability

4. **Scope Limitations**
   - Only covers publicly available information
   - Cannot access student-specific data
   - Limited to IT department resources

### 6.3 Ethical Considerations

1. **Accuracy and Reliability**
   - Risk of providing incorrect information
   - Need for clear disclaimers
   - Regular updates required

2. **Privacy**
   - User queries may contain sensitive information
   - Logging and data retention policies
   - Compliance with FERPA (if applicable)

3. **Bias**
   - Training data bias
   - Potential for discriminatory responses
   - Need for bias testing

4. **Transparency**
   - Source citation improves transparency
   - Clear indication of AI-generated content
   - Limitations clearly communicated

5. **Accessibility**
   - Ensuring all students can access
   - Language barriers
   - Disability accommodations

### 6.4 Recommendations

- Implement regular data updates
- Add user feedback mechanism
- Conduct bias audits
- Establish clear privacy policies
- Provide fallback to human support

---

## 7. Reflection & Future Scope

[~400-600 words]

### 7.1 Group Learning

- **Technical Skills**: Learned about RAG, vector databases, LLM integration
- **Collaboration**: Distributed development, version control, team coordination
- **Problem-Solving**: Iterative development, debugging, optimization
- **Enterprise AI**: Understanding real-world AI application challenges

### 7.2 Key Insights

- RAG is powerful but requires careful implementation
- Source citation is crucial for trust
- Data quality determines system quality
- User experience matters as much as accuracy

### 7.3 Challenges Overcome

- Integration of multiple technologies
- Balancing accuracy with response time
- Managing API costs
- Coordinating team contributions

### 7.4 Future Improvements

1. **Enhanced Retrieval**
   - Fine-tuned embedding models
   - Better chunking strategies
   - Multi-modal support (images, PDFs)

2. **Improved Generation**
   - Better prompt engineering
   - Fine-tuned models for domain
   - Multi-turn conversation support

3. **User Features**
   - User feedback mechanism
   - Query history
   - Personalized responses

4. **Enterprise Features**
   - Authentication/authorization
   - Analytics dashboard
   - Admin interface for content management
   - Multi-language support

5. **Deployment**
   - Production deployment
   - Scalability improvements
   - Monitoring and logging
   - CI/CD pipeline

### 7.5 Conclusion

[Summarize the project's value, lessons learned, and potential impact]

---

## 8. References

[Minimum 4 scholarly/industry references, ≤5 years old, APA 7th edition]

Example format:
```
Author, A. A. (Year). Title of article. *Journal Name*, *Volume*(Issue), pages. https://doi.org/xx.xxx/yyyy

Company Name. (Year). *Title of report*. Retrieved from https://example.com
```

**Suggested References:**
- Recent papers on RAG (2020-2024)
- LLM applications in enterprise IT
- Vector database comparisons
- Ethical AI in education

---

## 9. Appendix

### A. Sample Code
- Web crawler implementation
- RAG service code
- API endpoint examples
- Frontend components

### B. Detailed Prompts
- LLM prompt templates
- System prompts
- User query examples

### C. Additional Visuals
- Screenshots of system
- Architecture diagrams
- Test results visualizations
- UI mockups

### D. Data Samples
- Sample crawled data (1,423 pages from 13 entry points)
- Data collection statistics:
  - IT Department pages: ~1,200 pages
  - UITS service pages: ~83 pages
  - Knowledge base articles: 3 pages
  - Other resources: ~137 pages
- Embedding examples
- Query-response pairs

---

## Word Count Tracking

- Title Page: (not counted)
- Executive Summary: ~300 words
- Introduction: ~600-800 words
- Proposed Solution: ~800-1000 words
- Design & Methodology: ~1000-1200 words
- Testing & Results: ~800-1000 words
- Analysis: ~600-800 words
- Reflection: ~400-600 words
- References: (not counted)
- Appendix: (not counted)

**Total Target: 4,000-4,800 words**

