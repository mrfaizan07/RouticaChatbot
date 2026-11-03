import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, X, Compass, Radio, Cpu, ShieldCheck, ArrowRight, HelpCircle } from "lucide-react";
import { SUGGESTED_QUESTIONS } from "../../config/constants";
import { useChat } from "../../context/ChatContext";

export function QuickTopicsDrawer() {
  const { isQuickTopicsOpen, closeQuickTopics, sendQuickPrompt, isStreaming } = useChat();
  const [selectedCategory, setSelectedCategory] = useState("All");

  const categories = ["All", "Products", "Specs", "Solutions", "Support"];

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isQuickTopicsOpen) {
        closeQuickTopics();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isQuickTopicsOpen, closeQuickTopics]);

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
        <div className="absolute inset-0 z-40 flex items-center justify-center p-3 sm:p-4">
          {/* Backdrop Blur Overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.18 }}
            onClick={closeQuickTopics}
            className="absolute inset-0 bg-slate-950/60 backdrop-blur-xs"
          />

          {/* Centered Modal Card */}
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-label="Suggested Questions"
            initial={{ opacity: 0, scale: 0.94, y: 8 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 8 }}
            transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="relative z-50 w-full max-w-[380px] max-h-[82vh] sm:max-h-[540px] flex flex-col bg-white rounded-2xl sm:rounded-3xl shadow-2xl border border-slate-200/90 overflow-hidden text-slate-900"
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 bg-slate-50/80">
              <div className="flex items-center space-x-2.5">
                <div className="w-7 h-7 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-xs">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-slate-900 tracking-tight">
                    Quick Prompts & FAQs
                  </h3>
                  <p className="text-[10px] text-slate-500">
                    Select any topic to ask Routica Assistant
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={closeQuickTopics}
                className="w-7 h-7 rounded-lg text-slate-400 hover:text-slate-800 hover:bg-slate-200/60 transition-colors flex items-center justify-center"
                title="Close"
                aria-label="Close Prompts Modal"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center gap-1.5 px-3 py-2 overflow-x-auto scrollbar-none border-b border-slate-100 bg-white">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-2.5 py-1 rounded-full text-[11px] font-medium transition-all flex-shrink-0 ${
                    selectedCategory === cat
                      ? "bg-slate-900 text-white shadow-xs"
                      : "bg-slate-100 text-slate-600 hover:text-slate-900 hover:bg-slate-200"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Scrollable Questions List */}
            <div className="flex-1 overflow-y-auto p-3 space-y-2 chat-scrollbar bg-[#f8fafc]/50">
              {filteredQuestions.map((item, idx) => (
                <button
                  key={idx}
                  type="button"
                  disabled={isStreaming}
                  onClick={() => sendQuickPrompt(item.query)}
                  className="group w-full flex items-center justify-between p-2.5 rounded-xl border border-slate-200 bg-white hover:border-blue-400 hover:bg-blue-50/30 text-left transition-all active:scale-[0.99] disabled:opacity-40 shadow-xs hover:shadow-sm"
                >
                  <div className="flex items-start gap-2.5 min-w-0 pr-2">
                    <div className="p-1.5 rounded-lg bg-slate-50 border border-slate-100 flex-shrink-0 mt-0.5 group-hover:bg-white group-hover:border-blue-200 transition-colors">
                      {getIconForCategory(item.category)}
                    </div>
                    <div className="flex flex-col min-w-0">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                          {item.title}
                        </span>
                        <span className="text-[9px] uppercase tracking-wider px-1.5 py-0.5 rounded-md bg-slate-100 text-slate-500 font-medium">
                          {item.category}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-500 line-clamp-1 mt-0.5 font-normal">
                        {item.query}
                      </span>
                    </div>
                  </div>

                  <div className="w-6 h-6 rounded-lg bg-slate-50 group-hover:bg-blue-600 text-slate-400 group-hover:text-white flex items-center justify-center flex-shrink-0 transition-colors">
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </button>
              ))}
            </div>

            {/* Modal Footer Note */}
            <div className="px-4 py-2 bg-slate-50 border-t border-slate-100 text-[10px] text-slate-400 text-center">
              Answers are grounded in official Routica specs & documentation
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
