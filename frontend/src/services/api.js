/**
 * Standardized HTTP API client with timeout, headers, and error handling.
 */

import { getSessionId } from "../utils/storage";

export class ApiError extends Error {
  constructor(message, status = 500, details = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export async function request(url, options = {}) {
  const sessionId = getSessionId();
  const defaultHeaders = {
    "Content-Type": "application/json",
    "X-Session-ID": sessionId,
  };

  const headers = { ...defaultHeaders, ...(options.headers || {}) };
  const timeoutMs = options.timeoutMs || 25000;

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const signal = options.signal || controller.signal;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch (e) {
        errorData = { message: response.statusText || `HTTP Error ${response.status}` };
      }

      const errorMessage =
        errorData.detail ||
        (errorData.error && errorData.error.message) ||
        errorData.message ||
        `Request failed with status ${response.status}`;

      throw new ApiError(errorMessage, response.status, errorData);
    }

    return response;
  } catch (error) {
    clearTimeout(timeoutId);

    if (error.name === "AbortError") {
      throw new ApiError("Request timed out. Please check your connection and try again.", 408);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error.message || "Network error. Please try again.", 0);
  }
}

