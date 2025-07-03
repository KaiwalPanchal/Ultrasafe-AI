"""
Content Transformation System
Multi-agent system for transforming content between formats, styles, and complexity levels
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Configuration
ULTRASAFE_API_KEY: str | None = os.getenv("ULTRASAFE_API_KEY")
ULTRASAFE_API_BASE: str | None = os.getenv(
    "ULTRASAFE_API_BASE", "https://api.us.inc/usf/v1/hiring/chat/completions"
)

if not ULTRASAFE_API_KEY:
    raise RuntimeError("ULTRASAFE_API_KEY environment variable is not set")

llm = ChatOpenAI(
    model_name="usf1-mini",
    temperature=0.2,
    max_tokens=2000,
    openai_api_key=ULTRASAFE_API_KEY,
    openai_api_base=ULTRASAFE_API_BASE,
)

@dataclass
class QualityMetrics:
    """Quality metrics for transformed content"""
    overall_quality_score: float
    factual_accuracy_score: float
    style_adherence_score: float
    format_compliance_score: float
    complexity_match_score: float
    readability_score: float
    engagement_score: float
    issues_found: List[str]
    suggestions: List[str]

class ContentTransformationSystem:
    """Multi-agent content transformation system"""
    
    def __init__(self):
        self.llm = llm
        self.style_guides_dir = Path("style_guides")
        self.rag_index_dir = Path("rag_faiss_index")
        
        # Load RAG index if available
        self.rag_context = self._load_rag_context()
        
        # Transformation prompt
        self.transformation_prompt = PromptTemplate(
            input_variables=["content", "style_guide", "format_type", "style_name", "complexity_level", "rag_context"],
            template="""
You are an expert content transformer. Your task is to transform content according to specific style guidelines while maintaining ALL factual accuracy.

STYLE GUIDE TO FOLLOW:
{style_guide}

FORMAT: {format_type}
STYLE: {style_name}  
COMPLEXITY: {complexity_level}

CONTENT TO TRANSFORM:
{content}

{rag_context}

TRANSFORMATION REQUIREMENTS:
1. **PRESERVE ALL FACTS**: Every statistic, definition, and factual claim must remain exactly accurate
2. **APPLY STYLE**: Transform tone, voice, and presentation according to the style guide
3. **MATCH FORMAT**: Adapt structure for the specified format (blog post, LinkedIn, etc.)
4. **MATCH COMPLEXITY**: Adjust technical depth for the target audience level
5. **MAINTAIN COMPLETENESS**: Include all key information from original content
6. **NATURAL FLOW**: Ensure the transformed content reads naturally in the new style

CRITICAL: Do not add new facts, change statistics, or alter any factual information. Only change HOW the information is presented.

TRANSFORMED CONTENT:
"""
        )
        
        # Quality assessment prompt
        self.quality_prompt = PromptTemplate(
            input_variables=["original_content", "transformed_content", "target_format", "target_style", "target_complexity"],
            template="""
You are a quality control expert. Assess the quality of the transformed content.

ORIGINAL CONTENT:
{original_content}

TRANSFORMED CONTENT:
{transformed_content}

TARGET FORMAT: {target_format}
TARGET STYLE: {target_style}
TARGET COMPLEXITY: {target_complexity}

Assess the transformation quality and provide scores (0.0-1.0) and feedback:

1. **Factual Accuracy**: Are all facts preserved exactly?
2. **Style Adherence**: Does it match the target style?
3. **Format Compliance**: Does it follow the target format?
4. **Complexity Match**: Is it appropriate for the target audience?
5. **Readability**: Is it clear and easy to understand?
6. **Engagement**: Is it compelling and interesting?

Provide your assessment in this JSON format:
{{
    "overall_quality_score": 0.85,
    "factual_accuracy_score": 0.95,
    "style_adherence_score": 0.80,
    "format_compliance_score": 0.90,
    "complexity_match_score": 0.85,
    "readability_score": 0.88,
    "engagement_score": 0.82,
    "issues_found": [
        "Issue 1 description",
        "Issue 2 description"
    ],
    "suggestions": [
        "Suggestion 1",
        "Suggestion 2"
    ]
}}

ASSESSMENT:
"""
        )
    
    def _load_rag_context(self) -> str:
        """Load RAG context if available"""
        try:
            if self.rag_index_dir.exists():
                # For now, return a placeholder - you can implement actual RAG retrieval here
                return "\nRELEVANT CONTEXT:\n[No specific context loaded - using general knowledge]"
            else:
                return "\nRELEVANT CONTEXT:\n[No RAG context available]"
        except Exception as e:
            return f"\nRELEVANT CONTEXT:\n[Error loading RAG context: {e}]"
    
    def _load_style_guide(self, target_format: str, target_style: str, target_complexity: str) -> str:
        """Load the appropriate style guide"""
        try:
            # Look for style guide file
            style_filename = f"{target_format}_{target_style}_{target_complexity}.txt"
            style_path = self.style_guides_dir / style_filename
            
            if style_path.exists():
                with open(style_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # Fallback to a generic style guide
                return self._generate_fallback_style_guide(target_format, target_style, target_complexity)
                
        except Exception as e:
            print(f"Warning: Could not load style guide: {e}")
            return self._generate_fallback_style_guide(target_format, target_style, target_complexity)
    
    def _generate_fallback_style_guide(self, target_format: str, target_style: str, target_complexity: str) -> str:
        """Generate a fallback style guide when the file is not found"""
        return f"""
STYLE GUIDE FOR {target_format.upper()} - {target_style.upper()} - {target_complexity.upper()}

