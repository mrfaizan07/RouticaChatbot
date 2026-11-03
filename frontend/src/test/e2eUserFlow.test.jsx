import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../App";

describe("E2E User Flow: Complete Chatbot Experience", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    sessionStorage.clear();
  });

  it("completes full user journey: launch -> question -> streamed answer -> citations -> reset -> close", async () => {
    // 1. Mock backend readiness
    global.fetch = vi.fn().mockImplementation((url) => {
      if (url.includes("/ready")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ status: "ready" }),
        });
      }
      if (url.includes("/health")) {
        return Promise.resolve({
          ok: true,
          json: async () => ({ status: "healthy" }),
        });
      }
      if (url.includes("/chat/stream")) {
        // Return a mock readable stream emitting SSE events
        const encoder = new TextEncoder();
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(
              encoder.encode('event: status\ndata: {"status": "retrieving", "conversation_id": "c-999"}\n\n')
            );
            controller.enqueue(
              encoder.encode(
                'event: sources\ndata: {"sources": [{"title": "Routica Explorer II", "url": "https://routica.com/explorer-ii", "relevance_score": 0.96}]}\n\n'
              )
            );
            controller.enqueue(
              encoder.encode('event: token\ndata: {"token": "Explorer II features "}\n\n')
            );
            controller.enqueue(
              encoder.encode('event: token\ndata: {"token": "5G Sub-6GHz connectivity with dual SIM failover."}\n\n')
            );
            controller.enqueue(
              encoder.encode('event: complete\ndata: {"message_id": "m-1", "conversation_id": "c-999", "model": "gemini-1.5-flash"}\n\n')
            );
            controller.close();
          },
        });

        return Promise.resolve({
          ok: true,
          body: stream,
        });
      }
      return Promise.reject(new Error("Unknown URL: " + url));
    });

    render(<App />);

    // 2. Verify main landing page
    expect(screen.getByText("Official Chatbot for Routica")).toBeInTheDocument();
    expect(screen.getByText(/Your intelligent assistant for Routica information and assistance/i)).toBeInTheDocument();

    // 3. Open the chatbot via "Launch Assistant" button
    const launchButton = screen.getByRole("button", { name: /launch assistant/i });
    fireEvent.click(launchButton);

    // 4. Verify Chatbot Dialog is open
    expect(screen.getByRole("dialog", { name: /routica chat assistant/i })).toBeInTheDocument();
    expect(screen.getByText(/Welcome to Routica/i)).toBeInTheDocument();

    // 5. Select a suggested question: "Explorer I vs Explorer II"
    const suggestedPill = screen.getByText(/Explorer I vs Explorer II/i);
    fireEvent.click(suggestedPill);

    // 6. Verify streaming response arrives
    await waitFor(() => {
      expect(screen.getByText(/5G Sub-6GHz connectivity with dual SIM failover/i)).toBeInTheDocument();
    });

    // 7. Verify source references are displayed
    expect(screen.getByText(/Verified Sources/i)).toBeInTheDocument();

    // 8. Test starting a new conversation
    const newConvBtn = screen.getByRole("button", { name: /reset and start new conversation/i });
    expect(newConvBtn).toBeInTheDocument();
    fireEvent.click(newConvBtn);

    // Welcome screen should reappear
    await waitFor(() => {
      expect(screen.getByText(/Welcome to Routica/i)).toBeInTheDocument();
    });

    // 9. Close the chatbot
    const closeBtn = screen.getByRole("button", { name: /close chat window/i });
    fireEvent.click(closeBtn);

    // Dialog should be closed
    await waitFor(() => {
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });
  });
});

