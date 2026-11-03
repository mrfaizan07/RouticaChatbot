import React from "react";
import { Sparkles, Compass, Radio, Cpu, HelpCircle, ShieldCheck } from "lucide-react";
import { SUGGESTED_QUESTIONS } from "../../config/constants";
import { useChat } from "../../context/ChatContext";

export function WelcomeScreen() {
  const { sendMessage, isStreaming } = useChat();

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

  return (
    <div className="flex flex-col items-center justify-center px-4 py-6 text-center my-auto animate-fade-in">
      {/* Visual Emblem */}
      <div className="relative mb-3 flex items-center justify-center">
        <div className="absolute -inset-1 rounded-2xl bg-gradient-to-r from-blue-600 to-sky-400 opacity-20 blur-md" />
        <div className="relative w-12 h-12 rounded-2xl bg-gradient-to-tr from-slate-900 via-blue-950 to-blue-900 border border-blue-500/30 flex items-center justify-center text-white shadow-lg">
          <Sparkles className="w-6 h-6 text-blue-400 animate-pulse" />
        </div>
      </div>

      <h3 className="text-base font-bold text-slate-900 tracking-tight">
        Welcome to Routica
      </h3>
      <p className="text-xs text-slate-500 max-w-[280px] mt-1 leading-relaxed">
        Your verified assistant for wireless gateway routers, marine & RV 5G connectivity, and technical support.
      </p>

      {/* Suggested Topics List */}
      <div className="w-full mt-5 space-y-2 text-left">
        <div className="flex items-center justify-between px-1">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
            Popular Questions
          </span>
          <span className="text-[10px] text-blue-600 font-medium">Click to ask</span>
        </div>

        <div className="grid grid-cols-1 gap-2">
          {SUGGESTED_QUESTIONS.map((item, idx) => (
            <button
              key={idx}
              type="button"
              disabled={isStreaming}
              onClick={() => sendMessage(item.query)}
              className="group flex items-start gap-3 p-2.5 text-xs rounded-xl border border-slate-200/90 bg-white hover:border-blue-400 hover:bg-blue-50/40 text-slate-700 hover:text-blue-950 transition-all duration-200 shadow-xs hover:shadow-sm text-left active:scale-[0.99]"
            >
              <div className="p-1.5 rounded-lg bg-slate-50 group-hover:bg-white border border-slate-100 group-hover:border-blue-200/60 transition-colors mt-0.5 flex-shrink-0 shadow-xs">
                {getIconForCategory(item.category)}
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-semibold text-slate-900 group-hover:text-blue-700 transition-colors">
                  {item.title}
                </span>
                <span className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                  {item.query}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Trust pill */}
      <div className="mt-4 flex items-center justify-center gap-1.5 text-[10px] text-slate-400">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-500" />
        <span>Grounded in official Routica documentation & specs</span>
      </div>
    </div>
  );
}
