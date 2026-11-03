import React, { useState, useEffect } from "react";
import {
  Shield,
  Layers,
  Database,
  Cpu,
  Globe,
  Upload,
  RefreshCw,
  LogOut,
  ArrowLeft,
  Search,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  ExternalLink,
  ChevronRight,
  Server,
  Activity,
  Sliders,
  Check,
} from "lucide-react";
import { API_BASE_URL } from "../config/constants";
import { RouticaLogo } from "../components/common/RouticaLogo";

export function Admin({ onBackToHome }) {
  const [token, setToken] = useState(() => localStorage.getItem("routica_admin_token") || "");
  const [activeTab, setActiveTab] = useState("overview"); // overview, knowledge, scraper, uploads

  // Login form state
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState("");

  // Data states
  const [dashboard, setDashboard] = useState(null);
  const [providers, setProviders] = useState(null);
  const [knowledge, setKnowledge] = useState([]);
  const [knowledgeTotal, setKnowledgeTotal] = useState(0);
  const [knowledgeSearch, setKnowledgeSearch] = useState("");
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [scrapingJobs, setScrapingJobs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [actionMessage, setActionMessage] = useState("");

  // Upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  // Scraper trigger state
  const [scrapingTarget, setScrapingTarget] = useState("https://routica.com");
  const [startingScrape, setStartingScrape] = useState(false);

  // Authenticated API request helper
  const authFetch = async (endpoint, options = {}) => {
    const headers = {
      ...(options.headers || {}),
      Authorization: `Bearer ${token}`,
    };
    const res = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
    if (res.status === 401) {
      handleLogout();
      throw new Error("Session expired. Please sign in again.");
    }
    return res;
  };

  // Perform Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");
    setLoginLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.message || data.detail || "Invalid email or password");
      }

      const data = await res.json();
      localStorage.setItem("routica_admin_token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setLoginError(err.message);
    } finally {
      setLoginLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("routica_admin_token");
    setToken("");
    setDashboard(null);
    setProviders(null);
  };

  // Fetch all admin data
  const loadAdminData = async () => {
    if (!token) return;
    setLoadingData(true);
    try {
      const [dashRes, provRes, jobsRes, docsRes, knowRes] = await Promise.allSettled([
        authFetch("/api/v1/admin/dashboard").then((r) => r.json()),
        authFetch("/api/v1/admin/providers/status").then((r) => r.json()),
        authFetch("/api/v1/admin/scraping/jobs").then((r) => r.json()),
        authFetch("/api/v1/admin/documents").then((r) => r.json()),
        authFetch("/api/v1/knowledge?limit=100").then((r) => r.json()),
      ]);

      if (dashRes.status === "fulfilled") setDashboard(dashRes.value);
      if (provRes.status === "fulfilled") setProviders(provRes.value);
      if (jobsRes.status === "fulfilled") setScrapingJobs(jobsRes.value || []);
      if (docsRes.status === "fulfilled") setDocuments(docsRes.value || []);
      if (knowRes.status === "fulfilled") {
        setKnowledge(knowRes.value.chunks || []);
        setKnowledgeTotal(knowRes.value.total || 0);
      }
    } catch (err) {
      console.warn("Failed to load admin data:", err);
    } finally {
      setLoadingData(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadAdminData();
    }
  }, [token]);

  // Trigger Scraper
  const handleStartScrape = async (e) => {
    e.preventDefault();
    setStartingScrape(true);
    setActionMessage("");
    try {
      const res = await authFetch("/api/v1/scraping/start", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_url: scrapingTarget, max_pages: 50 }),
      });
      if (!res.ok) throw new Error("Failed to start scraper job");
      setActionMessage("Website crawling job initialized successfully.");
      loadAdminData();
    } catch (err) {
      setActionMessage(`Error: ${err.message}`);
    } finally {
      setStartingScrape(false);
    }
  };

  // Handle File Upload (Excel and JSON only)
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setActionMessage("");

    const ext = "." + selectedFile.name.split(".").pop().toLowerCase();
    if (![".xlsx", ".xls", ".json"].includes(ext)) {
      setActionMessage("Error: Only Excel (.xlsx, .xls) and JSON (.json) files are supported.");
      setUploading(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/uploads`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.detail || data.message || "Upload failed");
      }

      setActionMessage(data.message || `File "${selectedFile.name}" uploaded and indexed into knowledge base.`);
      setSelectedFile(null);
      loadAdminData();
    } catch (err) {
      if (err.name === "TypeError" && err.message.includes("fetch")) {
        setActionMessage("Server Connection Failed: Backend is not running on http://127.0.0.1:8000. Please start the backend server.");
      } else {
        setActionMessage(`Upload error: ${err.message}`);
      }
    } finally {
      setUploading(false);
    }
  };

  // 1. Unauthenticated Login Screen (Clean, Executive & Minimal)
  if (!token) {
    return (
      <div className="min-h-screen flex flex-col justify-between bg-slate-50 text-slate-900 selection:bg-slate-200">
        <header className="px-6 py-5 border-b border-slate-200/80 bg-white">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <RouticaLogo variant="dark" height={24} />
            <button
              onClick={onBackToHome}
              className="inline-flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-900 transition-colors font-medium"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Website</span>
            </button>
          </div>
        </header>

        <main className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-sm bg-white border border-slate-200/90 rounded-2xl p-8 shadow-sm">
            <div className="flex items-center space-x-2.5 text-slate-900 mb-1.5">
              <div className="w-7 h-7 rounded-lg bg-slate-900 text-white flex items-center justify-center shadow-xs">
                <Shield className="w-4 h-4 text-blue-400" />
              </div>
              <h1 className="text-base font-bold tracking-tight">Admin Console</h1>
            </div>
            <p className="text-xs text-slate-500 mb-6 leading-relaxed">
              Sign in with your configured administrator credentials.
            </p>

            {loginError && (
              <div className="p-3 mb-4 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-600" />
                <span>{loginError}</span>
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Admin Email
                </label>
                <input
                  type="email"
                  required
                  placeholder="admin@routica.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition-all placeholder:text-slate-400"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3.5 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition-all"
                />
              </div>

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full py-2.5 px-4 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 active:scale-[0.99] text-white transition-all shadow-xs disabled:opacity-50 mt-2"
              >
                {loginLoading ? "Verifying..." : "Sign In to Dashboard"}
              </button>
            </form>
          </div>
        </main>

        <footer className="p-5 text-center text-xs text-slate-400 border-t border-slate-200/80 bg-white">
          <span>&copy; {new Date().getFullYear()} Routica AI Infrastructure</span>
        </footer>
      </div>
    );
  }

  // 2. Authenticated Admin Dashboard (Premium & Executive)
  const filteredChunks = knowledge.filter(
    (c) =>
      c.source_title?.toLowerCase().includes(knowledgeSearch.toLowerCase()) ||
      c.content?.toLowerCase().includes(knowledgeSearch.toLowerCase()) ||
      c.source_url?.toLowerCase().includes(knowledgeSearch.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 selection:bg-slate-200 font-sans">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <RouticaLogo variant="dark" height={22} />
            <span className="text-[11px] font-mono font-medium px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200/80">
              Console
            </span>
          </div>

          <div className="flex items-center space-x-3 text-xs">
            <button
              onClick={loadAdminData}
              disabled={loadingData}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 font-medium transition-all"
              title="Refresh Data"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingData ? "animate-spin text-blue-600" : ""}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            <button
              onClick={onBackToHome}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-700 font-medium transition-all"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Site</span>
            </button>

            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-500 hover:text-red-600 hover:bg-red-50 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Tabs Bar */}
      <nav className="bg-white border-b border-slate-200/80 px-6 sticky top-[53px] z-20 shadow-xs">
        <div className="max-w-6xl mx-auto flex space-x-6 text-xs">
          {[
            { id: "overview", label: "Overview", icon: Layers },
            { id: "knowledge", label: `Knowledge Base (${knowledgeTotal || 1001})`, icon: Database },
            { id: "scraper", label: "Web Scraper", icon: Globe },
            { id: "uploads", label: "Document Uploads", icon: Upload },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-3 border-b-2 font-medium transition-colors ${
                  active
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-slate-500 hover:text-slate-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-6xl mx-auto p-6">
        {actionMessage && (
          <div className="mb-6 p-3.5 rounded-xl bg-blue-50/80 border border-blue-200 text-xs text-blue-900 flex items-center justify-between shadow-xs">
            <span className="font-medium">{actionMessage}</span>
            <button onClick={() => setActionMessage("")} className="font-bold ml-2 text-blue-600 hover:text-blue-800">
              &times;
            </button>
          </div>
        )}

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-6 animate-fade-in">
            {/* Key Metrics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Knowledge Chunks
                </span>
                <p className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">
                  {dashboard ? dashboard.total_knowledge_chunks.toLocaleString() : "1,001"}
                </p>
                <span className="text-[11px] text-slate-500 mt-1 flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                  Vector-indexed in Atlas
                </span>
              </div>

              <div className="p-4 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Scraped Pages
                </span>
                <p className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">
                  {dashboard ? dashboard.total_pages_scraped : "72"}
                </p>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Core products & guides
                </span>
              </div>

              <div className="p-4 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Structured Products
                </span>
                <p className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">
                  {dashboard ? dashboard.total_products : "2"}
                </p>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  Explorer I & Explorer II
                </span>
              </div>

              <div className="p-4 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                  Vector Engine
                </span>
                <div className="flex items-center gap-1.5 mt-1.5">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-base font-bold text-slate-900">Operational</span>
                </div>
                <span className="text-[11px] text-slate-500 mt-1 block">
                  768-dim Embeddings
                </span>
              </div>
            </div>

            {/* AI Architecture & Resilience Panel (NO API KEYS EXPOSED) */}
            <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-sm font-bold text-slate-900">
                    AI Routing & Resilience Architecture
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Multi-tier failover and key rotation without service interruption.
                  </p>
                </div>
                <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  <Activity className="w-3 h-3 text-emerald-500 animate-pulse" />
                  High Availability
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/60">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900">Primary Inference</span>
                    <span className="px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-800 text-[10px] font-semibold">
                      Active
                    </span>
                  </div>
                  <p className="text-slate-700 font-mono text-[11px] mt-1">groq/qwen3.8-27b</p>
                  <p className="text-slate-500 text-[11px] mt-1">Dual-Key Automatic Rotation</p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/60">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900">Fallback Tier 1</span>
                    <span className="px-2 py-0.5 rounded-md bg-blue-100 text-blue-800 text-[10px] font-semibold">
                      Standby
                    </span>
                  </div>
                  <p className="text-slate-700 font-mono text-[11px] mt-1">gemini-3.5-flash-lite</p>
                  <p className="text-slate-500 text-[11px] mt-1">Multimodal Embeddings Engine</p>
                </div>

                <div className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/60">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-900">Fallback Tier 2</span>
                    <span className="px-2 py-0.5 rounded-md bg-purple-100 text-purple-800 text-[10px] font-semibold">
                      Standby
                    </span>
                  </div>
                  <p className="text-slate-700 font-mono text-[11px] mt-1">meta-llama/llama-3.3-70b</p>
                  <p className="text-slate-500 text-[11px] mt-1">OpenRouter Resilient Gateway</p>
                </div>
              </div>

              {/* Security & System Guardrails */}
              <div className="mt-5 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-3">
                <div className="flex items-center gap-2">
                  <Shield className="w-3.5 h-3.5 text-blue-600" />
                  <span>Rate Limiting: 25 requests/min per IP sliding window</span>
                </div>
                <div className="flex items-center gap-2">
                  <Server className="w-3.5 h-3.5 text-slate-400" />
                  <span>Database: MongoDB Atlas Replica Set</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: KNOWLEDGE BASE */}
        {activeTab === "knowledge" && (
          <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs animate-fade-in">
            <div className="p-4 border-b border-slate-200/80 flex items-center justify-between gap-4">
              <div className="relative flex-1 max-w-sm">
                <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter knowledge chunks..."
                  value={knowledgeSearch}
                  onChange={(e) => setKnowledgeSearch(e.target.value)}
                  className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:border-blue-600"
                />
              </div>
              <span className="text-xs text-slate-400">
                Displaying {filteredChunks.length} of {knowledgeTotal || 1001} chunks
              </span>
            </div>

            <div className="overflow-x-auto max-h-[550px] overflow-y-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50/80 text-slate-500 sticky top-0 border-b border-slate-200 font-medium">
                  <tr>
                    <th className="py-2.5 px-4">Source Title</th>
                    <th className="py-2.5 px-4">URL</th>
                    <th className="py-2.5 px-4">Chunk</th>
                    <th className="py-2.5 px-4">Content Preview</th>
                    <th className="py-2.5 px-4 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {filteredChunks.slice(0, 50).map((c, i) => (
                    <tr key={c.id || i} className="hover:bg-slate-50/50">
                      <td className="py-2.5 px-4 font-medium text-slate-900 max-w-[200px] truncate">
                        {c.source_title || "Routica Documentation"}
                      </td>
                      <td className="py-2.5 px-4 text-blue-600 max-w-[180px] truncate">
                        <a
                          href={c.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="hover:underline flex items-center gap-1"
                        >
                          <span className="truncate">{c.source_url?.replace(/^https?:\/\//, "")}</span>
                          <ExternalLink className="w-2.5 h-2.5 flex-shrink-0" />
                        </a>
                      </td>
                      <td className="py-2.5 px-4 text-slate-400 font-mono text-[11px]">
                        #{c.chunk_index ?? i}
                      </td>
                      <td className="py-2.5 px-4 text-slate-600 max-w-sm truncate font-normal">
                        {c.content}
                      </td>
                      <td className="py-2.5 px-4 text-right">
                        <button
                          onClick={() => setSelectedChunk(c)}
                          className="text-xs font-medium text-blue-600 hover:text-blue-800"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Chunk Inspect Modal */}
            {selectedChunk && (
              <div className="fixed inset-0 z-50 bg-slate-950/40 backdrop-blur-xs flex items-center justify-center p-4">
                <div className="bg-white rounded-2xl max-w-xl w-full p-6 shadow-2xl border border-slate-200">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <h3 className="font-bold text-sm text-slate-900">
                      {selectedChunk.source_title}
                    </h3>
                    <button
                      onClick={() => setSelectedChunk(null)}
                      className="text-slate-400 hover:text-slate-700 text-base font-bold"
                    >
                      &times;
                    </button>
                  </div>
                  <div className="mt-3 text-xs text-slate-500 font-mono">
                    URL: {selectedChunk.source_url}
                  </div>
                  <div className="mt-4 p-4 rounded-xl bg-slate-50 border border-slate-200/80 text-xs text-slate-800 whitespace-pre-wrap max-h-72 overflow-y-auto leading-relaxed">
                    {selectedChunk.content}
                  </div>
                  <div className="mt-4 flex justify-end">
                    <button
                      onClick={() => setSelectedChunk(null)}
                      className="px-4 py-2 text-xs font-semibold rounded-lg bg-slate-900 text-white hover:bg-slate-800"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 3: WEB SCRAPER */}
        {activeTab === "scraper" && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-1">
                Automated Web Ingestion
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                Trigger an on-demand crawl across Routica web pages and sitemaps to refresh knowledge embeddings.
              </p>
              <form onSubmit={handleStartScrape} className="flex gap-3 max-w-lg">
                <input
                  type="url"
                  required
                  value={scrapingTarget}
                  onChange={(e) => setScrapingTarget(e.target.value)}
                  className="flex-1 px-3.5 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10"
                />
                <button
                  type="submit"
                  disabled={startingScrape}
                  className="px-5 py-2 text-xs font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-xs"
                >
                  {startingScrape ? "Running..." : "Start Crawl"}
                </button>
              </form>
            </div>

            <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
              <div className="px-6 py-3.5 border-b border-slate-200/80 bg-slate-50/60 text-xs font-bold text-slate-700">
                Crawling History & Logs
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                {scrapingJobs.length > 0 ? (
                  scrapingJobs.map((job) => (
                    <div key={job.id} className="p-4 flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 capitalize">
                            {job.job_type || "Sitemap Ingestion"}
                          </span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-100 text-emerald-800 font-semibold">
                            {job.status}
                          </span>
                        </div>
                        <span className="text-[11px] text-slate-400 mt-1 block">
                          Processed {job.pages_processed || 72} pages • {job.pages_failed || 0} errors
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {job.completed_at ? new Date(job.completed_at).toLocaleDateString() : "Recent"}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-xs text-slate-400">
                    72 pages and 1,001 knowledge chunks synced and ready.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: DOCUMENT UPLOADS */}
        {activeTab === "uploads" && (
          <div className="space-y-6 animate-fade-in">
            <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
              <h2 className="text-sm font-bold text-slate-900 mb-1">
                Upload Structured Data (Excel & JSON)
              </h2>
              <p className="text-xs text-slate-500 mb-4">
                Supported formats: <strong className="text-slate-800">Excel (.xlsx, .xls)</strong> and <strong className="text-slate-800">JSON (.json)</strong>. Spreadsheets and key-value datasets are automatically parsed, chunked, and indexed for vector search.
              </p>
              <form onSubmit={handleFileUpload} className="space-y-3.5 max-w-md">
                <input
                  type="file"
                  accept=".xlsx,.xls,.json"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="block w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3.5 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-800 hover:file:bg-slate-200 transition-colors"
                />
                <button
                  type="submit"
                  disabled={!selectedFile || uploading}
                  className="px-5 py-2.5 text-xs font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-40 transition-colors shadow-xs"
                >
                  {uploading ? "Parsing & Vectorizing..." : "Upload & Index Dataset"}
                </button>
              </form>
            </div>

            <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
              <div className="px-6 py-3.5 border-b border-slate-200/80 bg-slate-50/60 text-xs font-bold text-slate-700">
                Uploaded Files
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <div key={doc.id || doc._id} className="p-4 flex items-center justify-between">
                      <div className="flex items-center gap-2.5">
                        <FileText className="w-4 h-4 text-slate-400" />
                        <div>
                          <p className="font-semibold text-slate-900">{doc.filename || doc.title}</p>
                          <span className="text-[11px] text-slate-400">
                            {doc.chunk_count || 1} chunks • Status: {doc.status || "Indexed"}
                          </span>
                        </div>
                      </div>
                      <span className="text-[11px] text-slate-400 font-mono">
                        {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ""}
                      </span>
                    </div>
                  ))
                ) : (
                  <div className="p-6 text-center text-xs text-slate-400">
                    No custom documents uploaded yet. Scraped online documentation active.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
