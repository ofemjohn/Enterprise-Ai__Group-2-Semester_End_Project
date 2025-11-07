# KSU IT RAG Chatbot - Frontend

Modern React frontend for the KSU IT RAG Chatbot application.

## Features

- 🎨 Modern, responsive UI design
- 💬 Real-time chat interface
- 📚 Source citations display
- 🎯 Example questions sidebar
- 📱 Mobile-friendly design
- ⚡ Fast and smooth animations
- 🎨 KSU brand colors and styling

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm start
```

The app will open at http://localhost:3000

### Building for Production

```bash
npm run build
```

## Adding KSU Logo

Replace the logo placeholder in `src/components/Header.js`:

1. Add your logo file to `public/ksu-logo.png`
2. Update the Header component:

```jsx
<img src="/ksu-logo.png" alt="KSU Logo" className="ksu-logo" />
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── ChatInterface.js
│   │   ├── Header.js
│   │   ├── InputArea.js
│   │   ├── Message.js
│   │   └── Sidebar.js
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

