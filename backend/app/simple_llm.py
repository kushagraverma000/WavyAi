from __future__ import annotations

from typing import List, Optional

from .document import Document


def answer_with_gemini(question: str, context_docs: Optional[List[Document]] = None) -> str:
    """Simple stub that emulates an LLM answer without external dependencies.

    This keeps the backend fully runnable in lightweight environments. It
    just echoes the question and, if present, a short context summary.
    """
    question = (question or "").strip() or "Summarize the ARGO data in simple language."

    context_text = "\n\n".join(doc.page_content for doc in (context_docs or []))
    if context_text:
        return (
            "(Prototype answer without a real LLM)\n" +
            f"Question: {question}\n\n" +
            "Context summary:\n" + context_text
        )

    return (
        "(Prototype answer without a real LLM)\n" +
        f"Question: {question}\n\n" +
        "No additional ARGO context was available."
    )
