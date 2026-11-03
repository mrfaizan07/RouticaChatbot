import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ChatbotLauncher } from "../components/chatbot/ChatbotLauncher";
import { ChatHeader } from "../components/chatbot/ChatHeader";
import { WelcomeScreen } from "../components/chatbot/WelcomeScreen";
import { ChatMessage } from "../components/chatbot/ChatMessage";
import { SourceReferences } from "../components/chatbot/SourceReferences";
import { ErrorMessage } from "../components/chatbot/ErrorMessage";
import { ChatProvider } from "../context/ChatContext";

describe("Frontend Components", () => {
  it("renders ChatbotLauncher and responds to click", () => {
    render(
      <ChatProvider>
        <ChatbotLauncher />
      </ChatProvider>
    );

    const launcher = screen.getByRole("button", { name: /open routica chatbot/i });
    expect(launcher).toBeInTheDocument();
    fireEvent.click(launcher);
  });

  it("renders ChatHeader with Routica branding and online indicator", () => {
    render(
      <ChatProvider>
        <ChatHeader />
      </ChatProvider>
    );

    expect(screen.getByText("Routica Assistant")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /close chat window/i })).toBeInTheDocument();
  });

  it("renders WelcomeScreen with suggested question topics", () => {
    render(
      <ChatProvider>
        <WelcomeScreen />
      </ChatProvider>
    );

    expect(screen.getByText(/Welcome to Routica/i)).toBeInTheDocument();
    expect(screen.getByText(/Explorer I vs Explorer II/i)).toBeInTheDocument();
    expect(screen.getByText(/Marine & RV Internet/i)).toBeInTheDocument();
  });

  it("renders user ChatMessage correctly", () => {
    const userMsg = {
      id: "u-1",
      role: "user",
      content: "Does Explorer II have 5G?",
    };

    render(<ChatMessage message={userMsg} />);
    expect(screen.getByText("Does Explorer II have 5G?")).toBeInTheDocument();
  });

  it("renders assistant ChatMessage with markdown and sources", () => {
    const asstMsg = {
      id: "a-1",
      role: "assistant",
      content: "Yes, **Explorer II** features *5G Sub-6GHz* connectivity.",
      sources: [
        {
          title: "Explorer II Manual",
          url: "https://routica.com/explorer-ii",
          relevance_score: 0.95,
        },
      ],
      model: "gemini-1.5-flash",
    };

    render(<ChatMessage message={asstMsg} />);
    expect(screen.getByText(/Explorer II/i)).toBeInTheDocument();
    expect(screen.getByText(/Verified Sources/i)).toBeInTheDocument();
  });

  it("expands and displays source reference URLs on click", () => {
    const sources = [
      {
        title: "Explorer II Specifications",
        url: "https://routica.com/products/explorer-ii",
        relevance_score: 0.92,
      },
    ];

    render(<SourceReferences sources={sources} />);
    const button = screen.getByRole("button", { name: /verified sources/i });
    expect(button).toBeInTheDocument();

    fireEvent.click(button);
    expect(screen.getByText("Explorer II Specifications")).toBeInTheDocument();
    expect(screen.getByText("92%")).toBeInTheDocument();
  });

  it("renders ErrorMessage with retry button", () => {
    const retryFn = vi.fn();
    render(<ErrorMessage message="Network connection failed" onRetry={retryFn} />);

    expect(screen.getByText("Network connection failed")).toBeInTheDocument();
    const retryBtn = screen.getByRole("button", { name: /retry/i });
    fireEvent.click(retryBtn);
    expect(retryFn).toHaveBeenCalledTimes(1);
  });
});

