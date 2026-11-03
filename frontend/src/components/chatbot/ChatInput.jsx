import React, { useState, useRef, useEffect } from "react";
import { Send, Square } from "lucide-react";
import { MAX_MESSAGE_LENGTH } from "../../config/constants";
import { useChat } from "../../context/ChatContext";

export function ChatInput() {
  const [input, setInput] = useState("");
  const textareaRef = useRef(null);
  const { sendMessage, isStreaming, cancelGeneration } = useChat();

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

  return (
    <footer className="p-3 border-t border-slate-200/80 bg-white sm:rounded-b-3xl">
      <form onSubmit={handleSubmit} className="relative flex flex-col">
        <div className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 focus-within:border-blue-500 focus-within:ring-2 focus-within:ring-blue-500/20 rounded-2xl px-3.5 py-2.5 transition-all shadow-xs">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={
              isStreaming
                ? "Routica Assistant is answering..."
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
              className="flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 disabled:opacity-30 disabled:cursor-not-allowed text-white shadow-xs transition-transform active:scale-95 flex-shrink-0"
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
