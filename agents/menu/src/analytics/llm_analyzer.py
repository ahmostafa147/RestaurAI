import os
import json
from typing import Dict, List, Any, Optional

try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
except ImportError as e:
    raise ImportError(
        "LangChain dependencies are required but not installed. "
        "Please install them with: pip install langchain langchain-anthropic"
    ) from e

try:
    from dotenv import load_dotenv
except ImportError as e:
    raise ImportError(
        "python-dotenv is required but not installed. "
        "Please install it with: pip install python-dotenv"
    ) from e

from .models import LLMInsights, LLMErrorResponse


class LLMAnalyzer:
    """LLM-based analyzer for menu insights using Claude API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Anthropic API key"""
        # Load .env file from project root (3 levels up from this file)
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..','..', '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        # Get API key from parameter or environment
        resolved_api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        model = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')  # Default to Claude 3.5 Sonnet
        if not resolved_api_key:
            raise ValueError(
                "Anthropic API key is required. Please set ANTHROPIC_API_KEY environment variable "
                "or provide api_key parameter."
            )
        
        self.llm = ChatAnthropic(
            model=model,
            api_key=resolved_api_key,
            max_tokens=4000
        )
        self.parser = PydanticOutputParser(pydantic_object=LLMInsights)
        
        # Add direct Anthropic client for server compatibility
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=resolved_api_key)
            self.model = model
        except ImportError:
            raise ImportError("Missing anthropic dependency. Please install anthropic package.")
    
    
    
    def generate_llm_insights(self, menu_data: Dict, review_analytics: Dict, algorithmic_results: Dict) -> LLMInsights:
        """Generate comprehensive LLM insights using LangChain with structured output"""
        
        # Prepare context for LLM
        context = self._prepare_llm_context(menu_data, review_analytics, algorithmic_results)
        
        # Create prompt template with LangChain
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are a restaurant analytics expert with deep knowledge of food preparation, cooking techniques, and kitchen operations. 
            
            Analyze the provided menu and operational data to generate comprehensive insights about:
            1. Preparation time estimates for each menu item based on ingredients, cooking methods, and complexity
            2. Day-part categorization for each menu item based on their hourly ordering patterns  
            3. Overall day-part analysis for the restaurant
            4. Trend observations and patterns
            5. Actionable suggestions for menu optimization
            6. Integration of customer sentiment from reviews
            
            Consider:
            - Ingredient preparation time (chopping, marinating, etc.)
            - Cooking method complexity (grilling vs. frying vs. baking)
            - Assembly time for complex dishes
            - Kitchen workflow and parallel processing capabilities
            - Customer sentiment and review patterns
            - Business optimization opportunities
            
            IMPORTANT: You MUST provide ALL required fields in your response.
            
            {format_instructions}"""),
            ("human", """Analyze this restaurant data and provide comprehensive insights.

MANDATORY: You MUST include all required fields in your response, including:
- preparation_insights: Dictionary of preparation insights for each menu item
- day_part_analysis: Overall and per-item day-part analysis
- trend_observations: List of trend observations
- actionable_suggestions: List of actionable suggestions for optimization
- sentiment_integration: Integration of customer sentiment analysis

Context:
{context}""")
        ])
        
        # Create the chain with structured output parsing
        chain = prompt_template | self.llm | self.parser
        
        try:
            # Execute the chain with context
            result = chain.invoke({
                "context": context,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            return result
            
        except Exception as e:
            return LLMErrorResponse(
                error=f"LLM analysis failed: {str(e)}"
            )
    
    def _prepare_llm_context(self, menu_data: Dict, review_analytics: Dict, algorithmic_results: Dict) -> str:
        """Prepare context string for LLM analysis"""
        
        # Menu items summary with detailed ingredient information
        menu_summary = []
        for category, items in menu_data.items():
            for item in items:
                ingredients_detail = []
                for ing in item.get('ingredients', []):
                    ingredients_detail.append({
                        'name': ing.get('name'),
                        'quantity': ing.get('quantity'),
                        'unit': ing.get('unit'),
                        'cost': ing.get('cost', 0),
                        'supplier': ing.get('supplier', '')
                    })
                
                menu_summary.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'price': item.get('price'),
                    'category': category,
                    'description': item.get('description', ''),
                    'ingredients': ingredients_detail
                })
        
        # Popularity metrics
        popularity = algorithmic_results.get('popularity_metrics', {})
        profit_margins = algorithmic_results.get('profit_margins', {})
        temporal = algorithmic_results.get('temporal_patterns', {})
        
        # Review analytics summary
        review_summary = {}
        if review_analytics:
            menu_analytics = review_analytics.get('menu_analytics', {})
            review_summary = {
                'top_praised_items': menu_analytics.get('top_praised', []),
                'top_criticized_items': menu_analytics.get('top_criticized', []),
                'aspect_analysis': menu_analytics.get('aspect_analysis', {}),
                'items_mentioned': [item.get('name') for item in menu_analytics.get('items', [])]
            }
        
        context = f"""
MENU ITEMS:
{json.dumps(menu_summary, indent=2)}

POPULARITY METRICS:
{json.dumps(popularity, indent=2)}

PROFIT MARGINS:
{json.dumps(profit_margins, indent=2)}

TEMPORAL PATTERNS:
Peak hour: {temporal.get('peak_hour')}
Peak day: {temporal.get('peak_day')}
Total revenue: {temporal.get('total_revenue')}
Average order value: {temporal.get('average_order_value')}

REVIEW ANALYTICS:
{json.dumps(review_summary, indent=2)}
"""
        
        return context
    
    def analyze_item_sentiment(self, item_name: str, review_analytics: Dict) -> Dict[str, Any]:
        """Analyze sentiment for a specific menu item from review data"""
        if not review_analytics:
            return {'sentiment_score': 0, 'mentions': 0, 'feedback': []}
        
        menu_analytics = review_analytics.get('menu_analytics', {})
        items = menu_analytics.get('items', [])
        
        for item in items:
            if item.get('name', '').lower() == item_name.lower():
                return {
                    'sentiment_score': item.get('sentiment_score', 0),
                    'mentions': item.get('mention_count', 0),
                    'positive_count': item.get('positive_count', 0),
                    'negative_count': item.get('negative_count', 0),
                    'aspects': item.get('aspects', {}),
                    'feedback': []
                }
        
        return {'sentiment_score': 0, 'mentions': 0, 'feedback': []}
