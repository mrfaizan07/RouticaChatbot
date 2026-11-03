/**
 * Safe markdown parser and HTML sanitizer for chat messages.
 */

import DOMPurify from "dompurify";

/**
 * Escapes raw HTML characters before markdown processing.
 */
function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Converts standard Markdown to HTML with strict sanitization.
 */
export function formatMarkdown(text) {
  if (!text || typeof text !== "string") return "";

  // 1. Separate code blocks to protect them from inner markdown formatting
  const codeBlocks = [];
  let processed = text.replace(/```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
    const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
    codeBlocks.push({
      lang: lang.trim(),
      code: escapeHtml(code.trim()),
    });
    return placeholder;
  });

  // 1.5 Convert Markdown tables into clean, mobile-friendly structured bullet points
  processed = processed.replace(
    /(?:^|\n)(\|[^\n]+\|\n\|[\s\-:|]+\|\n(?:\|[^\n]+\|(?:\n|$))+)/g,
    (tableMatch) => {
      const lines = tableMatch.trim().split("\n");
      if (lines.length < 3) return tableMatch;

      const parseRow = (line) =>
        line
          .split("|")
          .map((c) => c.trim())
          .filter((c, i, arr) => i > 0 && i < arr.length - 1);

      const headers = parseRow(lines[0]);
      const rows = lines.slice(2).map(parseRow);

      let bulletOutput = "\n\n";
      rows.forEach((row) => {
        if (!row || row.length === 0) return;
        if (row.length === 2) {
          bulletOutput += `* **${row[0]}:** ${row[1]}\n`;
        } else if (row.length >= 3) {
          const featureName = row[0];
          const col1Name = headers[1] || "Option 1";
          const col2Name = headers[2] || "Option 2";
          bulletOutput += `* **${featureName}:**\n  - **${col1Name}:** ${row[1]}\n  - **${col2Name}:** ${row[2]}\n`;
          for (let i = 3; i < row.length; i++) {
            bulletOutput += `  - **${headers[i] || `Option ${i}`}:** ${row[i]}\n`;
          }
        } else {
          bulletOutput += `* ${row.join(" • ")}\n`;
        }
      });
      return bulletOutput + "\n";
    }
  );

  // 2. Inline code
  processed = processed.replace(/`([^`]+)`/g, (match, code) => {
    return `<code>${escapeHtml(code)}</code>`;
  });

  // 3. Headings (# h1 to #### h4)
  processed = processed.replace(/^#### (.*$)/gim, '<h4 class="font-semibold text-slate-800 text-sm mt-3 mb-1">$1</h4>');
  processed = processed.replace(/^### (.*$)/gim, '<h3 class="font-semibold text-slate-900 text-base mt-3 mb-1">$1</h3>');
  processed = processed.replace(/^## (.*$)/gim, '<h2 class="font-bold text-slate-900 text-lg mt-4 mb-2">$1</h2>');
  processed = processed.replace(/^# (.*$)/gim, '<h1 class="font-extrabold text-slate-900 text-xl mt-4 mb-2">$1</h1>');

  // 4. Blockquotes
  processed = processed.replace(/^\> (.*$)/gim, '<blockquote class="border-l-4 border-routica-500 pl-3 italic text-slate-600 my-2">$1</blockquote>');

  // 5. Bold & Italic
  processed = processed.replace(/\*\*\*(.*?)\*\*\*/g, "<strong><em>$1</em></strong>");
  processed = processed.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  processed = processed.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // 6. Markdown Links [text](url) - strictly sanitize protocol
  processed = processed.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (match, linkText, url) => {
    const cleanUrl = url.trim();
    // Only allow http:// and https:// URLs
    if (/^https?:\/\//i.test(cleanUrl)) {
      return `<a href="${cleanUrl}" target="_blank" rel="noopener noreferrer" class="text-routica-600 underline hover:text-routica-800 font-medium">${linkText}</a>`;
    }
    return linkText;
  });

  // 7. Unordered Lists (Sub-items and top-level items)
  processed = processed.replace(/(?:^|\n)\s{2,}[*-] (.*)/g, (match, item) => {
    return `\n<li class="ml-8 list-circle text-slate-600 text-[13px] my-0.5">${item}</li>`;
  });
  processed = processed.replace(/(?:^|\n)[*-] (.*)/g, (match, item) => {
    return `\n<li class="ml-4 list-disc text-slate-800 my-1">${item}</li>`;
  });

  // 8. Ordered Lists (1. item)
  processed = processed.replace(/(?:^|\n)\d+\. (.*)/g, (match, item) => {
    return `\n<li class="ml-4 list-decimal text-slate-700">${item}</li>`;
  });

  // 9. Paragraphs and line breaks
  const paragraphs = processed.split(/\n{2,}/);
  processed = paragraphs
    .map((p) => {
      const trimmed = p.trim();
      if (!trimmed) return "";
      if (
        trimmed.startsWith("<h") ||
        trimmed.startsWith("<li") ||
        trimmed.startsWith("<blockquote") ||
        trimmed.startsWith("__CODE_BLOCK_")
      ) {
        return trimmed;
      }
      return `<p class="mb-3 leading-relaxed text-slate-800">${trimmed.replace(/\n/g, "<br/>")}</p>`;
    })
    .join("\n");

  // 10. Restore code blocks with syntax wrapper and copy button capability
  codeBlocks.forEach((block, idx) => {
    const placeholder = `__CODE_BLOCK_${idx}__`;
    const htmlBlock = `
      <div class="relative my-3 rounded-lg overflow-hidden bg-slate-900 border border-slate-800 text-xs">
        ${block.lang ? `<div class="bg-slate-800/80 px-3 py-1 text-slate-400 font-mono text-[11px] uppercase">${block.lang}</div>` : ""}
        <pre class="p-3 overflow-x-auto text-slate-100 font-mono"><code>${block.code}</code></pre>
      </div>`;
    processed = processed.replace(placeholder, htmlBlock);
  });

  // 11. Final strict DOMPurify sanitization
  return DOMPurify.sanitize(processed, {
    ALLOWED_TAGS: [
      "p", "br", "strong", "em", "h1", "h2", "h3", "h4",
      "ul", "ol", "li", "code", "pre", "blockquote", "a", "div", "span",
      "table", "thead", "tbody", "tr", "th", "td"
    ],
    ALLOWED_ATTR: ["href", "target", "rel", "class"],
  });
}

