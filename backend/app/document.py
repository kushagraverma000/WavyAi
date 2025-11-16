from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Document:
    """Minimal stand-in for LangChain's Document.

    This avoids pulling in langchain as a dependency while keeping
    the rest of the code's interfaces intact.
    """

    page_content: str
    metadata: Optional[Dict[str, Any]] = None
