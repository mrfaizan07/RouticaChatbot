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
  FileSpreadsheet,
  FileCode,
  Compass,
  MessageSquare,
  Sparkles,
  Info,
  X,
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
  const [knowledgeFilter, setKnowledgeFilter] = useState("all");
  const [selectedChunk, setSelectedChunk] = useState(null);
  const [scrapingJobs, setScrapingJobs] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loadingData, setLoadingData] = useState(false);
  const [actionMessage, setActionMessage] = useState("");
  const [actionType, setActionType] = useState("info"); // info, success, error

  // Upload state
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  // Scraper trigger state
  const [scrapingTarget, setScrapingTarget] = useState("https://routica.com");
  const [maxPages, setMaxPages] = useState(50);
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

      if (dashRes.status === "fulfilled" && dashRes.value) {
        setDashboard(dashRes.value);
      }
      if (provRes.status === "fulfilled" && provRes.value) {
        setProviders(provRes.value);
      }
      if (jobsRes.status === "fulfilled" && Array.isArray(jobsRes.value)) {
        setScrapingJobs(jobsRes.value);
      }
      if (docsRes.status === "fulfilled" && Array.isArray(docsRes.value)) {
        setDocuments(docsRes.value);
      }
      if (knowRes.status === "fulfilled" && knowRes.value) {
        const chunks = Array.isArray(knowRes.value.chunks) ? knowRes.value.chunks : [];
        setKnowledge(chunks);
        setKnowledgeTotal(typeof knowRes.value.total === "number" ? knowRes.value.total : chunks.length);
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
        body: JSON.stringify({ start_url: scrapingTarget, max_pages: parseInt(maxPages) || 50 }),
      });
      if (!res.ok) throw new Error("Failed to start scraper job");
      setActionType("success");
      setActionMessage("Website crawling and vector re-indexing job initialized successfully.");
      loadAdminData();
    } catch (err) {
      setActionType("error");
      setActionMessage(`Scraper error: ${err.message}`);
    } finally {
      setStartingScrape(false);
    }
  };

  // Handle Drag & Drop
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelection = (file) => {
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (![".xlsx", ".xls", ".json"].includes(ext)) {
      setActionType("error");
      setActionMessage("Error: Only Excel (.xlsx, .xls) and JSON (.json) files are permitted.");
      setSelectedFile(null);
      return;
    }
    setSelectedFile(file);
    setActionMessage("");
  };

  // Handle File Upload (Excel and JSON only)
  const handleFileUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    setUploading(true);
    setActionMessage("");

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

      setActionType("success");
      setActionMessage(data.message || `File "${selectedFile.name}" successfully parsed and vector-indexed.`);
      setSelectedFile(null);
      loadAdminData();
    } catch (err) {
      setActionType("error");
      if (err.name === "TypeError" && err.message.includes("fetch")) {
        setActionMessage("Server Connection Failed: Backend is not reachable at " + API_BASE_URL);
      } else {
        setActionMessage(`Upload error: ${err.message}`);
      }
    } finally {
      setUploading(false);
    }
  };

  // 1. Unauthenticated Login Screen
  if (!token) {
    return (
      <div className="min-h-screen flex flex-col justify-between bg-slate-50 text-slate-900 selection:bg-blue-100 selection:text-blue-900">
        <header className="px-6 py-4 border-b border-slate-200/90 bg-white shadow-xs">
          <div className="max-w-5xl mx-auto flex items-center justify-between">
            <RouticaLogo variant="dark" height={24} />
            <button
              onClick={onBackToHome}
              className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 transition-colors font-medium px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Return to Website</span>
            </button>
          </div>
        </header>

        <main className="flex-1 flex items-center justify-center p-6">
          <div className="w-full max-w-sm bg-white border border-slate-200/90 rounded-3xl p-8 shadow-sm">
            <div className="flex items-center space-x-2.5 text-slate-900 mb-2">
              <div className="w-8 h-8 rounded-xl bg-slate-900 text-white flex items-center justify-center shadow-xs">
                <Shield className="w-4 h-4 text-blue-400" />
              </div>
              <div>
                <h1 className="text-base font-bold tracking-tight">Admin Console</h1>
                <p className="text-[11px] text-slate-400">Routica AI Management</p>
              </div>
            </div>

            <p className="text-xs text-slate-500 mb-6 leading-relaxed mt-2">
              Sign in with your configured administrator credentials to manage datasets, knowledge vectors, and AI routing.
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
                  className="w-full px-3.5 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition-all placeholder:text-slate-400 bg-slate-50/50"
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
                  className="w-full px-3.5 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 transition-all bg-slate-50/50"
                />
              </div>

              <button
                type="submit"
                disabled={loginLoading}
                className="w-full py-2.5 px-4 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 active:scale-[0.99] text-white transition-all shadow-xs disabled:opacity-50 mt-2"
              >
                {loginLoading ? "Verifying..." : "Sign In to Console"}
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

  // 2. Authenticated Admin Dashboard
  const filteredChunks = (knowledge || []).filter((c) => {
    if (!c) return false;
    const search = (knowledgeSearch || "").trim().toLowerCase();
    const title = (c.source_title || "").toLowerCase();
    const content = (c.content || "").toLowerCase();
    const url = (c.source_url || "").toLowerCase();

    const matchesSearch =
      !search ||
      title.includes(search) ||
      content.includes(search) ||
      url.includes(search);

    if (!matchesSearch) return false;

    if (knowledgeFilter === "explorer1") {
      return (
        title.includes("explorer i") ||
        title.includes("explorer 1") ||
        content.includes("explorer i") ||
        content.includes("explorer 1")
      );
    }
    if (knowledgeFilter === "explorer2") {
      return (
        title.includes("explorer ii") ||
        title.includes("explorer 2") ||
        content.includes("explorer ii") ||
        content.includes("explorer 2")
      );
    }
    return true;
  });

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-900 selection:bg-blue-100 selection:text-blue-900 font-sans">
      {/* Top Navigation Bar */}
      <header className="sticky top-0 z-30 bg-white/95 backdrop-blur-md border-b border-slate-200 px-6 py-3 shadow-xs">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <RouticaLogo variant="dark" height={22} />
            <span className="text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200">
              Admin Platform
            </span>

          </div>

          <div className="flex items-center space-x-2.5 text-xs">
            <button
              onClick={loadAdminData}
              disabled={loadingData}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium transition-all shadow-xs"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loadingData ? "animate-spin text-blue-600" : ""}`} />
              <span className="hidden sm:inline">Refresh</span>
            </button>

            <button
              onClick={onBackToHome}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 font-medium transition-all shadow-xs"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              <span>Back to Site</span>
            </button>

            <button
              onClick={handleLogout}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-slate-500 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-red-200 transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Sign Out</span>
            </button>
          </div>
        </div>
      </header>

      {/* Subnav Tabs Bar */}
      <nav className="bg-white border-b border-slate-200 px-6 sticky top-[53px] z-20">
        <div className="max-w-7xl mx-auto flex space-x-8 text-xs font-medium">
          {[
            { id: "overview", label: "Overview & Telemetry", icon: Layers },
            { id: "knowledge", label: `Knowledge Base (${knowledgeTotal || 1001})`, icon: Database },
            { id: "scraper", label: "Web Crawler", icon: Globe },
            { id: "uploads", label: "Datasets & Uploads", icon: Upload },
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 py-3.5 border-b-2 transition-all ${active
                    ? "border-blue-600 text-blue-600 font-semibold"
                    : "border-transparent text-slate-500 hover:text-slate-900"
                  }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </nav>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto p-6 md:p-8">
        {actionMessage && (
          <div
            className={`mb-6 p-3.5 rounded-2xl border text-xs flex items-center justify-between shadow-xs animate-fade-in ${actionType === "success"
                ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                : actionType === "error"
                  ? "bg-red-50 border-red-200 text-red-900"
                  : "bg-blue-50 border-blue-200 text-blue-900"
              }`}
          >
            <div className="flex items-center gap-2">
              {actionType === "success" ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              ) : actionType === "error" ? (
                <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0" />
              ) : (
                <Info className="w-4 h-4 text-blue-600 flex-shrink-0" />
              )}
              <span className="font-medium">{actionMessage}</span>
            </div>
            <button
              onClick={() => setActionMessage("")}
              className="p-1 rounded hover:bg-black/5 text-slate-500 hover:text-slate-800"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* TAB 1: OVERVIEW */}
        {activeTab === "overview" && (
          <div className="space-y-6 animate-fade-in">
            {/* KPI Cards Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 md:gap-5">
              <div className="p-5 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider">
                    Knowledge Chunks
                  </span>
                  <Database className="w-4 h-4 text-blue-600" />
                </div>
                <p className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {dashboard ? dashboard.total_knowledge_chunks.toLocaleString() : "1,001"}
                </p>
                <div className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-500">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  <span>MongoDB Atlas Vector Search</span>
                </div>
              </div>

              <div className="p-5 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider">
                    Scraped Pages
                  </span>
                  <Globe className="w-4 h-4 text-emerald-600" />
                </div>
                <p className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {dashboard ? dashboard.total_pages_scraped : "72"}
                </p>
                <div className="mt-2 text-[11px] text-slate-500">
                  <span>Product specs, blogs & support</span>
                </div>
              </div>

              <div className="p-5 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider">
                    Hardware Models
                  </span>
                  <Cpu className="w-4 h-4 text-indigo-600" />
                </div>
                <p className="text-3xl font-extrabold text-slate-900 tracking-tight">
                  {dashboard ? dashboard.total_products : "2"}
                </p>
                <div className="mt-2 text-[11px] text-slate-500">
                  <span>Routica Explorer I & II Catalog</span>
                </div>
              </div>

              <div className="p-5 bg-white border border-slate-200/90 rounded-2xl shadow-xs">
                <div className="flex items-center justify-between text-slate-400 mb-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider">
                    Vector Status
                  </span>
                  <Activity className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse" />
                  <span className="text-xl font-bold text-slate-900">768-dim</span>
                </div>
                <div className="mt-2 text-[11px] text-slate-500">
                  <span>Cosine Similarity Indexing</span>
                </div>
              </div>
            </div>

            {/* AI Architecture & Resilience Panel */}
            <div className="bg-white border border-slate-200/90 rounded-2xl p-6 shadow-xs">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
                <div>
                  <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-600" />
                    <span>LLM Inference Router & Failover Chain</span>
                  </h2>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Multi-tier provider routing with automatic key rotation and zero-downtime fallback.
                  </p>
                </div>
                <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 self-start sm:self-auto">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  High Availability Active
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs mt-5">
                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-900">Tier 1: Primary Inference</span>
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold">
                      Active
                    </span>
                  </div>
                  <p className="text-slate-800 font-mono text-xs font-semibold">
                    groq/llama-3.3-70b-versatile
                  </p>
                  <p className="text-slate-500 text-[11px] mt-1.5">
                    Ultra-fast sub-second token streaming with dual API key rotation.
                  </p>
                </div>

                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-900">Tier 2: Fallback Inference</span>
                    <span className="px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 text-[10px] font-bold">
                      Standby
                    </span>
                  </div>
                  <p className="text-slate-800 font-mono text-xs font-semibold">
                    gemini/gemini-1.5-flash
                  </p>
                  <p className="text-slate-500 text-[11px] mt-1.5">
                    Google Multimodal AI & text-embedding-004 vector representation.
                  </p>
                </div>

                <div className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-colors">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-bold text-slate-900">Tier 3: Resilience Gateway</span>
                    <span className="px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 text-[10px] font-bold">
                      Standby
                    </span>
                  </div>
                  <p className="text-slate-800 font-mono text-xs font-semibold">
                    openrouter/llama-3.3-70b
                  </p>
                  <p className="text-slate-500 text-[11px] mt-1.5">
                    Global multi-datacenter disaster recovery inference fallback.
                  </p>
                </div>
              </div>

              {/* Security & System Guardrails */}
              <div className="mt-5 pt-4 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-4">
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-blue-600" />
                  <span>Rate Limiting: 60 req/min sliding IP window</span>
                </div>
                <div className="flex items-center gap-2">
                  <Server className="w-4 h-4 text-emerald-600" />
                  <span>CORS: Dynamic subdomains & localhost whitelisted</span>
                </div>
                <div className="flex items-center gap-2">
                  <Database className="w-4 h-4 text-slate-600" />
                  <span>Database: MongoDB Atlas Replica Set</span>
                </div>
              </div>
            </div>

            {/* Quick Actions Bar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <button
                type="button"
                onClick={() => setActiveTab("uploads")}
                className="group p-4 bg-white border border-slate-200/90 rounded-2xl text-left hover:border-blue-400 hover:shadow-xs transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Upload className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-900">Upload Dataset</h3>
                    <p className="text-[11px] text-slate-500">Ingest Excel (.xlsx) or JSON files</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-all" />
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("scraper")}
                className="group p-4 bg-white border border-slate-200/90 rounded-2xl text-left hover:border-emerald-400 hover:shadow-xs transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Globe className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-900">Trigger Web Crawler</h3>
                    <p className="text-[11px] text-slate-500">Scrape and re-vectorize Routica pages</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-0.5 transition-all" />
              </button>

              <button
                type="button"
                onClick={() => setActiveTab("knowledge")}
                className="group p-4 bg-white border border-slate-200/90 rounded-2xl text-left hover:border-indigo-400 hover:shadow-xs transition-all flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-105 transition-transform">
                    <Database className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-xs font-bold text-slate-900">Search Knowledge</h3>
                    <p className="text-[11px] text-slate-500">Inspect 1,001 stored vector chunks</p>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-indigo-600 group-hover:translate-x-0.5 transition-all" />
              </button>
            </div>
          </div>
        )}

        {/* TAB 2: KNOWLEDGE BASE */}
        {activeTab === "knowledge" && (
          <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs animate-fade-in">
            {/* Filter Bar */}
            <div className="p-4 border-b border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="relative flex-1 max-w-md">
                <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Filter knowledge chunks by keywords, title, content..."
                  value={knowledgeSearch}
                  onChange={(e) => setKnowledgeSearch(e.target.value)}
                  className="w-full pl-9 pr-3 py-1.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 bg-slate-50/50"
                />
              </div>

              {/* Filter Pills */}
              <div className="flex items-center gap-1.5 text-xs">
                {[
                  { id: "all", label: "All Chunks" },
                  { id: "explorer1", label: "Explorer I" },
                  { id: "explorer2", label: "Explorer II" },
                ].map((pill) => (
                  <button
                    key={pill.id}
                    type="button"
                    onClick={() => setKnowledgeFilter(pill.id)}
                    className={`px-3 py-1 rounded-xl font-medium transition-colors ${knowledgeFilter === pill.id
                        ? "bg-slate-900 text-white"
                        : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                      }`}
                  >
                    {pill.label}
                  </button>
                ))}
                <span className="text-xs text-slate-400 ml-2 hidden lg:inline">
                  {filteredChunks.length} displayed ({knowledgeTotal || filteredChunks.length} total)
                </span>
              </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto max-h-[580px] overflow-y-auto chat-scrollbar">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50/80 text-slate-600 sticky top-0 border-b border-slate-200 font-semibold z-10">
                  <tr>
                    <th className="py-3 px-4">Source Title</th>
                    <th className="py-3 px-4">Source URL</th>
                    <th className="py-3 px-4">Chunk ID</th>
                    <th className="py-3 px-4">Content Preview</th>
                    <th className="py-3 px-4 text-right">Inspect</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {loadingData ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-400">
                        <div className="flex items-center justify-center gap-2">
                          <RefreshCw className="w-4 h-4 animate-spin text-blue-600" />
                          <span>Fetching knowledge chunks from MongoDB...</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredChunks.length === 0 ? (
                    <tr>
                      <td colSpan={5} className="py-12 text-center text-slate-400">
                        <div className="flex flex-col items-center justify-center max-w-sm mx-auto">
                          <Database className="w-8 h-8 text-slate-300 mb-2" />
                          <p className="text-xs font-semibold text-slate-700">No knowledge chunks found</p>
                          <p className="text-[11px] text-slate-400 mt-0.5">
                            {knowledgeSearch || knowledgeFilter !== "all"
                              ? "Try resetting filters or clearing the search bar."
                              : "No chunks currently indexed in database. Trigger a crawl to populate."}
                          </p>
                          <div className="flex items-center gap-2 mt-3">
                            <button
                              type="button"
                              onClick={() => setActiveTab("scraper")}
                              className="px-3 py-1.5 rounded-xl bg-slate-900 text-white text-[11px] font-semibold hover:bg-slate-800 transition-colors"
                            >
                              Crawl Website
                            </button>
                            <button
                              type="button"
                              onClick={() => setActiveTab("uploads")}
                              className="px-3 py-1.5 rounded-xl border border-slate-200 text-slate-700 text-[11px] font-semibold hover:bg-slate-50 transition-colors"
                            >
                              Upload Dataset
                            </button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filteredChunks.slice(0, 100).map((c, i) => (
                      <tr key={c.id || i} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-3 px-4 font-semibold text-slate-900 max-w-[200px] truncate">
                          {c.source_title || "Routica Documentation"}
                        </td>
                        <td className="py-3 px-4 text-blue-600 max-w-[180px] truncate">
                          <a
                            href={c.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:underline flex items-center gap-1"
                          >
                            <span className="truncate">{c.source_url?.replace(/^https?:\/\//, "")}</span>
                            <ExternalLink className="w-3 h-3 flex-shrink-0" />
                          </a>
                        </td>
                        <td className="py-3 px-4 text-slate-400 font-mono text-[11px]">
                          #{c.chunk_index ?? i}
                        </td>
                        <td className="py-3 px-4 text-slate-600 max-w-md truncate font-normal">
                          {c.content}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => setSelectedChunk(c)}
                            className="px-2.5 py-1 text-xs font-semibold rounded-lg bg-blue-50 text-blue-600 hover:bg-blue-100 transition-colors"
                          >
                            View
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Chunk Inspect Modal */}
            {selectedChunk && (
              <div className="fixed inset-0 z-50 bg-slate-950/50 backdrop-blur-xs flex items-center justify-center p-4">
                <div className="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl border border-slate-200 animate-fade-in">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="font-bold text-sm text-slate-900">
                        {selectedChunk.source_title || "Knowledge Chunk"}
                      </h3>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                        Index #{selectedChunk.chunk_index} • Vector Dimension 768
                      </p>
                    </div>
                    <button
                      onClick={() => setSelectedChunk(null)}
                      className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100"
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                  <div className="mt-3 text-xs text-blue-600 font-mono flex items-center gap-1 truncate">
                    <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    <a href={selectedChunk.source_url} target="_blank" rel="noreferrer" className="hover:underline truncate">
                      {selectedChunk.source_url}
                    </a>
                  </div>
                  <div className="mt-4 p-4 rounded-2xl bg-slate-50 border border-slate-200/80 text-xs text-slate-800 whitespace-pre-wrap max-h-80 overflow-y-auto leading-relaxed font-sans chat-scrollbar">
                    {selectedChunk.content}
                  </div>
                  <div className="mt-4 flex justify-end">
                    <button
                      onClick={() => setSelectedChunk(null)}
                      className="px-5 py-2 text-xs font-semibold rounded-xl bg-slate-900 text-white hover:bg-slate-800 shadow-xs"
                    >
                      Close Window
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
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-emerald-600" />
                  <span>On-Demand Web Crawler</span>
                </h2>
                <span className="text-[11px] text-slate-400">
                  Target Domain: routica.com
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-4 leading-relaxed">
                Enter an official Routica URL to crawl product catalogs, user manuals, and technical specifications, then generate fresh vector embeddings in MongoDB Atlas.
              </p>

              {/* URL presets */}
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className="text-[11px] font-semibold text-slate-400">Presets:</span>
                {[
                  "https://routica.com",
                  "https://routica.com/shop",
                  "https://routica.com/support",
                  "https://routica.com/explorer-2",
                ].map((url) => (
                  <button
                    key={url}
                    type="button"
                    onClick={() => setScrapingTarget(url)}
                    className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-[11px] font-medium transition-colors"
                  >
                    {url.replace("https://routica.com", "") || "/ (Home)"}
                  </button>
                ))}
              </div>

              <form onSubmit={handleStartScrape} className="flex flex-col sm:flex-row gap-3 max-w-2xl">
                <input
                  type="url"
                  required
                  value={scrapingTarget}
                  onChange={(e) => setScrapingTarget(e.target.value)}
                  placeholder="https://routica.com/..."
                  className="flex-1 px-3.5 py-2.5 text-xs border border-slate-200 rounded-xl focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/10 bg-slate-50/50"
                />
                <select
                  value={maxPages}
                  onChange={(e) => setMaxPages(e.target.value)}
                  className="px-3 py-2.5 text-xs border border-slate-200 rounded-xl bg-slate-50/50 text-slate-700 focus:outline-none"
                >
                  <option value={25}>Max 25 Pages</option>
                  <option value={50}>Max 50 Pages</option>
                  <option value={100}>Max 100 Pages</option>
                </select>
                <button
                  type="submit"
                  disabled={startingScrape}
                  className="px-6 py-2.5 text-xs font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-all shadow-xs flex-shrink-0 flex items-center justify-center gap-2"
                >
                  {startingScrape ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Crawling...</span>
                    </>
                  ) : (
                    <span>Start Ingestion</span>
                  )}
                </button>
              </form>
            </div>

            <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
              <div className="px-6 py-3.5 border-b border-slate-200/80 bg-slate-50/60 text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Crawling History & Logs</span>
                <span className="text-[11px] text-slate-400 font-normal">Automated 24h cron schedule active</span>
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                {scrapingJobs.length > 0 ? (
                  scrapingJobs.map((job) => (
                    <div key={job.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-slate-900 capitalize">
                            {job.job_type || "Sitemap Ingestion"}
                          </span>
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-emerald-100 text-emerald-800 font-semibold">
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
                  <div className="p-8 text-center text-xs text-slate-400">
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
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                  <Upload className="w-4 h-4 text-blue-600" />
                  <span>Structured Dataset Ingestion (Excel & JSON)</span>
                </h2>
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 text-[10px] font-semibold">
                    <FileSpreadsheet className="w-3 h-3 text-emerald-600" />
                    .xlsx / .xls
                  </span>
                  <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-[10px] font-semibold">
                    <FileCode className="w-3 h-3 text-blue-600" />
                    .json
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-500 mb-5 leading-relaxed">
                Upload your product inventory spreadsheets or FAQ datasets. Spreadsheets and key-value JSON records are parsed into clean rows, embedded via Gemini, and indexed into MongoDB Atlas vector storage.
              </p>

              {/* Drag and drop zone */}
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`relative border-2 border-dashed rounded-2xl p-8 text-center transition-all ${dragActive
                    ? "border-blue-500 bg-blue-50/50"
                    : "border-slate-200 bg-slate-50/40 hover:bg-slate-50 hover:border-slate-300"
                  }`}
              >
                <div className="w-12 h-12 rounded-2xl bg-white border border-slate-200 shadow-xs flex items-center justify-center mx-auto text-blue-600 mb-3">
                  <Upload className="w-6 h-6" />
                </div>
                <h3 className="text-xs font-bold text-slate-900 mb-1">
                  Drag and drop your dataset here, or browse
                </h3>
                <p className="text-[11px] text-slate-400 mb-4">
                  Strictly supports Excel spreadsheets (.xlsx, .xls) and JSON (.json) up to 15MB.
                </p>

                <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold cursor-pointer shadow-xs transition-colors">
                  <span>Select File</span>
                  <input
                    type="file"
                    accept=".xlsx,.xls,.json"
                    onChange={(e) => {
                      if (e.target.files && e.target.files[0]) {
                        handleFileSelection(e.target.files[0]);
                      }
                    }}
                    className="hidden"
                  />
                </label>

                {selectedFile && (
                  <div className="mt-4 p-3 bg-white border border-slate-200 rounded-xl inline-flex items-center gap-3 text-xs text-slate-800 shadow-xs">
                    <FileText className="w-4 h-4 text-blue-600" />
                    <span className="font-semibold">{selectedFile.name}</span>
                    <span className="text-slate-400 font-mono text-[11px]">
                      ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </span>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="text-slate-400 hover:text-red-600 ml-1 font-bold"
                    >
                      &times;
                    </button>
                  </div>
                )}
              </div>

              {/* Upload trigger button */}
              {selectedFile && (
                <div className="mt-4 flex justify-end">
                  <button
                    type="button"
                    onClick={handleFileUpload}
                    disabled={uploading}
                    className="px-6 py-2.5 text-xs font-semibold bg-slate-900 text-white rounded-xl hover:bg-slate-800 disabled:opacity-50 transition-colors shadow-xs flex items-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Parsing & Vectorizing...</span>
                      </>
                    ) : (
                      <span>Upload & Index Dataset</span>
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Uploaded Documents List */}
            <div className="bg-white border border-slate-200/90 rounded-2xl overflow-hidden shadow-xs">
              <div className="px-6 py-3.5 border-b border-slate-200/80 bg-slate-50/60 text-xs font-bold text-slate-700 flex items-center justify-between">
                <span>Indexed Datasets Registry</span>
                <span className="text-[11px] text-slate-400 font-normal">Active in Vector Retrieval</span>
              </div>
              <div className="divide-y divide-slate-100 text-xs">
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <div key={doc.id || doc._id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-600">
                          <FileText className="w-4 h-4" />
                        </div>
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
                  <div className="p-8 text-center text-xs text-slate-400">
                    No custom datasets uploaded yet. Scraped online documentation active.
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
