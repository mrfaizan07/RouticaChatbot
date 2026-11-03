import React from "react";
import { Sparkles } from "lucide-react";

export function TypingIndicator() {
  return (
    <div
      className="flex items-start gap-2.5 my-3 animate-fade-in"
      role="status"
      aria-label="Assistant is thinking"
    >
      <div className="w-7 h-7 rounded-xl bg-slate-900 border border-slate-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
        <Sparkles className="w-3.5 h-3.5 text-blue-400" />
      </div>

      <div className="flex flex-col gap-1 max-w-[80%]">
        <div className="px-3.5 py-2.5 rounded-2xl rounded-tl-xs bg-white border border-slate-200/90 shadow-xs flex items-center space-x-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.3s]"></span>
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.15s]"></span>
          <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-bounce"></span>
        </div>
      </div>
    </div>
  );
}
