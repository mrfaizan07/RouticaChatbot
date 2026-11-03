# Routica AI Chatbot Frontend

A premium, enterprise-level AI chatbot frontend built with React, Vite, Tailwind CSS, and Lucide React, fully integrated with the Routica FastAPI RAG backend.

## Technology Stack

- **Framework:** React 18 + Vite
- **Styling:** Tailwind CSS + PostCSS + Autoprefixer
- **Icons:** Lucide React
- **Animations:** Framer Motion
- **Security:** DOMPurify (HTML sanitization)
- **Streaming:** Native `fetch` + `ReadableStream` with robust SSE buffer parser
- **Testing:** Vitest + React Testing Library + JSDOM

## Features

- **Single Minimalist Page:** Minimalist enterprise landing page with Routica branding.
- **Floating Chatbot Launcher:** Responsive floating widget in bottom-right corner.
- **Real-Time SSE Streaming:** Progressive token rendering with event boundaries (`status`, `sources`, `token`, `complete`, `error`).
- **Grounded Source Citations:** Interactive source reference pills with direct external links, relevance scores, and previews.
- **Safe Markdown Rendering:** Formatted code blocks, tables, lists, bold/italics, and blockquotes with DOMPurify sanitization.
- **Full-Screen Mobile Adaptation:** Smooth transition from floating window on desktop to full-screen sheet on mobile.
- **Smart Auto-Scroll:** Automatically follows streaming tokens unless user manually scrolls up.
- **Session Continuity:** Non-persistent session management using `sessionStorage` and `X-Session-ID` headers.

## Getting Started

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Ensure `VITE_API_BASE_URL` points to your active FastAPI backend (e.g. `http://localhost:8000` or production Render URL).

### 3. Run Development Server
```bash
npm run dev
```

### 4. Build for Production
```bash
npm run build
```

### 5. Run Tests
```bash
npm test
npm run test:e2e
```

