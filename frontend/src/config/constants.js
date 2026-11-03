/**
 * Global application constants and configuration.
 */

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

export const ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/health`,
  READY: `${API_BASE_URL}/ready`,
  CHAT: `${API_BASE_URL}/api/v1/chat`,
  CHAT_STREAM: `${API_BASE_URL}/api/v1/chat/stream`,
  CONVERSATIONS: `${API_BASE_URL}/api/v1/conversations`,
};

export const STORAGE_KEYS = {
  SESSION_ID: "routica_session_id",
  ACTIVE_CONVERSATION_ID: "routica_active_conv_id",
  CHAT_OPEN: "routica_chat_open",
};

export const MAX_MESSAGE_LENGTH = 5000;

export const SUGGESTED_QUESTIONS = [
  {
    title: "Explorer I vs Explorer II",
    query: "What is the difference between Routica Explorer I and Explorer II?",
    category: "Products",
  },
  {
    title: "Marine & RV Internet",
    query: "How does Routica provide internet connectivity for boats, yachts, and RVs?",
    category: "Solutions",
  },
  {
    title: "Pricing & Guarantee",
    query: "What is the price of Explorer I and Explorer II, and is there a money-back guarantee?",
    category: "Support",
  },
  {
    title: "5G & Wi-Fi 6 Specs",
    query: "What are the 5G and Wi-Fi 6 technical specifications for Routica routers?",
    category: "Specs",
  },
];
