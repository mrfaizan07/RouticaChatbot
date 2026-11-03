import React, { useState } from "react";
import { Bot, User, Copy, Check, Sparkles } from "lucide-react";
import { formatMarkdown } from "../../utils/formatMessage";
import { SourceReferences } from "./SourceReferences";

export function ChatMessage({ message }) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.warn("Failed to copy text:", err);
    }
  };

  if (isUser) {
    return (
      <div className="flex justify-end my-3 animate-fade-in">
        <div className="flex items-end gap-2 max-w-[85%] sm:max-w-[78%]">
          <div className="px-4 py-2.5 rounded-2xl rounded-br-xs bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-sm text-sm leading-relaxed whitespace-pre-wrap word-break break-words select-text">
            {message.content}
          </div>
          <div className="w-7 h-7 rounded-full bg-slate-200 border border-slate-300/60 text-slate-700 flex items-center justify-center flex-shrink-0 text-xs shadow-xs">
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message
  const htmlContent = formatMarkdown(message.content);

  return (
    <div className="flex justify-start my-3 animate-fade-in group">
      <div className="flex items-start gap-2.5 max-w-[95%] sm:max-w-[88%]">
        <div className="w-7 h-7 rounded-xl bg-slate-900 border border-slate-800 text-white flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
        </div>

        <div className="flex flex-col flex-1 min-w-0">
          <div
            className={`relative px-4 py-3 rounded-2xl rounded-tl-xs bg-white border ${
              message.isError
                ? "border-red-200 bg-red-50/40 text-red-900"
                : "border-slate-200/90 text-slate-800 shadow-xs"
            }`}
          >
            {/* Message Body */}
            {message.content ? (
              <div
                className="markdown-body text-sm select-text"
                dangerouslySetInnerHTML={{ __html: htmlContent }}
              />
            ) : (
              <div className="flex items-center gap-1.5 py-1 px-1">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.3s]" />
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce [animation-delay:-0.15s]" />
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" />
              </div>
            )}

            {/* Sources Citations */}
            {message.sources && message.sources.length > 0 && (
              <SourceReferences sources={message.sources} />
            )}

            {/* Response Footer (Model badge & Copy) */}
            {!message.isStreaming && message.content && (
              <div className="flex items-center justify-between mt-2.5 pt-1.5 border-t border-slate-100 text-[11px] text-slate-400 select-none">
                <span className="font-mono text-[10px] text-slate-400 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-100">
                  {message.model ? message.model.split("/").pop() : "Routica Verified"}
                </span>

                <button
                  type="button"
                  onClick={handleCopy}
                  title="Copy to clipboard"
                  className="inline-flex items-center gap-1 text-slate-400 hover:text-slate-700 transition-colors px-1.5 py-0.5 rounded hover:bg-slate-100"
                >
                  {copied ? (
                    <>
                      <Check className="w-3 h-3 text-emerald-600" />
                      <span className="text-emerald-600 font-medium">Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      <span>Copy</span>
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
