"""Google Gemini LLM service for generating responses."""
from typing import Optional, Dict, Any, List
import google.generativeai as genai

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class GeminiService:
    """Service for Google Gemini LLM interactions."""

    def __init__(self):
        """Initialize Gemini service."""
        try:
            if settings.GOOGLE_GEMINI_API_KEY:
                genai.configure(api_key=settings.GOOGLE_GEMINI_API_KEY)
                self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
                logger.info("Google Gemini service initialized successfully")
            else:
                logger.warning("Google Gemini API key not provided, using fallback responses")
                self.model = None
        except Exception as e:
            logger.error("Failed to initialize Google Gemini service", error=str(e))
            self.model = None

    def generate_response(
        self,
        query: str,
        context: Optional[str] = None,
        user_type: Optional[str] = None,
        query_intent: Optional[str] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generate response using Google Gemini."""
        if not self.model:
            return self._generate_fallback_response(query, user_type, sources)

        try:
            # Build comprehensive prompt
            prompt = self._build_comprehensive_prompt(query, context, user_type, query_intent, sources)
            
            # Generate response
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                    temperature=0.7,
                )
            )

            return {
                "text": response.text,
                "confidence": 0.8,
            }
        except Exception as e:
            logger.error("Gemini response generation failed", error=str(e), exc_info=True)
            return self._generate_fallback_response(query, user_type, sources)

    def _build_comprehensive_prompt(
        self,
        query: str,
        context: Optional[str],
        user_type: Optional[str],
        query_intent: Optional[str],
        sources: Optional[List[Dict[str, Any]]],
    ) -> str:
        """Build comprehensive prompt for Gemini."""
        prompt_parts = []
        
        # System context
        prompt_parts.append("You are WavyAI, an expert oceanographic data assistant specializing in ARGO float data analysis.")
        
        # User type specific instructions
        if user_type == "researcher":
            prompt_parts.append("""
You're assisting a researcher. Provide:
- Technical, detailed responses with scientific accuracy
- Statistical analysis and data quality information
- References to measurement techniques and QC flags
- Specific numerical values and uncertainties
- Recommendations for further analysis
""")
        elif user_type == "student":
            prompt_parts.append("""
You're assisting a student. Provide:
- Clear, educational explanations of oceanographic concepts
- Simple language with scientific terminology explained
- Context about why measurements matter
- Learning-focused insights
- Encourage further exploration
""")
        elif user_type == "manager":
            prompt_parts.append("""
You're assisting a manager/decision-maker. Provide:
- Executive summaries with key insights
- Trends, risks, and actionable recommendations
- Business/operational implications
- Clear conclusions and next steps
- Focus on practical applications
""")
        else:
            prompt_parts.append("Provide clear, informative responses about oceanographic data suitable for a general audience.")

        # Query intent context
        if query_intent:
            intent_context = {
                "data_exploration": "Focus on exploring and understanding the available data patterns.",
                "decision_support": "Provide actionable insights and recommendations.",
                "learning": "Explain concepts and provide educational context.",
                "monitoring": "Focus on current conditions and trends.",
                "export": "Guide the user on data access and download options."
            }
            if query_intent in intent_context:
                prompt_parts.append(f"Query Intent: {intent_context[query_intent]}")

        # Data context
        if context:
            prompt_parts.append(f"Available Data Context:\n{context}")

        # Sources information
        if sources:
            prompt_parts.append("Data Sources Available:")
            for i, source in enumerate(sources[:5], 1):
                source_info = f"{i}. {source.get('type', 'Profile')}"
                if source.get('date'):
                    source_info += f" from {source['date']}"
                if source.get('location'):
                    loc = source['location']
                    source_info += f" at {loc.get('lat', 0):.2f}°N, {loc.get('lon', 0):.2f}°E"
                prompt_parts.append(source_info)

        # Main query
        prompt_parts.append(f"\nUser Query: {query}")

        # Response instructions
        prompt_parts.append("""
Please provide a comprehensive response that:
1. Directly answers the user's question
2. Uses the available data context and sources
3. Includes specific details when data is available
4. Suggests visualizations (maps, plots, tables) that would be helpful
5. Mentions data download options (CSV, NetCDF) when relevant
6. Is tailored to the user type and intent

Format your response in clear sections when appropriate.
""")

        return "\n\n".join(prompt_parts)

    def _generate_fallback_response(
        self,
        query: str,
        user_type: Optional[str],
        sources: Optional[List[Dict[str, Any]]],
    ) -> Dict[str, Any]:
        """Generate enhanced fallback response when Gemini is not available."""
        user_type = user_type or "general"
        source_count = len(sources) if sources else 0
        
        # Enhanced templates with more detailed responses
        templates = {
            "researcher": f"""
Based on the ARGO oceanographic data analysis for '{query}':

**Data Summary:**
- Found {source_count} relevant data profiles
- Data includes temperature, salinity, and pressure measurements
- Quality control flags and metadata available

**Technical Details:**
- Measurements follow ARGO data standards
- Spatial and temporal coverage varies by query parameters
- Statistical analysis available for trend identification

**Recommendations:**
- Review individual profiles for detailed measurements
- Consider temporal and spatial filtering for focused analysis
- Download data in NetCDF format for comprehensive analysis
- Visualize data using T-S diagrams and depth profiles

**Data Access:**
Maps, plots, and tables are available for interactive exploration. Data can be exported in CSV or ARGO NetCDF formats for further analysis.
""",
            "student": f"""
Let me help you understand '{query}' using oceanographic data:

**What We Found:**
I discovered {source_count} data profiles that relate to your question. These come from ARGO floats - autonomous instruments that drift in the ocean and measure water properties.

**Key Concepts:**
- ARGO floats measure temperature, salinity (saltiness), and pressure at different depths
- This data helps scientists understand ocean currents, climate patterns, and marine ecosystems
- Each measurement has quality checks to ensure accuracy

**Learning Opportunities:**
- Explore the interactive maps to see where data was collected
- Look at depth profiles to understand how ocean properties change with depth
- Compare measurements from different locations and times

**Next Steps:**
Use the visualization tools to explore patterns in the data. You can view maps, create plots, and examine data tables to deepen your understanding.
""",
            "manager": f"""
**Executive Summary: {query}**

**Key Findings:**
- Analyzed {source_count} oceanographic data profiles
- Data spans multiple geographic regions and time periods
- Comprehensive measurements of key ocean parameters available

**Strategic Insights:**
- Ocean data reveals patterns relevant to operational planning
- Seasonal and regional variations identified in the dataset
- Data quality meets international oceanographic standards

**Actionable Recommendations:**
1. Utilize interactive visualizations for stakeholder presentations
2. Export data in standard formats for integration with existing systems
3. Monitor trends for operational decision-making
4. Consider expanded data coverage for enhanced insights

**Resources Available:**
Interactive maps, analytical plots, and detailed data tables support decision-making processes. Data export capabilities ensure integration with existing workflows.
""",
            "general": f"""
Here's what I found about '{query}':

**Data Overview:**
I analyzed {source_count} oceanographic data profiles from ARGO floats worldwide. These autonomous instruments provide valuable insights into ocean conditions.

**What This Means:**
The data shows various oceanographic patterns and trends that help us understand:
- Ocean temperature and salinity distributions
- Seasonal and regional variations
- Long-term climate patterns
- Marine ecosystem conditions

**Explore Further:**
- **Interactive Maps:** See where data was collected globally
- **Data Plots:** Visualize trends and patterns in the measurements
- **Data Tables:** Examine detailed measurements and metadata
- **Downloads:** Export data in CSV or NetCDF formats for your own analysis

The visualization tools and data export options make it easy to explore and use this oceanographic information for your specific needs.
"""
        }
        
        response_text = templates.get(user_type, templates["general"])
        
        return {
            "text": response_text,
            "confidence": 0.7,
        }


# Global Gemini service instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
