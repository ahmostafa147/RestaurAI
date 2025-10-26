"""
LLM-based analysis for ingredient management using LangChain and Anthropic Claude
"""

import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

try:
    from langchain_anthropic import ChatAnthropic
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from dotenv import load_dotenv
except ImportError as e:
    raise ImportError(f"Missing required dependencies: {e}. Please install langchain, langchain-anthropic, and python-dotenv.")

from .models import LLMInsights, LLMErrorResponse


class LLMAnalyzer:
    """LLM-based analysis for ingredient insights and recommendations"""
    
    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Initialize the LLM analyzer
        
        Args:
            anthropic_api_key: Anthropic API key. If None, will try to load from .env
        """
        # Load environment variables
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', '..','..', '.env')
        load_dotenv(env_path)
        
        # Get API key
        api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        model = os.getenv('CLAUDE_MODEL')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not provided and not found in environment variables")
        
        # Initialize LLM with structured output parser
        self.parser = PydanticOutputParser(pydantic_object=LLMInsights)
        
        self.llm = ChatAnthropic(
            model=model,
            api_key=api_key,
            temperature=0.3
        )
        
        # Add direct Anthropic client for server compatibility
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
            self.model = model
        except ImportError:
            raise ImportError("Missing anthropic dependency. Please install anthropic package.")
    
    def generate_llm_insights(self, consumption_data: Dict[str, Any], 
                            inventory_data: Dict[str, Any], 
                            menu_data: Dict[str, Any]) -> LLMInsights:
        """
        Generate LLM insights for ingredient management
        
        Args:
            consumption_data: Output from ConsumptionAnalyzer
            inventory_data: Current inventory information
            menu_data: Menu items and their ingredients
            
        Returns:
            LLMInsights object with recommendations and analysis
        """
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(consumption_data, inventory_data, menu_data)
            
            # Create prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """You are an expert restaurant inventory manager. Analyze the provided ingredient consumption data, current inventory levels, and menu information to provide actionable insights for inventory management.

Your analysis should focus on:
1. Reorder suggestions with optimal quantities and timing
2. Identifying critical ingredients that could disrupt operations
3. Cost optimization opportunities
4. Seasonal and temporal trends
5. Supplier performance insights
6. Inventory turnover optimization

Provide specific, actionable recommendations based on the data. Consider factors like:
- Usage volatility and predictability
- Cost impact of stockouts
- Storage constraints
- Supplier lead times
- Menu item popularity
- Seasonal variations

{format_instructions}"""),
                ("human", """Please analyze the following restaurant inventory data and provide comprehensive insights:

{context}""")
            ])
            
            # Create the chain
            chain = prompt_template | self.llm | self.parser
            
            # Generate insights
            insights = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "context": context
            })
            
            return insights
            
        except Exception as e:
            # Return error response
            return LLMInsights(
                reorder_suggestions=[],
                critical_items=[],
                optimization_tips=[f"Error generating insights: {str(e)}"],
                seasonal_recommendations=[],
                cost_optimization_suggestions=[],
                supplier_analysis={},
                inventory_turnover_insights=[]
            )
    
    def _prepare_llm_context(self, consumption_data: Dict[str, Any], 
                           inventory_data: Dict[str, Any], 
                           menu_data: Dict[str, Any]) -> str:
        """
        Prepare context string for LLM analysis
        
        Args:
            consumption_data: Consumption analysis results
            inventory_data: Current inventory data
            menu_data: Menu items and ingredients
            
        Returns:
            Formatted context string for LLM
        """
        context_parts = []
        
        # Add consumption analysis
        context_parts.append("=== CONSUMPTION ANALYSIS ===")
        if 'per_ingredient' in consumption_data:
            for ingredient_id, data in consumption_data['per_ingredient'].items():
                context_parts.append(f"""
Ingredient ID {ingredient_id}:
- Average daily usage: {data.get('avg_daily_usage', 0):.2f} units
- Average hourly usage: {data.get('avg_hourly_usage', 0):.2f} units
- Usage volatility: {data.get('usage_volatility', 0):.2f}
- Peak usage hours: {data.get('peak_hours', [])}
- Peak usage days: {data.get('peak_days', [])}
- Used in menu items: {', '.join(data.get('menu_items', []))}
- Total usage events: {data.get('usage_events_count', 0)}
- Analysis period: {data.get('time_span_days', 0)} days
""")
        
        # Add current inventory
        context_parts.append("\n=== CURRENT INVENTORY ===")
        if 'inventory' in inventory_data:
            for ingredient in inventory_data['inventory']:
                context_parts.append(f"""
Ingredient: {ingredient.get('name', 'Unknown')} (ID: {ingredient.get('id', 'N/A')})
- Current stock: {ingredient.get('quantity', 0)} {ingredient.get('unit', 'units')}
- Cost per unit: ${ingredient.get('cost', 0):.2f}
- Supplier: {ingredient.get('supplier', 'Unknown')}
- Available: {ingredient.get('available', True)}
""")
        
        # Add low stock warnings
        if 'warnings' in inventory_data:
            context_parts.append("\n=== LOW STOCK WARNINGS ===")
            for warning in inventory_data['warnings']:
                context_parts.append(f"""
