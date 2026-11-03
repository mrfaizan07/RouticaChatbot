import React from "react";
import { MessageSquare, ChevronRight, Lock, ExternalLink } from "lucide-react";
import { RouticaLogo } from "../components/common/RouticaLogo";
import { useChat } from "../context/ChatContext";

export function Home({ onNavigateAdmin }) {
  const { openChat, backendStatus } = useChat();

  return (
    <main className="min-h-screen flex flex-col justify-between bg-white text-slate-900 selection:bg-blue-100 selection:text-blue-900">
      {/* Minimal Top Brand Bar */}
      <header className="w-full max-w-5xl mx-auto px-6 py-6 flex items-center justify-between border-b border-slate-100">
        <div className="flex items-center space-x-3">
          <RouticaLogo variant="dark" height={26} />
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-medium ${
              backendStatus === "ready"
                ? "bg-emerald-50 text-emerald-700 border border-emerald-100"
                : "bg-amber-50 text-amber-700 border border-amber-100"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                backendStatus === "ready" ? "bg-emerald-500 animate-pulse" : "bg-amber-500"
              }`}
            />
            {backendStatus === "ready" ? "System Operational" : "Connecting..."}
          </span>

          <button
            type="button"
            onClick={onNavigateAdmin}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 bg-white hover:bg-slate-50 text-slate-700 font-medium transition-all"
            title="Open Admin Dashboard"
          >
            <Lock className="w-3.5 h-3.5 text-slate-500" />
            <span>Admin</span>
          </button>
        </div>
      </header>

      {/* Main Minimal Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 py-20 text-center max-w-2xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-xs font-medium mb-6">
          <span>Official AI Assistant</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-950 leading-[1.15]">
          Official Chatbot for Routica
        </h1>

        <p className="mt-4 text-base sm:text-lg text-slate-600 max-w-lg font-normal leading-relaxed">
          Your intelligent assistant for Routica information and assistance.
        </p>

        {/* Primary Call to Action */}
        <div className="mt-8 flex items-center gap-3">
          <button
            type="button"
            onClick={openChat}
            aria-label="Launch Assistant"
            className="flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-700 active:scale-[0.99] text-white font-medium text-sm shadow-sm hover:shadow transition-all duration-150 focus:outline-none focus:ring-4 focus:ring-blue-100"
          >
            <MessageSquare className="w-4 h-4" />
            <span>Launch Assistant</span>
            <ChevronRight className="w-4 h-4 opacity-70" />
          </button>
        </div>
      </section>

      {/* Minimal Footer */}
      <footer className="w-full max-w-5xl mx-auto px-6 py-6 border-t border-slate-100 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
        <span>&copy; {new Date().getFullYear()} Routica. All rights reserved.</span>
        <div className="flex items-center space-x-4">
          <button
            type="button"
            onClick={onNavigateAdmin}
            className="hover:text-slate-600 transition-colors"
          >
            Admin Portal
          </button>
          <a
            href="https://routica.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 hover:text-slate-600 transition-colors"
          >
            <span>routica.com</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </footer>
    </main>
  );
}
