import React from "react";
import { MessageSquare, X } from "lucide-react";
import { useChat } from "../../context/ChatContext";

export function ChatbotLauncher() {
  const { isOpen, toggleChat, backendStatus, messages } = useChat();

  return (
    <div className="fixed bottom-5 right-5 sm:bottom-6 sm:right-6 z-50">
      <button
        onClick={toggleChat}
        aria-label={isOpen ? "Close Routica Chatbot" : "Open Routica Chatbot"}
        aria-expanded={isOpen}
        className="group relative flex items-center justify-center w-14 h-14 rounded-full bg-routica-600 hover:bg-routica-700 text-white shadow-lg hover:shadow-xl hover:shadow-routica-600/25 transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-routica-400/50 active:scale-95"
      >
        {/* Pulsing subtle status ring when backend is ready */}
        {backendStatus === "ready" && !isOpen && (
          <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-white"></span>
          </span>
        )}

        {isOpen ? (
          <X className="w-6 h-6 transition-transform duration-200 group-hover:rotate-90" />
        ) : (
          <MessageSquare className="w-6 h-6 transition-transform duration-200 group-hover:scale-110" />
        )}

        {/* Hover label for desktop */}
        {!isOpen && (
          <span className="absolute right-16 px-3 py-1.5 rounded-lg bg-slate-900 text-white text-xs font-medium whitespace-nowrap opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity duration-200 shadow-md hidden sm:block">
            Ask Routica AI
          </span>
        )}
      </button>
    </div>
  );
}

