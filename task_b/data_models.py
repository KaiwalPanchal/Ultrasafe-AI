"""
Data Models for Content Transformation System
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any, Optional

class ContentFormat(Enum):
    BLOG_POST = "blog_post"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_THREAD = "twitter_thread"
    EMAIL_NEWSLETTER = "email_newsletter"
    PODCAST_SCRIPT = "podcast_script"

class ContentStyle(Enum):
    GEN_Z = "gen_z"
    MILLENNIAL = "millennial"
    ENTHUSIASTIC_MOTIVATIONAL = "enthusiastic_and_motivational"
    FORMAL_PROFESSIONAL = "formal_professional"
    CASUAL_CONVERSATIONAL = "casual_conversational"
    YODA_STAR_WARS = "yoda_star_wars"
    SHERLOCK_HOLMES = "sherlock_holmes"
    TONY_STARK_IRON_MAN = "tony_stark_iron_man"

class ComplexityLevel(Enum):
    NEWBIE = "newbie"
    KNOWS_A_LITTLE = "knows_a_little"
    EXPERT = "expert"

@dataclass
class ContentAnalysis:
    """Analysis results from Style Analysis Agent"""
    topic: str
    current_format: str
    current_style: str
    current_complexity: str
    key_themes: List[str]
    target_audience: str
    content_length: str
    tone_characteristics: Dict[str, Any]
    technical_depth: str
    readability_score: float

@dataclass
class TransformationPlan:
    """Transformation plan from Planning Agent"""
    source_format: str
    target_format: str
    source_style: str
    target_style: str
    source_complexity: str
    target_complexity: str
    transformation_steps: List[str]
    style_adaptations: List[str]
    format_adaptations: List[str]
    complexity_adaptations: List[str]
    estimated_length: str
    key_preservation_points: List[str]

@dataclass
class TransformationResult:
    """Result from Content Conversion Agent"""
    transformed_content: str
    applied_style: str
    applied_format: str
    applied_complexity: str
    transformation_notes: List[str]
    preserved_facts: List[str]
    style_elements_used: List[str]

@dataclass
class QualityMetrics:
    """Quality metrics from Quality Control Agent"""
    factual_accuracy_score: float
    style_adherence_score: float
    format_compliance_score: float
    complexity_match_score: float
    readability_score: float
    engagement_score: float
    overall_quality_score: float
    issues_found: List[str]
    suggestions: List[str]
    passes_quality_check: bool

@dataclass
class SystemState:
    """State object for LangGraph workflow"""
    original_content: str
    user_request: Dict[str, Any]
    content_analysis: Optional[ContentAnalysis] = None
    transformation_plan: Optional[TransformationPlan] = None
    transformation_result: Optional[TransformationResult] = None
    quality_metrics: Optional[QualityMetrics] = None
    rag_context: Optional[Dict[str, Any]] = None
    user_feedback: Optional[Dict[str, Any]] = None
    iteration_count: int = 0
    max_iterations: int = 3 