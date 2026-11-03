import React from "react";
import { RotateCcw, X, Sparkles, ChevronDown } from "lucide-react";
import { IconButton } from "../common/IconButton";
import { RouticaLogo } from "../common/RouticaLogo";
import { useChat } from "../../context/ChatContext";

export function ChatHeader() {
  const {
    closeChat,
    startNewConversation,
    backendStatus,
    messages,
    isStreaming,
    isQuickTopicsOpen,
    toggleQuickTopics,
  } = useChat();

  const isOnline = backendStatus === "ready";

  return (
    <header className="relative z-50 flex items-center justify-between px-4 py-3 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 text-white rounded-t-2xl sm:rounded-t-3xl shadow-sm border-b border-slate-800/80 select-none">
      {/* Brand & Assistant Identity */}
      <div className="flex items-center space-x-3">
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            {/* Official Routica Vector Logo */}
            <RouticaLogo variant="light" height={22} className="drop-shadow-xs" />
            <span className="sr-only">Routica Assistant</span>


          </div>

          <div className="flex items-center space-x-1.5 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full ${isOnline ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
                }`}
            />

          </div>
        </div>
      </div>

      {/* Header Actions */}
      <div className="flex items-center space-x-1.5">
        {/* Executive Quick Prompts Toggle Button */}
        <button
          type="button"
          onClick={toggleQuickTopics}
          title={isQuickTopicsOpen ? "Close suggested prompts" : "Explore suggested questions & topics"}
          aria-label={isQuickTopicsOpen ? "Close Prompts Drawer" : "Open Prompts Drawer"}
          aria-expanded={isQuickTopicsOpen}
          className={`group relative inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-400/50 select-none ${isQuickTopicsOpen
            ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md shadow-blue-500/30 border border-blue-400/50 ring-1 ring-white/20 active:scale-95"
            : "bg-slate-800/80 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700/80 hover:border-blue-400/50 shadow-xs hover:shadow-blue-500/10 active:scale-95"
            }`}
        >
          {/* Dynamic Toggle Icon (Sparkles <-> X) */}
          <span className="relative flex items-center justify-center">
            {isQuickTopicsOpen ? (
              <X className="w-3.5 h-3.5 text-white transition-transform duration-200 group-hover:rotate-90" />
            ) : (
              <Sparkles className="w-3.5 h-3.5 text-blue-400 group-hover:text-blue-300 transition-all duration-200 group-hover:scale-110" />
            )}
          </span>

          <span className="text-[11px] font-semibold tracking-tight">
            Prompts
          </span>

          {/* Toggle Chevron Indicator */}
          <ChevronDown
            className={`w-3 h-3 transition-transform duration-200 ${isQuickTopicsOpen
              ? "rotate-180 text-white/90"
              : "text-slate-400 group-hover:text-slate-200"
              }`}
          />
        </button>

        {messages.length > 0 && (
          <IconButton
            icon={RotateCcw}
            onClick={startNewConversation}
            variant="header"
            size="sm"
            title="New Conversation"
            ariaLabel="Reset and start new conversation"
            disabled={isStreaming}
            className="hover:bg-slate-800/80 hover:text-white text-slate-300 transition-colors"
          />
        )}

        <IconButton
          icon={X}
          onClick={closeChat}
          variant="header"
          size="sm"
          title="Close Chat"
          ariaLabel="Close chat window"
          className="hover:bg-slate-800/80 hover:text-white text-slate-300 transition-colors"
        />
      </div>
    </header>
  );
}
