from functools import lru_cache
from typing import List, Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from .config import settings
from .document import Document


@lru_cache
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a singleton Gemini embeddings client (LangChain wrapper)."""
    if not settings.gemini_api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Set GOOGLE_API_KEY or WAVYAI_GEMINI_API_KEY."
        )
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.gemini_api_key,
    )


@lru_cache
def get_chat_model() -> ChatGoogleGenerativeAI:
    """Return a singleton Gemini chat model (LangChain wrapper)."""
    if not settings.gemini_api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Set GOOGLE_API_KEY or WAVYAI_GEMINI_API_KEY."
        )
    return ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.gemini_api_key,
        temperature=0.3,
    )


def answer_with_gemini(question: str, context_docs: Optional[List[Document]] = None) -> str:
    """Use LangChain+Gemini to answer a question.

    - `context_docs` are optional retrieved documents (e.g., from FAISS/Postgres).
    - Always goes through LangChain's chat wrapper, never direct Gemini calls.
    """
    chat = get_chat_model()

    system_prompt = (
        "You are WavyAI, an assistant that explains ARGO ocean data in simple, clear language. "
        "Use the provided context when available, and avoid making up data."
    )

    context_text = "\n\n".join(doc.page_content for doc in context_docs or [])

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt + "\n\nContext:\n{context}"),
            ("human", "Question: {question}"),
        ]
    )

    chain = prompt | chat
    result = chain.invoke({"question": question, "context": context_text or "(no extra context)"})
    return result.content or "I could not generate a response."
