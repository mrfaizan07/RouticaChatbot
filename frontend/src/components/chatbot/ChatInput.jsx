import React, { useState, useRef, useEffect } from "react";
import { Send, Square, Compass, Sparkles } from "lucide-react";
import { MAX_MESSAGE_LENGTH, SUGGESTED_QUESTIONS } from "../../config/constants";
import { useChat } from "../../context/ChatContext";

export function ChatInput() {
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);
  const {
    sendMessage,
    isStreaming,
    cancelGeneration,
    messages,
    toggleQuickTopics,
    sendQuickPrompt,
  } = useChat();

  // Auto-resize textarea height
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isStreaming) return;
    sendMessage(input);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const isOverLimit = input.length > MAX_MESSAGE_LENGTH;
  const canSend = input.trim().length > 0 && !isOverLimit && !isStreaming;

  // Recent quick chips for 1-click queries
  const quickPills = [
    "Explorer I vs II",
    "Dual-SIM failover",
    "Pricing & guarantee",
    "Marine IP67 rating",
  ];

  return (
    <footer className="p-3 border-t border-slate-200/80 bg-white sm:rounded-b-3xl">
      {/* Quick Prompts Bar (visible during conversation) */}
      {messages.length > 0 && (
        <div className="flex items-center gap-1.5 pb-2.5 overflow-x-auto scrollbar-none text-[11px]">
          <button
            type="button"
            onClick={toggleQuickTopics}
            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200/80 font-medium hover:bg-blue-100 flex-shrink-0 transition-colors shadow-xs"
          >
            <Sparkles className="w-2.5 h-2.5 text-blue-600" />
            <span>Topics</span>
          </button>

          {quickPills.map((pill, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isStreaming}
              onClick={() => {
                const match = SUGGESTED_QUESTIONS.find((q) => q.title.includes(pill) || pill.includes(q.category));
                sendQuickPrompt(match ? match.query : `Tell me about Routica ${pill}`);
              }}
              className="px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200/70 border border-slate-200/60 font-medium transition-colors flex-shrink-0 disabled:opacity-40"
            >
              {pill}
            </button>
          ))}
        </div>
      )}

      <form onSubmit={handleSubmit} className="relative flex flex-col">
        <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/15 rounded-2xl px-3.5 py-2.5 transition-all shadow-xs">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isStreaming
                ? "Routica Assistant is generating..."
                : "Ask about Explorer I, II, 5G specs, pricing..."
            }
            aria-label="Chat message input"
            className="w-full bg-transparent text-sm text-slate-800 placeholder-slate-400 resize-none focus:outline-none max-h-32 min-h-[24px] leading-relaxed py-0.5"
          />

          {isStreaming ? (
            <button
              type="button"
              onClick={cancelGeneration}
              title="Stop generating"
              aria-label="Stop generation"
              className="flex items-center justify-center w-8 h-8 rounded-xl bg-slate-800 hover:bg-slate-900 text-white transition-transform active:scale-95 flex-shrink-0 shadow-xs"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          ) : (
            <button
              type="submit"
              disabled={!canSend}
              title="Send message (Enter)"
              aria-label="Send message"
              className="flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-30 disabled:cursor-not-allowed text-white shadow-xs transition-all active:scale-95 flex-shrink-0"
            >
              <Send className="w-3.5 h-3.5 ml-0.5" />
            </button>
          )}
        </div>

        {/* Helper footer */}
        <div className="flex items-center justify-between px-1.5 mt-1.5 text-[11px] text-slate-400">
          <span>Shift + Enter for new line</span>
          {input.length > 3000 && (
            <span className={isOverLimit ? "text-red-500 font-semibold" : ""}>
              {input.length}/{MAX_MESSAGE_LENGTH}
            </span>
          )}
        </div>
      </form>
    </footer>
  );
}
