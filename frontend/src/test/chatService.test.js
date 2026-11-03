import { describe, it, expect, vi, beforeEach } from "vitest";
import { chatService } from "../services/chatService";

describe("chatService", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("sends a message via POST and parses response JSON", async () => {
    const mockResponse = {
      conversation_id: "conv-123",
      message_id: "msg-456",
      answer: "Explorer II has dual SIM and 5G.",
      sources: [{ title: "Specs", url: "https://routica.com/specs" }],
      provider: "gemini",
      model: "gemini-1.5-flash",
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockResponse,
    });

    const result = await chatService.sendMessage({
      message: "What are the specs of Explorer II?",
    });

    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(result.answer).toBe("Explorer II has dual SIM and 5G.");
    expect(result.sources).toHaveLength(1);
  });

  it("handles backend error responses gracefully", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 429,
      statusText: "Too Many Requests",
      json: async () => ({
        error: { message: "Rate limit exceeded. Try again in 60s." },
      }),
    });

    await expect(
      chatService.sendMessage({ message: "Hello" })
    ).rejects.toThrow("Rate limit exceeded");
  });

  it("checks readiness and health endpoints", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: "ready" }),
    });

    const readyRes = await chatService.checkReadiness();
    expect(readyRes.status).toBe("ready");
  });
});

