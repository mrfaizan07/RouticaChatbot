import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ChatInput } from "../components/chatbot/ChatInput";
import { ChatProvider, useChat } from "../context/ChatContext";

// Test wrapper providing custom mock chat functions
function TestChatHarness({ onSend }) {
  return (
    <ChatProvider>
      <ChatInput />
    </ChatProvider>
  );
}

describe("Chat Input & Interaction Logic", () => {
  it("disables send button when input is empty or whitespace", () => {
    render(<TestChatHarness />);

    const sendBtn = screen.getByRole("button", { name: /send message/i });
    expect(sendBtn).toBeDisabled();

    const textarea = screen.getByRole("textbox", { name: /chat message input/i });
    fireEvent.change(textarea, { target: { value: "   " } });
    expect(sendBtn).toBeDisabled();

    fireEvent.change(textarea, { target: { value: "Valid question" } });
    expect(sendBtn).not.toBeDisabled();
  });

  it("sends message on Enter key press", () => {
    render(<TestChatHarness />);

    const textarea = screen.getByRole("textbox", { name: /chat message input/i });
    fireEvent.change(textarea, { target: { value: "Tell me about Explorer I" } });

    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: false });
    // Textarea input clears after send
    expect(textarea.value).toBe("");
  });

  it("does not send message on Shift+Enter (adds newline)", () => {
    render(<TestChatHarness />);

    const textarea = screen.getByRole("textbox", { name: /chat message input/i });
    fireEvent.change(textarea, { target: { value: "Line 1" } });

    fireEvent.keyDown(textarea, { key: "Enter", shiftKey: true });
    // Textarea input remains
    expect(textarea.value).toBe("Line 1");
  });
});

