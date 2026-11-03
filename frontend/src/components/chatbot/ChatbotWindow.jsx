import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChatHeader } from "./ChatHeader";
import { QuickTopicsDrawer } from "./QuickTopicsDrawer";
import { ChatMessages } from "./ChatMessages";
import { ChatInput } from "./ChatInput";
import { useChat } from "../../context/ChatContext";

export function ChatbotWindow() {
  const { isOpen, closeChat } = useChat();
  const windowRef = useRef(null);

  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === "Escape" && isOpen) {
        closeChat();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, closeChat]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          ref={windowRef}
          role="dialog"
          aria-label="Routica Chat Assistant"
          aria-modal="false"
          initial={{ opacity: 0, y: 20, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 16, scale: 0.95 }}
          transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="fixed bottom-0 right-0 sm:bottom-24 sm:right-6 z-50 w-full sm:w-[420px] h-[100dvh] sm:h-[640px] sm:max-h-[85vh] flex flex-col bg-white sm:rounded-3xl shadow-2xl shadow-slate-950/25 border border-slate-200/90 overflow-hidden origin-bottom-right"
        >
          <ChatHeader />
          <ChatMessages />
          <ChatInput />
          <QuickTopicsDrawer />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
