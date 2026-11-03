import React from "react";
import { RotateCcw, X, Sparkles } from "lucide-react";
import { IconButton } from "../common/IconButton";
import { RouticaLogo } from "../common/RouticaLogo";
import { useChat } from "../../context/ChatContext";

export function ChatHeader() {
  const { closeChat, startNewConversation, backendStatus, messages, isStreaming } = useChat();

  const isOnline = backendStatus === "ready";

  return (
    <header className="relative flex items-center justify-between px-4 py-3 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 text-white rounded-t-2xl sm:rounded-t-3xl shadow-sm border-b border-slate-800/80 select-none">
      {/* Brand & Assistant Identity */}
      <div className="flex items-center space-x-3">
        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            {/* Official Routica Vector Logo */}
            <RouticaLogo variant="light" height={22} className="drop-shadow-xs" />
            
            <span className="hidden">Routica Assistant</span>
            <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-blue-500/15 text-blue-400 border border-blue-400/30 text-[10px] font-semibold tracking-wide uppercase">
              <Sparkles className="w-2.5 h-2.5 text-blue-400 animate-pulse" />
              AI
            </span>
          </div>

          <div className="flex items-center space-x-1.5 mt-0.5">
            <span
              className={`w-2 h-2 rounded-full ${
                isOnline ? "bg-emerald-400 animate-pulse" : "bg-amber-400"
              }`}
            />
            <span className="text-[11px] text-slate-300 font-medium tracking-tight">
              {isOnline ? "Online • Ready to assist" : "Connecting..."}
            </span>
          </div>
        </div>
      </div>

      {/* Header Actions */}
      <div className="flex items-center space-x-1">
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
