# Routica AI Assistant & Admin Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4+-06B6D4?style=flat&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas%20Vector%20Search-47A248?style=flat&logo=mongodb&logoColor=white)](https://mongodb.com)

A high-performance, enterprise-grade AI chatbot and administration dashboard for **Routica**. Provides RAG-powered customer intelligence, real-time token streaming, automated multi-turn web scraping, Excel/JSON knowledge ingestion, and full vector search retrieval.

---

## Key Features

- **Conversational RAG Engine:** Answers customer queries using verified knowledge documents and Routica product catalogs.
- **Strict Anti-Hallucination & Clean Output:** Clean, concise bullet-point responses with direct source citations and no raw markdown table clutter.
- **Multi-Model LLM Resilience:** Primary inference powered by Groq (`llama-3.3-70b-versatile`) with automatic fallback to Gemini (`gemini-1.5-flash`) or OpenRouter.
- **Minimalist Admin Dashboard:**
  - Secure JWT authentication (`/admin`).
  - Document ingestion supporting Excel (`.xlsx`, `.xls`) and `.json` datasets.
  - Live vector embedding generation and indexing.
  - Scraper configuration and trigger controls.
  - Chat analytics, conversation history inspection, and latency metrics.
- **Render Ready:** Pre-configured `render.yaml` Blueprint with automatic zero-CORS configuration, dynamic `$PORT` binding, and static SPA routing rewrites.

---

## Architecture Overview

```
Routicabot/
├── backend/
│   ├── app/
│   │   ├── api/v1/         # Endpoints: auth, chat, documents, scraper, analytics
│   │   ├── core/           # Security, auth, hashing, rate limiting
│   │   ├── models/         # Pydantic schemas and database models
│   │   ├── services/       # RAG, LLM router, embeddings, vector search, scraper
│   │   ├── config.py       # Pydantic BaseSettings with dynamic $PORT & CORS
│   │   └── main.py         # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── tests/              # Backend test suites
├── frontend/
│   ├── src/
│   │   ├── components/     # Chatbot, Header, Admin Dashboard, Analytics
│   │   ├── hooks/          # useStreamingChat, useAuth, useDocuments
│   │   ├── services/       # Axios API client with dynamic base URL
│   │   └── config/         # App constants and configuration
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite build configuration
├── render.yaml             # Render infrastructure Blueprint
├── .env.example            # Environment template (safe for public repos)
└── requirements.txt        # Root requirements for Render Python builds
```

---

## Quick Start (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- MongoDB Atlas cluster (with Vector Search index configured)

### 2. Backend Setup
```bash
# Navigate to backend or workspace root
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp ../.env.example .env
# Edit .env with your MONGODB_URI and GROQ_API_KEY / GEMINI_API_KEY

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Set VITE_API_BASE_URL=http://localhost:8000

# Start Vite dev server
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser. Access the Admin Panel at [http://localhost:5173/#admin](http://localhost:5173/#admin).

---

## Render Deployment Guide

The repository includes a ready-to-use [`render.yaml`](render.yaml) file for one-click deployment using Render Blueprints.

### Option A: Automatic Deployment via Render Blueprint (Recommended)
1. Push this repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Connect your `mrfaizan07/RouticaChatbot` repository.
5. Render will automatically detect `render.yaml` and configure:
   - **Backend Web Service:** `routica-ai-backend` (Python)
   - **Frontend Static Site:** `routica-ai-frontend` (React/Vite with SPA rewrite rule `/* -> /index.html`)
6. Fill in the required secret environment variables prompted by Render:
   - `MONGODB_URI`
   - `GROQ_API_KEY` (or `GEMINI_API_KEY`)
   - `SECRET_KEY` & `JWT_SECRET_KEY`
   - `ADMIN_PASSWORD`
7. Click **Apply**. Once built, copy your backend URL and add `VITE_API_BASE_URL` to your frontend environment variables.

---

### Option B: Manual Service Creation on Render

#### Backend (Web Service)
- **Environment:** Python
- **Root Directory:** (leave empty or set to `backend`)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  - `PORT`: `10000` (automatically set by Render)
  - `HOST`: `0.0.0.0`
  - `APP_ENV`: `production`
  - `DEBUG`: `false`
  - `MONGODB_URI`: `mongodb+srv://...`
  - `MONGODB_DATABASE`: `routica_chatbot`
  - `GROQ_API_KEY`: `gsk_...`
  - `GEMINI_API_KEY`: `...`
  - `SECRET_KEY`: `<generate-a-random-32-char-string>`
  - `JWT_SECRET_KEY`: `<generate-a-random-32-char-string>`
  - `ADMIN_USERNAME`: `admin`
  - `ADMIN_PASSWORD`: `<your-admin-password>`
  - `FRONTEND_URL`: `https://your-frontend-subdomain.onrender.com`

#### Frontend (Static Site)
- **Root Directory:** `frontend`
- **Build Command:** `npm install && npm run build`
- **Publish Directory:** `dist`
- **Environment Variables:**
  - `VITE_API_BASE_URL`: `https://your-backend-subdomain.onrender.com`
- **Redirects / Rewrites:**
  - Type: `Rewrite`
  - Source: `/*`
  - Destination: `/index.html`

---

## Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `MONGODB_URI` | MongoDB Atlas connection string | `mongodb+srv://...` |
| `MONGODB_DATABASE` | Database name | `routica_chatbot` |
| `GROQ_API_KEY` | Primary LLM API key | `gsk_...` |
| `GEMINI_API_KEY` | Secondary LLM / Embedding key | `...` |
| `SECRET_KEY` | App encryption key | Min 32 chars |
| `JWT_SECRET_KEY` | JWT signing secret | Min 32 chars |
| `ADMIN_USERNAME` | Admin panel login | `admin` |
| `ADMIN_PASSWORD` | Admin panel password | Secure password |
| `FRONTEND_URL` | Frontend origin for CORS | `https://*.onrender.com` |
| `VITE_API_BASE_URL` | Frontend API client base URL | `https://routica-ai-backend.onrender.com` |

---

## Security & Reliability

- **No Secrets in Repo:** All `.env` files and uploaded customer datasets are strictly excluded via `.gitignore`.
- **Dynamic CORS Middleware:** Secure origin validation supporting local development and all `*.onrender.com` domains automatically.
- **Preflight Safe:** Whitelisted HTTP `OPTIONS` methods avoid cross-origin preflight stalls.
- **Input Validation:** Strict MIME type, file size, and extension filtering (`.xlsx`, `.xls`, `.json`).

---

## License
Proprietary & Confidential - Designed for Routica.

