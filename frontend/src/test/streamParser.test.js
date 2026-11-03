import { describe, it, expect, vi } from "vitest";
import { SSEStreamParser } from "../utils/streamParser";

describe("SSEStreamParser", () => {
  it("parses a single complete event with JSON data", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    parser.feed('event: token\ndata: {"token": "Explorer II"}\n\n');

    expect(events).toHaveLength(1);
    expect(events[0].event).toBe("token");
    expect(events[0].data).toEqual({ token: "Explorer II" });
  });

  it("handles multiple events delivered in a single chunk", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    const chunk = [
      'event: status\ndata: {"status": "retrieving"}\n\n',
      'event: sources\ndata: {"sources": [{"title": "Routica Specs"}]}\n\n',
      'event: token\ndata: {"token": "Hello"}\n\n',
    ].join("");

    parser.feed(chunk);

    expect(events).toHaveLength(3);
    expect(events[0].event).toBe("status");
    expect(events[1].event).toBe("sources");
    expect(events[2].event).toBe("token");
    expect(events[2].data.token).toBe("Hello");
  });

  it("handles one event split across multiple chunk reads", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    parser.feed("event: tok");
    expect(events).toHaveLength(0);

    parser.feed('en\ndata: {"token": "5G Sub-');
    expect(events).toHaveLength(0);

    parser.feed('6GHz"}\n\n');
    expect(events).toHaveLength(1);
    expect(events[0].event).toBe("token");
    expect(events[0].data.token).toBe("5G Sub-6GHz");
  });

  it("handles Windows CRLF (\\r\\n) line endings correctly", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    parser.feed('event: status\r\ndata: {"status": "ready"}\r\n\r\n');

    expect(events).toHaveLength(1);
    expect(events[0].event).toBe("status");
    expect(events[0].data.status).toBe("ready");
  });

  it("handles UTF-8 and multilingual/Hindi characters without corruption", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    parser.feed('event: token\ndata: {"token": "नमस्ते, Routica में आपका स्वागत है।"}\n\n');

    expect(events).toHaveLength(1);
    expect(events[0].data.token).toBe("नमस्ते, Routica में आपका स्वागत है।");
  });

  it("ignores SSE comments and keep-alive heartbeats", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    parser.feed(": heartbeat ping\n\n");
    parser.feed('event: complete\ndata: {"duration_ms": 120}\n\n');

    expect(events).toHaveLength(1);
    expect(events[0].event).toBe("complete");
  });

  it("flushes remaining buffered event on stream end", () => {
    const events = [];
    const parser = new SSEStreamParser((e) => events.push(e));

    // Stream ends without trailing double newline
    parser.feed('event: error\ndata: {"error": "Server timeout"}');
    expect(events).toHaveLength(0);

    parser.flush();
    expect(events).toHaveLength(1);
    expect(events[0].event).toBe("error");
    expect(events[0].data.error).toBe("Server timeout");
  });
});

