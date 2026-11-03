import React, { useState } from "react";
import { ExternalLink, ChevronDown, ChevronUp, BookOpen } from "lucide-react";

export function SourceReferences({ sources }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || !Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 pt-2.5 border-t border-slate-100 text-xs">
      <button
        type="button"
        onClick={() => setIsExpanded((prev) => !prev)}
        className="flex items-center justify-between w-full text-slate-500 hover:text-slate-800 font-medium py-1 text-left transition-colors"
        aria-expanded={isExpanded}
      >
        <span className="flex items-center gap-1.5">
          <BookOpen className="w-3.5 h-3.5 text-routica-600" />
          <span>Verified Sources ({sources.length})</span>
        </span>
        {isExpanded ? (
          <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
        ) : (
          <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
        )}
      </button>

      {isExpanded && (
        <div className="mt-2 space-y-1.5">
          {sources.map((src, index) => {
            const url = src.url || "https://routica.com";
            const title = src.title || "Routica Knowledge";
            const score = src.relevance_score ? Math.round(src.relevance_score * 100) : null;

            return (
              <a
                key={index}
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center justify-between p-2 rounded-lg bg-slate-50 hover:bg-routica-50 border border-slate-200/80 hover:border-routica-200 transition-all text-slate-700 hover:text-routica-900"
              >
                <div className="flex flex-col min-w-0 pr-2">
                  <span className="font-medium truncate group-hover:text-routica-700">
                    {title}
                  </span>
                  <span className="text-[10px] text-slate-400 truncate">
                    {url.replace(/^https?:\/\//, "")}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 flex-shrink-0">
                  {score && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">
                      {score}%
                    </span>
                  )}
                  <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-routica-600 transition-colors" />
                </div>
              </a>
            );
          })}
        </div>
      )}
    </div>
  );
}

