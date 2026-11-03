/**
 * Service managing user conversation history and session states.
 */

import { ENDPOINTS } from "../config/constants";
import { request } from "./api";

export const conversationService = {
  /**
   * Lists all conversations belonging to the active session.
   */
  async getConversations() {
    const res = await request(ENDPOINTS.CONVERSATIONS, { method: "GET" });
    return await res.json();
  },

  /**
   * Retrieves messages for an existing conversation ID.
   */
  async getMessages(conversationId) {
    if (!conversationId) return [];
    const res = await request(`${ENDPOINTS.CONVERSATIONS}/${conversationId}`, { method: "GET" });
    return await res.json();
  },

  /**
   * Deletes a conversation by ID.
   */
  async deleteConversation(conversationId) {
    if (!conversationId) return;
    const res = await request(`${ENDPOINTS.CONVERSATIONS}/${conversationId}`, { method: "DELETE" });
    return await res.json();
  },
};

