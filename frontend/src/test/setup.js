import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock clipboard
Object.assign(navigator, {
  clipboard: {
    writeText: vi.fn().mockImplementation(() => Promise.resolve()),
  },
});

// Mock window.scrollTo
window.HTMLElement.prototype.scrollTo = vi.fn();

