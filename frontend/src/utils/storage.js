/**
 * Safe client-side storage utility managing session tokens without leaking cross-user data.
 */

import { STORAGE_KEYS } from "../config/constants";

export const generateUUID = () => {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
};

export const getSessionId = () => {
  try {
    let sessionId = sessionStorage.getItem(STORAGE_KEYS.SESSION_ID);
    if (!sessionId) {
      sessionId = generateUUID();
      sessionStorage.setItem(STORAGE_KEYS.SESSION_ID, sessionId);
    }
    return sessionId;
  } catch (e) {
    // Fallback for private browsing where storage may be restricted
    return "ephemeral-" + generateUUID();
  }
};

export const getActiveConversationId = () => {
  try {
    return sessionStorage.getItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID) || null;
  } catch (e) {
    return null;
  }
};

export const setActiveConversationId = (convId) => {
  try {
    if (convId) {
      sessionStorage.setItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID, convId);
    } else {
      sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID);
    }
  } catch (e) {
    // Ignore storage quota errors
  }
};

export const clearSessionState = () => {
  try {
    sessionStorage.removeItem(STORAGE_KEYS.ACTIVE_CONVERSATION_ID);
  } catch (e) {}
};