CRITICAL: {warning.get('ingredient_name', 'Unknown')}
- Current stock: {warning.get('current_quantity', 0)} {warning.get('unit', 'units')}
- Predicted runout: {warning.get('predicted_runout', 'Unknown')}
- Severity: {warning.get('severity', 'Unknown')}
- Days remaining: {warning.get('days_remaining', 0):.1f}
- Consumption rate: {warning.get('consumption_rate', 0):.2f} units/hour
- Affects menu items: {', '.join(warning.get('menu_items_affected', []))}
""")
        
        # Add menu information
        context_parts.append("\n=== MENU ITEMS ===")
        if menu_data:
            for category, items in menu_data.items():
                context_parts.append(f"\n{category.upper()}:")
                for item in items:
                    ingredients = item.get('ingredients', [])
                    ingredient_names = [ing.get('name', 'Unknown') for ing in ingredients]
                    context_parts.append(f"- {item.get('name', 'Unknown')}: {', '.join(ingredient_names)}")
        
        # Add analysis metadata
        context_parts.append(f"\n=== ANALYSIS METADATA ===")
        context_parts.append(f"Analysis generated at: {datetime.now().isoformat()}")
        context_parts.append(f"Total tickets analyzed: {consumption_data.get('total_tickets_analyzed', 0)}")
        context_parts.append(f"Analysis period: {consumption_data.get('analysis_period_days', 0)} days")
        
        return "\n".join(context_parts)
    
    def analyze_supplier_performance(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze supplier performance based on inventory data
        
        Args:
            inventory_data: Current inventory data
            
        Returns:
            Supplier performance analysis
        """
        supplier_analysis = {}
        
        if 'inventory' not in inventory_data:
            return supplier_analysis
        
        # Group ingredients by supplier
        suppliers = {}
        for ingredient in inventory_data['inventory']:
            supplier = ingredient.get('supplier', 'Unknown')
            if supplier not in suppliers:
                suppliers[supplier] = {
                    'ingredients': [],
                    'total_cost': 0,
                    'total_quantity': 0,
                    'avg_cost': 0
                }
            
            cost = ingredient.get('cost', 0)
            quantity = ingredient.get('quantity', 0)
            
            suppliers[supplier]['ingredients'].append(ingredient.get('name', 'Unknown'))
            suppliers[supplier]['total_cost'] += cost * quantity
            suppliers[supplier]['total_quantity'] += quantity
        
        # Calculate averages
        for supplier, data in suppliers.items():
            if data['total_quantity'] > 0:
                data['avg_cost'] = data['total_cost'] / data['total_quantity']
        
        return suppliers
    
    def generate_reorder_recommendations(self, warnings: List[Dict[str, Any]], 
                                       consumption_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate specific reorder recommendations based on warnings and consumption data
        
        Args:
            warnings: Low stock warnings
            consumption_data: Consumption analysis data
            
        Returns:
            List of reorder recommendations
        """
        recommendations = []
        
        for warning in warnings:
            ingredient_id = warning.get('ingredient_id')
            ingredient_id_str = str(ingredient_id)
            
            # Get consumption data for this ingredient
            consumption_info = consumption_data.get('per_ingredient', {}).get(ingredient_id_str, {})
            
            # Calculate suggested reorder quantity
            avg_daily_usage = consumption_info.get('avg_daily_usage', 0)
            usage_volatility = consumption_info.get('usage_volatility', 0)
            
            # Base reorder quantity on 7 days of usage plus safety buffer
            base_quantity = avg_daily_usage * 7
            
            # Add volatility buffer (higher volatility = larger buffer)
            volatility_buffer = max(1.2, 1.0 + (usage_volatility / avg_daily_usage) if avg_daily_usage > 0 else 1.2)
            suggested_quantity = base_quantity * volatility_buffer
            
            # Determine urgency
            days_remaining = warning.get('days_remaining', 0)
            if days_remaining <= 1:
                urgency = "critical"
            elif days_remaining <= 3:
                urgency = "high"
            elif days_remaining <= 7:
                urgency = "medium"
            else:
                urgency = "low"
            
            recommendation = {
                'ingredient_id': ingredient_id,
                'ingredient_name': warning.get('ingredient_name', 'Unknown'),
                'suggested_quantity': round(suggested_quantity, 2),
                'unit': warning.get('unit', 'units'),
                'urgency': urgency,
                'reasoning': f"Based on {avg_daily_usage:.2f} units/day usage with {usage_volatility:.2f} volatility",
                'estimated_cost': suggested_quantity * warning.get('cost_per_unit', 0),
                'supplier': warning.get('supplier', 'Unknown'),
                'days_remaining': days_remaining
            }
            
            recommendations.append(recommendation)
        
        return recommendations
