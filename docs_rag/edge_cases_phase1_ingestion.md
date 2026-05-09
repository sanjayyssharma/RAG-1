# Edge Cases: Phase 1 (Data Ingestion & Processing)

This document outlines the potential edge cases and handling strategies for Phase 1 of the Mutual Fund FAQ Assistant architecture.

## 1. Scraping & Data Fetching Edge Cases
*   **Dynamic Content / Client-Side Rendering:** HTML parsers (like BeautifulSoup) may fail to extract data if Groww uses heavy JavaScript to render the factsheets or tables.
    *   *Mitigation:* Use headless browsers (e.g., Playwright or Selenium) or Langchain's WebBaseLoader with JS execution capabilities.
*   **Rate Limiting & Blocking:** Groww might block or rate-limit the scraping bot if fetching too frequently.
    *   *Mitigation:* Implement exponential backoff, user-agent rotation, or respectful crawl delays.
*   **Website Structural Changes:** The HTML DOM structure (CSS classes, div IDs) of the 5 URLs might change, breaking the HTML parser.
    *   *Mitigation:* Use robust, semantic HTML parsing rather than relying on brittle CSS selectors. Set up alerts for scraping failures.

## 2. Extraction & Cleaning Edge Cases
*   **Malformed Tabular Data:** Financial tables (like expense ratios or returns) might be merged or nested, leading to garbled text extraction.
    *   *Mitigation:* Implement specific table-extraction logic or Markdown conversion tools to preserve structural relationships.
*   **Extraneous Ads and Pop-ups:** Unwanted text from banners or navigation menus getting included in the corpus.
    *   *Mitigation:* Define strict bounding boxes or target specific HTML tags (`<article>`, `<main>`) to isolate the core content.

## 3. Chunking & Embedding Edge Cases
*   **Context Fragmentation:** A section like "Holdings" or "Exit Load" might be cut in half if relying strictly on character counts.
    *   *Mitigation:* Strictly use Markdown Header-based Chunking (`MarkdownHeaderTextSplitter`) so that all content under a specific `##` or `###` header is grouped as a single chunk, preserving its semantic boundary.
*   **Embedding Out-of-Vocabulary (OOV) Terms:** Specific financial jargon might not be well-represented in the chosen embedding model.
    *   *Mitigation:* Evaluate embedding models against domain-specific queries; consider fine-tuning if similarity scores are consistently poor.
