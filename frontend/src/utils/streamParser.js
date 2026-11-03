/**
 * Resilient Server-Sent Events (SSE) stream buffer parser.
 * Handles split network chunks, multiline data, UTF-8 boundaries, and typed events.
 */

export class SSEStreamParser {
  constructor(onEvent) {
    this.onEvent = onEvent;
    this.buffer = "";
    this.currentEvent = "message";
    this.currentData = [];
  }

  /**
   * Feeds a decoded text chunk from the network into the accumulator buffer.
   * Dispatches events when double newline delimiters are reached.
   */
  feed(chunk) {
    if (!chunk) return;
    this.buffer += chunk;

    // Normalize Windows CRLF to LF
    this.buffer = this.buffer.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

    let lineEndIdx;
    while ((lineEndIdx = this.buffer.indexOf("\n")) !== -1) {
      const line = this.buffer.slice(0, lineEndIdx);
      this.buffer = this.buffer.slice(lineEndIdx + 1);

      if (line.trim() === "") {
        // Empty line indicates event boundary
        this._dispatch();
      } else if (line.startsWith("event:")) {
        this.currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        this.currentData.push(line.slice(5).trim());
      } else if (line.startsWith(":")) {
        // SSE comment / heartbeat ping — ignore
      }
    }
  }

  /**
   * Flushes any remaining content in the buffer when the network stream closes.
   */
  flush() {
    if (this.buffer.trim().length > 0) {
      const lines = this.buffer.split("\n");
      for (const line of lines) {
        if (line.startsWith("event:")) {
          this.currentEvent = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          this.currentData.push(line.slice(5).trim());
        }
      }
      this._dispatch();
    } else if (this.currentData.length > 0) {
      this._dispatch();
    }
    this.buffer = "";
  }

  _dispatch() {
    if (this.currentData.length === 0 && this.currentEvent === "message") {
      return;
    }

    const rawData = this.currentData.join("\n");
    let parsedData = rawData;

    try {
      if (rawData.startsWith("{") || rawData.startsWith("[")) {
        parsedData = JSON.parse(rawData);
      }
    } catch (e) {
      // Keep as string if not valid JSON
    }

    if (this.onEvent) {
      try {
        this.onEvent({
          event: this.currentEvent,
          data: parsedData,
          raw: rawData,
        });
      } catch (err) {
        console.error("Error in SSE event handler:", err);
      }
    }

    // Reset for next event
    this.currentEvent = "message";
    this.currentData = [];
  }
}

/**
 * Consumes a fetch Response body stream with an SSEStreamParser.
 */
export async function consumeSSEStream(response, onEvent, signal) {
  if (!response.body) {
    throw new Error("ReadableStream not supported by this browser environment");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");
  const parser = new SSEStreamParser(onEvent);

  try {
    while (true) {
      if (signal && signal.aborted) {
        await reader.cancel();
        break;
      }

      const { done, value } = await reader.read();
      if (done) break;

      const text = decoder.decode(value, { stream: true });
      parser.feed(text);
    }
  } finally {
    parser.flush();
    reader.releaseLock();
  }
}

