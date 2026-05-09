# Phase 3.2: Frontend UI Design Specification

This document outlines the design architecture, visual aesthetics, and API integration logic for the Mutual Fund RAG Assistant's user interface.

## 1. Visual Aesthetics & Theme
To establish a premium, trustworthy, and modern feel, the application utilizes a dark-mode glassmorphism theme.
*   **Background:** Deep navy/almost black (`#0B0F19`) with subtle radial gradients (e.g., `#3B82F6` with low opacity) to add depth.
*   **Panels:** The main chat container utilizes CSS glassmorphism (`backdrop-filter: blur(12px)`) layered over a semi-transparent dark background.
*   **Typography:** Google's **Inter** font is used globally for high readability.
*   **Accent Colors:** Vibrant blue (`#3B82F6`) for interactive elements like the send button and user chat bubbles.
*   **Animations:** Smooth fade-in transitions for chat bubbles and a bouncing-dot animation for the loading state.

## 2. Core UI Components

### Header & Compliance
*   **Title:** "HDFC Mutual Fund Assistant" displayed with a subtle text gradient.
*   **Disclaimer Banner:** A strict compliance requirement. A pill-shaped amber badge (`#FBBF24`) stating exactly: **"Facts-only. No investment advice."** This is prominently displayed to set user expectations immediately.

### Chat Interface
*   **Suggested Queries:** Three clickable, pill-shaped buttons above the input field to reduce friction for new users. 
    1. *"What is the exit load for HDFC Flexi Cap?"*
    2. *"What are the top holdings of HDFC Mid Cap?"*
    3. *"Should I invest in HDFC Large Cap?"* (Intentionally triggers the refusal guardrail).
*   **Message Bubbles:** 
    *   *User:* Aligned right, blue background.
    *   *Bot:* Aligned left, subtle transparent background.

## 3. Data Integration & API Logic
The frontend communicates statelessly with the Python FastAPI backend.

### Request Flow
1.  User submits a text query via the input box.
2.  The UI instantly appends the user's message bubble and displays a bouncing-dot loading indicator.
3.  A `POST` request is sent via `fetch` to the backend:
    ```json
    POST http://localhost:8000/chat
    {
      "query": "user message string"
    }
    ```

### Response Handling
The FastAPI backend returns a structured JSON payload. The UI is designed to gracefully parse and render each component of this payload within a single bot message bubble:

```json
{
  "answer": "The exit load is 1%.",
  "source": "https://groww.in/...",
  "footer": "Last updated from sources: 10 May 2026"
}
```

*   **`answer` (Required):** Rendered as the primary text content of the bot's message bubble.
*   **`source` (Optional):** If present and not null, it is rendered below the answer as a clickable hyperlink styled as *Source: Official Document*.
*   **`footer` (Optional):** If present and not null, it is rendered at the very bottom of the bubble in a smaller, muted font, visually separated by a subtle border line.

## 4. Error Handling
*   If the FastAPI backend is offline or returns an HTTP 500 error, the UI catches the exception and renders a local error bubble: *"Connection Error: Ensure the FastAPI backend is running on port 8000."*
*   During an error, the input field is automatically re-enabled to prevent the UI from locking up.
