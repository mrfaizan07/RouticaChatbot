/**
 * Chat service interfacing with FastAPI /chat and /chat/stream endpoints.
 */

import { ENDPOINTS } from "../config/constants";
import { request, ApiError } from "./api";
import { getSessionId } from "../utils/storage";
import { consumeSSEStream } from "../utils/streamParser";

export const chatService = {
  /**
   * Sends a chat message synchronously returning full JSON response.
   */
  async sendMessage({ message, conversationId, pageContext, signal }) {
    const sessionId = getSessionId();
    const payload = {
      message,
      session_id: sessionId,
      conversation_id: conversationId || null,
      page_context: pageContext || window.location.href,
    };

    const res = await request(ENDPOINTS.CHAT, {
      method: "POST",
      body: JSON.stringify(payload),
      signal,
    });

    return await res.json();
  },

  /**
   * Streams chat response tokens using POST-based SSE.
   * Dispatches typed events: status, sources, token, complete, error.
   */
  async streamMessage({ message, conversationId, pageContext, onEvent, signal }) {
    const sessionId = getSessionId();
    const payload = {
      message,
      session_id: sessionId,
      conversation_id: conversationId || null,
      page_context: pageContext || window.location.href,
    };

    const res = await request(ENDPOINTS.CHAT_STREAM, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        Accept: "text/event-stream",
      },
      signal,
    });

    await consumeSSEStream(res, onEvent, signal);
  },

  /**
   * Checks the readiness status of backend databases and AI providers.
   */
  async checkReadiness() {
    try {
      const res = await request(ENDPOINTS.READY, { timeoutMs: 4000 });
      return await res.json();
    } catch (err) {
      return { status: "unavailable", error: err.message };
    }
  },

  /**
   * Checks the basic process liveness.
   */
  async checkHealth() {
    try {
      const res = await request(ENDPOINTS.HEALTH, { timeoutMs: 3000 });
      return await res.json();
    } catch (err) {
      return { status: "unhealthy", error: err.message };
    }
  },
};

