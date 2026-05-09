# Edge Cases: Phase 2 (RAG Pipeline & Core Logic)

This document outlines the potential edge cases and handling strategies for Phase 2 of the Mutual Fund FAQ Assistant architecture.

## 1. Query Processing Edge Cases
*   **Mixed Intent Queries:** A user asks a factual question combined with an advisory one (e.g., "What is the exit load, and should I buy this?").
    *   *Mitigation:* The intent classifier should flag the advisory portion and trigger the standard refusal response, or answer the factual part and append a refusal for the advisory part.
*   **Vague or Ambiguous Queries:** Queries that don't specify the scheme (e.g., "What is the minimum SIP amount?").
    *   *Mitigation:* Prompt the user to clarify which of the 5 schemes they are referring to, or if the policy is uniform across all 5, state the general policy clearly.
*   **Out of Scope Queries:** Queries about schemes not included in the 5 specified URLs (e.g., "Tell me about SBI Bluechip Fund").
    *   *Mitigation:* The VectorDB search will yield low confidence scores. Trigger a fallback: "I only have information on the 5 supported HDFC schemes."

## 2. Retrieval Edge Cases
*   **Conflicting Information:** A scheme might have updated facts that contradict older FAQs still present on the same page.
    *   *Mitigation:* Ensure the scraping logic grabs the most recently updated sections or prioritize tables over raw text.
*   **Zero Relevant Documents:** The user asks a completely unrelated factual question (e.g., "What is the weather?").
    *   *Mitigation:* Strict similarity score thresholds. If the top-k results are below the threshold, return a polite "Data Not Found / Out of Scope" message.

## 3. LLM Generation Edge Cases
*   **Hallucinations on Edge Facts:** The LLM might try to fill in blanks if the retrieved context is missing a specific detail.
    *   *Mitigation:* Set temperature to 0.0. Use strict prompt constraints: "If the context does not contain the answer, reply ONLY with 'I do not have this information'."
*   **Constraint Violations:** The LLM generates a response longer than 3 sentences.
    *   *Mitigation:* Implement a post-generation validation check. If it exceeds 3 sentences, either truncate intelligently or trigger a fallback regeneration.
*   **Missing Footer/Source:** The LLM fails to format the source link and updated date properly.
    *   *Mitigation:* Handle the footer append programmatically in the backend code (Phase 3) rather than relying on the LLM to generate it.
