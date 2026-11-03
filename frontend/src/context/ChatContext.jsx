/**
 * Global Chat Context providing launcher state, backend status, quick options, and chat operations.
 */

import React, { createContext, useContext, useState, useEffect } from "react";
import { useStreamingChat } from "../hooks/useStreamingChat";
import { chatService } from "../services/chatService";

const ChatContext = createContext(null);

export function ChatProvider({ children }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isQuickTopicsOpen, setIsQuickTopicsOpen] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking"); // 'ready' | 'degraded' | 'offline' | 'checking'
  const [statusDetails, setStatusDetails] = useState(null);

  const chat = useStreamingChat();

  // Check real backend status on mount and periodically
  useEffect(() => {
    let isMounted = true;

    async function checkStatus() {
      try {
        const readyData = await chatService.checkReadiness();
        if (!isMounted) return;

        if (readyData.status === "ready") {
          setBackendStatus("ready");
          setStatusDetails(readyData);
        } else if (readyData.database && readyData.database.connected) {
          setBackendStatus("ready");
          setStatusDetails(readyData);
        } else {
          // Fallback to health probe
          const healthData = await chatService.checkHealth();
          if (healthData.status === "healthy") {
            setBackendStatus("ready");
            setStatusDetails(healthData);
          } else {
            setBackendStatus("offline");
          }
        }
      } catch (e) {
        if (isMounted) setBackendStatus("offline");
      }
    }

    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  const openChat = () => setIsOpen(true);
  const closeChat = () => {
    setIsOpen(false);
    setIsQuickTopicsOpen(false);
  };
  const toggleChat = () => setIsOpen((prev) => !prev);

  const toggleQuickTopics = () => setIsQuickTopicsOpen((prev) => !prev);
  const openQuickTopics = () => setIsQuickTopicsOpen(true);
  const closeQuickTopics = () => setIsQuickTopicsOpen(false);

  // Auto-close quick topics when a message is sent
  const sendQuickPrompt = (query) => {
    setIsQuickTopicsOpen(false);
    chat.sendMessage(query);
  };

  const value = {
    isOpen,
    openChat,
    closeChat,
    toggleChat,
    isQuickTopicsOpen,
    toggleQuickTopics,
    openQuickTopics,
    closeQuickTopics,
    sendQuickPrompt,
    backendStatus,
    statusDetails,
    ...chat,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
}
