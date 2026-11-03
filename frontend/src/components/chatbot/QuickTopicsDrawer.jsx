import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, Compass, Radio, Cpu, HelpCircle, ShieldCheck, ArrowRight } from "lucide-react";
import { SUGGESTED_QUESTIONS } from "../../config/constants";
import { useChat } from "../../context/ChatContext";

export function QuickTopicsDrawer() {
  const { isQuickTopicsOpen, closeQuickTopics, sendQuickPrompt, isStreaming } = useChat();
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = ["All", "Products", "Specs", "Solutions", "Support"];

  const getIconForCategory = (category) => {
    switch (category) {
      case "Products":
        return <Compass className="w-4 h-4 text-blue-600" />;
      case "Solutions":
        return <Radio className="w-4 h-4 text-emerald-600" />;
      case "Specs":
        return <Cpu className="w-4 h-4 text-indigo-600" />;
      default:
        return <ShieldCheck className="w-4 h-4 text-amber-600" />;
    }
  };

  const filteredQuestions =
    selectedCategory === "All"
      ? SUGGESTED_QUESTIONS
      : SUGGESTED_QUESTIONS.filter((q) => q.category === selectedCategory);

  return (
    <AnimatePresence>
      {isQuickTopicsOpen && (
        <motion.div
          initial={{ opacity: 0, y: -12, height: 0 }}
          animate={{ opacity: 1, y: 0, height: "auto" }}
          exit={{ opacity: 0, y: -12, height: 0 }}
          transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-20 bg-slate-900/95 backdrop-blur-md border-b border-slate-800 text-white shadow-xl overflow-hidden"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-slate-800/80 bg-slate-950/60">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center border border-blue-400/30">
                <Sparkles className="w-3.5 h-3.5 animate-pulse" />
              </div>
              <div>
                <h4 className="text-xs font-bold text-slate-100 tracking-tight">
                  Suggested Topics & FAQs
                </h4>
                <p className="text-[10px] text-slate-400">
                  Select an option to immediately query Routica AI
                </p>
              </div>
            </div>

            <button
              onClick={closeQuickTopics}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/80 transition-colors"
              title="Close Topics"
              aria-label="Close Topics"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-1.5 px-4 py-2 overflow-x-auto scrollbar-none border-b border-slate-800/50 bg-slate-900/50">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all flex-shrink-0 ${
                  selectedCategory === cat
                    ? "bg-blue-600 text-white shadow-xs"
                    : "bg-slate-800/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Questions Grid */}
          <div className="max-h-60 overflow-y-auto p-3 space-y-2 chat-scrollbar">
            {filteredQuestions.map((item, idx) => (
              <button
                key={idx}
                type="button"
                disabled={isStreaming}
                onClick={() => sendQuickPrompt(item.query)}
                className="group w-full flex items-center justify-between p-2.5 rounded-xl border border-slate-800/90 bg-slate-950/40 hover:bg-slate-800/70 hover:border-blue-500/50 text-left transition-all active:scale-[0.99] disabled:opacity-40"
              >
                <div className="flex items-start gap-2.5 min-w-0 pr-2">
                  <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 flex-shrink-0 mt-0.5 group-hover:border-blue-500/40 transition-colors">
                    {getIconForCategory(item.category)}
                  </div>
                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-slate-200 group-hover:text-blue-300 transition-colors">
                        {item.title}
                      </span>
                      <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                        {item.category}
                      </span>
                    </div>
                    <span className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                      {item.query}
                    </span>
                  </div>
                </div>

                <div className="w-6 h-6 rounded-lg bg-slate-800/60 group-hover:bg-blue-600 text-slate-400 group-hover:text-white flex items-center justify-center flex-shrink-0 transition-colors">
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </button>
            ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
