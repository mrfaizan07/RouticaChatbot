import React, { useEffect, useRef, useState } from "react";
import { ChatMessage } from "./ChatMessage";
import { WelcomeScreen } from "./WelcomeScreen";
import { TypingIndicator } from "./TypingIndicator";
import { ErrorMessage } from "./ErrorMessage";
import { useChat } from "../../context/ChatContext";

export function ChatMessages() {
  const { messages, isStreaming, statusText, error, retryLastMessage, hasFailedMessage } = useChat();
  const scrollRef = useRef(null);
  const [userHasScrolledUp, setUserHasScrolledUp] = useState(false);

  // Monitor user scroll position
  const handleScroll = () => {
    if (!scrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 60;
    setUserHasScrolledUp(!isAtBottom);
  };

  // Smart auto-scroll: only scrolls to bottom if user hasn't explicitly scrolled up
  useEffect(() => {
    if (!userHasScrolledUp && scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: isStreaming ? "auto" : "smooth",
      });
    }
  }, [messages, statusText, isStreaming, userHasScrolledUp]);

  return (
    <div
      ref={scrollRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto px-4 py-3 chat-scrollbar bg-[#f8fafc]/50 flex flex-col"
    >
      {messages.length === 0 ? (
        <WelcomeScreen />
      ) : (
        <div className="flex flex-col flex-1">
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {isStreaming && statusText && (
            <TypingIndicator statusText={statusText} />
          )}

          {error && (
            <ErrorMessage
              message={error}
              onRetry={hasFailedMessage ? retryLastMessage : null}
            />
          )}
        </div>
      )}
    </div>
  );
}