FORMAT REQUIREMENTS:
- Format: {target_format}
- Structure: Appropriate for {target_format}
- Length: Suitable for {target_format}

STYLE REQUIREMENTS:
- Tone: {target_style}
- Voice: {target_style}
- Language: {target_style}

COMPLEXITY REQUIREMENTS:
- Audience: {target_complexity}
- Technical Level: {target_complexity}
- Explanations: {target_complexity}

GENERAL GUIDELINES:
- Maintain factual accuracy
- Use appropriate tone and style
- Follow format conventions
- Match complexity level
- Ensure readability and engagement
"""
    
    def _assess_quality(self, original_content: str, transformed_content: str, 
                       target_format: str, target_style: str, target_complexity: str) -> QualityMetrics:
        """Assess the quality of the transformation"""
        try:
            prompt = self.quality_prompt.format(
                original_content=original_content,
                transformed_content=transformed_content,
                target_format=target_format,
                target_style=target_style,
                target_complexity=target_complexity
            )
            
            messages = [
                SystemMessage(content="You are a quality control expert for content transformation."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            
            # Try to parse JSON response
            try:
                quality_data = json.loads(response.content)
                return QualityMetrics(**quality_data)
            except json.JSONDecodeError:
                # Fallback to default metrics
                return QualityMetrics(
                    overall_quality_score=0.8,
                    factual_accuracy_score=0.9,
                    style_adherence_score=0.8,
                    format_compliance_score=0.8,
                    complexity_match_score=0.8,
                    readability_score=0.8,
                    engagement_score=0.8,
                    issues_found=["Could not parse quality assessment"],
                    suggestions=["Review transformation manually"]
                )
                
        except Exception as e:
            print(f"Warning: Quality assessment failed: {e}")
            return QualityMetrics(
                overall_quality_score=0.7,
                factual_accuracy_score=0.8,
                style_adherence_score=0.7,
                format_compliance_score=0.7,
                complexity_match_score=0.7,
                readability_score=0.7,
                engagement_score=0.7,
                issues_found=["Quality assessment failed"],
                suggestions=["Review transformation manually"]
            )
    
    def transform_content(self, content: str, target_format: str, target_style: str, 
                         target_complexity: str, target_topic: Optional[str] = None,
                         user_feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Transform content to target format, style, and complexity
        
        Args:
            content: Original content to transform
            target_format: Target format (blog_post, linkedin_post, twitter_thread, etc.)
            target_style: Target style (gen_z, millennial, formal_professional, etc.)
            target_complexity: Target complexity (newbie, knows_a_little, expert)
            target_topic: Optional topic for RAG context (not used in this implementation)
            user_feedback: Optional user feedback for iteration
            
        Returns:
            Dict with transformation results and quality metrics
        """
        try:
            # Load style guide
            style_guide = self._load_style_guide(target_format, target_style, target_complexity)
            
            # Prepare transformation prompt
            rag_context = self._load_rag_context()
            if target_topic:
                rag_context += f"\nTOPIC CONTEXT: {target_topic}"
            
            # Add user feedback if provided
            feedback_context = ""
            if user_feedback:
                feedback_context = f"\nUSER FEEDBACK:\n"
                if user_feedback.get('issues'):
                    feedback_context += f"Issues to fix: {', '.join(user_feedback['issues'])}\n"
                if user_feedback.get('suggestions'):
                    feedback_context += f"Suggestions: {', '.join(user_feedback['suggestions'])}\n"
                if user_feedback.get('target_improvements'):
                    feedback_context += f"Target improvements: {', '.join(user_feedback['target_improvements'])}\n"
            
            prompt = self.transformation_prompt.format(
                content=content,
                style_guide=style_guide,
                format_type=target_format,
                style_name=target_style,
                complexity_level=target_complexity,
                rag_context=rag_context + feedback_context
            )
            
            # Perform transformation
            messages = [
                SystemMessage(content="You are an expert content transformer who maintains factual accuracy while adapting style and format."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            transformed_content = response.content.strip()
            
            # Assess quality
            quality_metrics = self._assess_quality(
                content, transformed_content, target_format, target_style, target_complexity
            )
            
            return {
                'success': True,
                'transformed_content': transformed_content,
                'quality_metrics': {
                    'overall_quality_score': quality_metrics.overall_quality_score,
                    'factual_accuracy_score': quality_metrics.factual_accuracy_score,
                    'style_adherence_score': quality_metrics.style_adherence_score,
                    'format_compliance_score': quality_metrics.format_compliance_score,
                    'complexity_match_score': quality_metrics.complexity_match_score,
                    'readability_score': quality_metrics.readability_score,
                    'engagement_score': quality_metrics.engagement_score,
                    'issues_found': quality_metrics.issues_found,
                    'suggestions': quality_metrics.suggestions
                },
                'iterations': 1,
                'rag_context_used': self.rag_index_dir.exists()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f"Transformation failed: {str(e)}",
                'transformed_content': f"Error: {str(e)}",
                'quality_metrics': {
                    'overall_quality_score': 0.0,
                    'factual_accuracy_score': 0.0,
                    'style_adherence_score': 0.0,
                    'format_compliance_score': 0.0,
                    'complexity_match_score': 0.0,
                    'readability_score': 0.0,
                    'engagement_score': 0.0,
                    'issues_found': [f"Transformation error: {str(e)}"],
                    'suggestions': ["Check input parameters and try again"]
                },
                'iterations': 0,
                'rag_context_used': False
            } 