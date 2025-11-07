# Frontend Setup Guide

## 🎨 React Frontend for KSU IT RAG Chatbot

A modern, responsive React frontend with a beautiful chat interface.

## ✨ Features

- 🎨 **Modern UI Design**: Clean, professional interface with KSU brand colors
- 💬 **Real-time Chat**: Smooth chat interface with message history
- 📚 **Source Citations**: Beautiful display of source URLs with links
- 🎯 **Example Questions**: Sidebar with quick-start questions
- 📱 **Responsive**: Works perfectly on desktop, tablet, and mobile
- ⚡ **Fast & Smooth**: Optimized animations and transitions
- 🎨 **Markdown Support**: Rich text formatting in bot responses

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Running Development Server

```bash
npm start
```

The app will automatically open at http://localhost:3000

### Building for Production

```bash
npm run build
```

This creates an optimized production build in the `build/` folder.

## 🎨 Adding KSU Logo

1. **Save your logo file** to `frontend/public/ksu-logo.png`
   - Supported formats: PNG, SVG, JPG
   - Recommended size: 200x200px or larger

2. **Update Header component** (`frontend/src/components/Header.js`):
   
   Replace this section:
   ```jsx
   <div className="logo-placeholder">
     <span className="logo-text">KSU</span>
   </div>
   ```
   
   With:
   ```jsx
   <img 
     src="/ksu-logo.png" 
     alt="Kennesaw State University Logo" 
     className="ksu-logo"
   />
   ```

3. **Add CSS** in `frontend/src/components/Header.css`:
   ```css
   .ksu-logo {
     width: 50px;
     height: 50px;
     object-fit: contain;
   }
   ```

## 📁 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── ksu-logo.png (add your logo here)
├── src/
│   ├── components/
│   │   ├── ChatInterface.js    # Main chat component
│   │   ├── Header.js           # Top header with logo
│   │   ├── Sidebar.js          # Example questions sidebar
│   │   ├── Message.js          # Individual message component
│   │   └── InputArea.js        # Message input area
│   ├── App.js                  # Main app component
│   ├── App.css                 # App styles
│   ├── index.js                # Entry point
│   └── index.css               # Global styles
└── package.json
```

## 🎨 Design Features

### Color Scheme
- **Primary Blue**: `#003057` (KSU Blue)
- **Accent Gold**: `#FFC72C` (KSU Gold)
- **Background**: Clean white with subtle gradients
- **Messages**: Distinct styling for user vs bot messages

### Components

1. **Header**
   - KSU logo and branding
   - Online status indicator
   - Mobile-responsive menu button

2. **Chat Interface**
   - Message bubbles with avatars
   - Markdown rendering for rich text
   - Source citations with clickable links
   - Smooth scrolling and animations

3. **Sidebar**
   - Example questions for quick start
   - About section
   - Mobile-friendly overlay

4. **Input Area**
   - Auto-resizing textarea
   - Send button with loading state
   - Keyboard shortcuts (Enter to send)

## 🔧 Configuration

### API Endpoint

The frontend is configured to connect to the backend API at:
- Development: `http://localhost:8000` (via proxy in package.json)
- Production: Update `API_URL` in components if needed

### Customization

You can customize:
- Colors in `src/index.css` (CSS variables)
- Component styles in individual CSS files
- Example questions in `Sidebar.js`
- Welcome message in `ChatInterface.js`

## 📱 Responsive Design

The frontend is fully responsive:
- **Desktop**: Full sidebar, wide chat area
- **Tablet**: Collapsible sidebar, optimized layout
- **Mobile**: Overlay sidebar, compact design

## 🐛 Troubleshooting

### Frontend won't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify proxy configuration in package.json

### Logo not showing
- Check file path: `frontend/public/ksu-logo.png`
- Verify image format is supported
- Check browser console for errors

### Styling issues
- Clear browser cache
- Restart development server
- Check CSS file imports

## 🎯 For Presentation

The frontend is designed to be:
- **Visually Impressive**: Modern, clean design
- **Professional**: KSU branding and colors
- **Functional**: Smooth interactions and animations
- **Demo-Ready**: Easy to show live during presentation

---

**Ready to use!** Just add your KSU logo and start the development server.

