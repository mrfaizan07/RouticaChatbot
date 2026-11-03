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
    query: "How does Routica provide reliable internet connectivity for boats, yachts, and RVs?",
    category: "Solutions",
  },
  {
    title: "Dual SIM & Carrier Failover",
    query: "How does the dual-SIM automatic carrier failover work on Routica routers?",
    category: "Specs",
  },
  {
    title: "Pricing & 30-Day Guarantee",
    query: "What is the price of Explorer I and Explorer II, and is there a money-back guarantee?",
    category: "Support",
  },
  {
    title: "5G & Wi-Fi 6 Specifications",
    query: "What are the 5G cellular speed and Wi-Fi 6 technical specifications for Routica routers?",
    category: "Specs",
  },
  {
    title: "Installation & Setup Guide",
    query: "How do I install and power the Routica Explorer on my RV or marine vessel?",
    category: "Support",
  },
];
