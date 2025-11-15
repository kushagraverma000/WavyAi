"""LLM service for generating responses."""
from typing import Optional, Dict, Any, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class LLMService:
    """Service for LLM interactions."""

    def __init__(self):
        """Initialize LLM service."""
        try:
            model_name = settings.HUGGINGFACE_MODEL
            device = 0 if torch.cuda.is_available() else -1
            logger.info(
                "Loading Hugging Face model",
                model=model_name,
                device="cuda" if device == 0 else "cpu",
            )
            self.generator = pipeline(
                "text-generation",
                model=AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                ),
                tokenizer=AutoTokenizer.from_pretrained(model_name),
                device=device,
            )
            self.max_new_tokens = settings.HUGGINGFACE_MAX_NEW_TOKENS
        except Exception as e:
            logger.error("Failed to initialize Hugging Face model", error=str(e))
            self.generator = None
            self.max_new_tokens = 256

    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        user_type: Optional[str] = None,
        query_intent: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate response using LLM."""
        if not self.generator:
            return self._generate_fallback_response(query, user_type, sources)

        try:
            # Build system prompt based on user type
            system_prompt = self._build_system_prompt(user_type, query_intent)

            # Build user message
            user_message = self._build_user_message(query, context, sources)

            prompt = f"{system_prompt}\n\n{user_message}\n\nAssistant:"

            outputs = self.generator(
                prompt,
                max_new_tokens=self.max_new_tokens,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
            )

            response_text = outputs[0]["generated_text"][len(prompt) :].strip()

            return {
                "text": response_text,
                "confidence": 0.7,
            }
        except Exception as e:
            logger.error("LLM response generation failed", error=str(e), exc_info=True)
            return self._generate_fallback_response(query, user_type, sources)

    def _build_system_prompt(
        self,
        user_type: Optional[str],
        query_intent: Optional[str],
    ) -> str:
        """Build system prompt based on user type."""
        base_prompt = "You are an AI assistant for oceanographic ARGO float data. "
        
        if user_type == "researcher":
            return (
                base_prompt +
                "Provide technical, detailed responses with QC flags, statistics, and citations. "
                "Use scientific terminology and include data quality information."
            )
        elif user_type == "student":
            return (
                base_prompt +
                "Provide educational, easy-to-understand explanations. "
                "Use simple language, provide context, and explain concepts clearly."
            )
        elif user_type == "manager":
            return (
                base_prompt +
                "Provide executive summaries with trends, risks, and recommendations. "
                "Focus on actionable insights and practical implications."
            )
        elif user_type == "fishery":
            return (
                base_prompt +
                "Provide fishing impact analysis with oxygen levels, zones, and seasonal patterns. "
                "Focus on practical implications for fisheries management."
            )
        elif user_type == "shipping":
            return (
                base_prompt +
                "Provide navigation safety reports with current conditions, routes, and alerts. "
                "Focus on safety and operational implications."
            )
        elif user_type == "ngo":
            return (
                base_prompt +
                "Provide environmental overviews with simplified metrics and conservation insights. "
                "Focus on environmental impact and conservation implications."
            )
        else:
            return (
                base_prompt +
                "Provide clear, informative responses about oceanographic data."
            )

    def _build_user_message(
        self,
        query: str,
        context: Optional[str],
        sources: Optional[List[Dict[str, Any]]],
    ) -> str:
        """Build user message with context and sources."""
        message = f"Query: {query}\n\n"
        
        if context:
            message += f"Context: {context}\n\n"
        
        if sources:
            message += "Data Sources:\n"
            for i, source in enumerate(sources[:5], 1):
                message += f"{i}. {source.get('type', 'Unknown')} "
                if source.get('date'):
                    message += f"({source['date']}) "
                if source.get('location'):
                    loc = source['location']
                    message += f"at {loc.get('lat', 0):.2f}°N, {loc.get('lon', 0):.2f}°E"
                message += "\n"
            message += "\n"
        
        message += "Please provide a comprehensive response based on the query and available data sources."
        
        return message

    def _generate_fallback_response(
        self,
        query: str,
        user_type: Optional[str],
        sources: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Generate fallback response when LLM is not available."""
        user_type = user_type or "general"
        
        templates = {
            "researcher": f"Based on the ARGO data analysis, I found information related to '{query}'. " +
                         f"The data includes {len(sources) if sources else 0} profiles with relevant measurements. " +
                         "Technical details with QC flags and statistics are available in the data sources.",
            "student": f"Let me explain '{query}' in simple terms. " +
                      f"I found {len(sources) if sources else 0} data profiles that can help answer your question. " +
                      "Oceanographic data shows various patterns and trends that scientists use to understand ocean processes.",
            "manager": f"Executive Summary: Analysis of '{query}' shows relevant oceanographic data. " +
                      f"Found {len(sources) if sources else 0} data sources. " +
                      "Trends and patterns are available for review, with recommendations based on the data.",
            "fishery": f"Fishing Impact Analysis: '{query}' relates to ocean conditions affecting fisheries. " +
                      f"Found {len(sources) if sources else 0} data profiles with oxygen levels and temperature data. " +
                      "Seasonal patterns and zone recommendations are available.",
            "shipping": f"Navigation Safety Report: '{query}' relates to ocean conditions for shipping. " +
                       f"Found {len(sources) if sources else 0} data sources with current conditions. " +
                       "Route recommendations and safety alerts are available.",
            "ngo": f"Environmental Overview: '{query}' relates to oceanographic conditions. " +
                  f"Found {len(sources) if sources else 0} data sources. " +
                  "Simplified metrics and conservation insights are available.",
            "general": f"Here's what I found about '{query}'. " +
                      f"I found {len(sources) if sources else 0} data profiles with relevant information. " +
                      "The data shows various oceanographic patterns and trends.",
        }
        
        response_text = templates.get(user_type, templates["general"])
        
        return {
            "text": response_text,
            "confidence": 0.7,
        }


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service

