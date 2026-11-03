/**
 * Custom hook providing robust SSE streaming, state management, and cancellation.
 */

import { useState, useRef, useCallback, useEffect } from "react";
import { chatService } from "../services/chatService";
import {
  getActiveConversationId,
  setActiveConversationId,
  clearSessionState,
} from "../utils/storage";

export function useStreamingChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(getActiveConversationId());
  const [lastFailedMessage, setLastFailedMessage] = useState(null);

  const abortControllerRef = useRef(null);

  // Synchronize active conversation with session storage
  useEffect(() => {
    setActiveConversationId(conversationId);
  }, [conversationId]);

  /**
   * Cancels any in-flight streaming generation cleanly.
   */
  const cancelGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setStatusText("");
  }, []);

  /**
   * Resets the conversation to a clean state.
   */
  const startNewConversation = useCallback(() => {
    cancelGeneration();
    setMessages([]);
    setError(null);
    setLastFailedMessage(null);
    setConversationId(null);
    clearSessionState();
  }, [cancelGeneration]);

  /**
   * Sends a message and progressively consumes the SSE stream.
   */
  const sendMessage = useCallback(
    async (text) => {
      const trimmed = text.trim();
      if (!trimmed || isStreaming) return;

      setError(null);
      setLastFailedMessage(null);

      // Create optimistic user message
      const userMessage = {
        id: "user-" + Date.now(),
        role: "user",
        content: trimmed,
        created_at: new Date().toISOString(),
      };

      // Create placeholder assistant message for incoming stream
      const assistantMessageId = "asst-" + Date.now();
      const initialAssistantMessage = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        sources: [],
        isStreaming: true,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage, initialAssistantMessage]);
      setIsStreaming(true);
      setStatusText("");

      const controller = new AbortController();
      abortControllerRef.current = controller;

      let accumulatedContent = "";
      let accumulatedSources = [];

      try {
        await chatService.streamMessage({
          message: trimmed,
          conversationId,
          onEvent: (eventObj) => {
            const { event, data } = eventObj;

            switch (event) {
              case "status":
                if (data.conversation_id) {
                  setConversationId(data.conversation_id);
                }
                break;

              case "sources":
                if (data.sources && Array.isArray(data.sources)) {
                  accumulatedSources = data.sources;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, sources: accumulatedSources }
                        : msg
                    )
                  );
                }
                break;

              case "token":
                setStatusText("");
                if (data.token) {
                  accumulatedContent += data.token;
                  setMessages((prev) =>
                    prev.map((msg) =>
                      msg.id === assistantMessageId
                        ? { ...msg, content: accumulatedContent }
                        : msg
                    )
                  );
                }
                break;

              case "complete":
                if (data.conversation_id) {
                  setConversationId(data.conversation_id);
                }
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          isStreaming: false,
                          model: data.model,
                          provider: data.provider,
                          duration_ms: data.duration_ms,
                        }
                      : msg
                  )
                );
                break;

              case "error":
                const errMessage = data.error || "An error occurred during response generation.";
                setError(errMessage);
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === assistantMessageId
                      ? {
                          ...msg,
                          isStreaming: false,
                          content: accumulatedContent || "I encountered an issue processing your request.",
                          isError: true,
                        }
                      : msg
                  )
                );
                break;

              default:
                break;
            }
          },
          signal: controller.signal,
        });
      } catch (err) {
        if (err.name === "AbortError" || controller.signal.aborted) {
          // User aborted the stream intentionally
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    isStreaming: false,
                    content: accumulatedContent
                      ? accumulatedContent + "\n\n*(Generation stopped by user)*"
                      : "*(Generation stopped)*",
                  }
                : msg
            )
          );
        } else {
          const failureMsg = err.message || "Failed to communicate with the chatbot backend.";
          setError(failureMsg);
          setLastFailedMessage(trimmed);

          // Mark message with error
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    isStreaming: false,
                    content: accumulatedContent || "Failed to receive response. Please retry.",
                    isError: true,
                  }
                : msg
            )
          );
        }
      } finally {
        setIsStreaming(false);
        setStatusText("");
        abortControllerRef.current = null;
      }
    },
    [conversationId, isStreaming]
  );

  /**
   * Retries the last failed user message.
   */
  const retryLastMessage = useCallback(() => {
    if (!lastFailedMessage || isStreaming) return;
    const msgToRetry = lastFailedMessage;
    // Remove the failed user and assistant messages from the tail
    setMessages((prev) => {
      if (prev.length >= 2 && prev[prev.length - 1].isError) {
        return prev.slice(0, prev.length - 2);
      }
      return prev;
    });
    sendMessage(msgToRetry);
  }, [lastFailedMessage, isStreaming, sendMessage]);

  return {
    messages,
    isStreaming,
    statusText,
    error,
    conversationId,
    sendMessage,
    retryLastMessage,
    cancelGeneration,
    startNewConversation,
    hasFailedMessage: Boolean(lastFailedMessage),
  };
}

