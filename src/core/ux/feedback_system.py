"""
ImpressionCore UX - Comprehensive Feedback System
==================================================

This module implements a comprehensive feedback collection and analysis system that captures
both explicit user feedback and implicit behavioral signals. It provides sentiment analysis,
performance correlation tracking, and long-term satisfaction monitoring to continuously
improve the user experience.

Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
Architecture: Brain-inspired multimodal framework
Focus: User experience optimization through feedback-driven adaptation

Key Features:
- Multi-modal feedback collection (explicit ratings, implicit behavior)
- Real-time sentiment analysis using lightweight NLP
- Performance correlation analysis between feedback and system metrics
- Long-term satisfaction tracking with trend analysis
- Integration with ML adaptation engine for continuous improvement
- Memory-optimized for constrained hardware environments

Author: GitHub Copilot & Kirk LaSalle
Created: 2025-06-01
Version: 1.0.0
"""

import json
import time
import logging
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import threading
from collections import defaultdict, deque
import sqlite3
import pickle

# Core framework imports
try:
    from src.core.utils.rich_enhancements import RichTextManager
    from src.core.utils.rich_logging import RichLogger
    from src.core.utils.rich_status_animation import RichStatusAnimation
    CORE_UTILS_AVAILABLE = True
    MemoryTracker = None  # Use simplified memory tracking
except ImportError:
    try:
        from core.utils.rich_enhancements import RichTextManager
        from core.utils.rich_logging import RichLogger
        from core.utils.rich_status_animation import RichStatusAnimation
        CORE_UTILS_AVAILABLE = True
        MemoryTracker = None  # Use simplified memory tracking
    except ImportError:
        CORE_UTILS_AVAILABLE = False
        RichTextManager = None
        RichLogger = logging.getLogger(__name__)
        RichStatusAnimation = None
        MemoryTracker = None

# ML/Statistical imports
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import accuracy_score, mean_squared_error
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available. Some feedback analysis features will be limited.")

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK not available. Sentiment analysis will use fallback method.")


class FeedbackType(Enum):
    """Types of feedback that can be collected."""
    EXPLICIT_RATING = "explicit_rating"
    TEXT_FEEDBACK = "text_feedback"
    BEHAVIORAL_IMPLICIT = "behavioral_implicit"
    PERFORMANCE_CORRELATION = "performance_correlation"
    SATISFACTION_SURVEY = "satisfaction_survey"
    ERROR_REPORT = "error_report"
    FEATURE_REQUEST = "feature_request"


class SentimentPolarity(Enum):
    """Sentiment polarity classifications."""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


@dataclass
class FeedbackEntry:
    """Represents a single feedback entry from a user."""
    feedback_id: str
    user_id: str
    session_id: str
    timestamp: datetime
    feedback_type: FeedbackType
    content: Union[str, int, float, Dict[str, Any]]
    context: Dict[str, Any] = field(default_factory=dict)
    sentiment_score: Optional[float] = None
    sentiment_polarity: Optional[SentimentPolarity] = None
    associated_metrics: Dict[str, float] = field(default_factory=dict)
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert feedback entry to dictionary for serialization."""
        result = asdict(self)
        result['timestamp'] = self.timestamp.isoformat()
        result['feedback_type'] = self.feedback_type.value
        if self.sentiment_polarity:
            result['sentiment_polarity'] = self.sentiment_polarity.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FeedbackEntry':
        """Create feedback entry from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['feedback_type'] = FeedbackType(data['feedback_type'])
        if data.get('sentiment_polarity') is not None:
            data['sentiment_polarity'] = SentimentPolarity(data['sentiment_polarity'])
        return cls(**data)


@dataclass
class SatisfactionMetrics:
    """Aggregated satisfaction metrics for analysis."""
    user_id: str
    period_start: datetime
    period_end: datetime
    total_feedback_count: int
    average_rating: float
    sentiment_distribution: Dict[str, int] = field(default_factory=dict)
    trend_direction: str = "stable"  # "improving", "declining", "stable"
    satisfaction_score: float = 0.0
    confidence_level: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert satisfaction metrics to dictionary."""
        result = asdict(self)
        result['period_start'] = self.period_start.isoformat()
        result['period_end'] = self.period_end.isoformat()
        return result


@dataclass
class PerformanceCorrelation:
    """Performance correlation analysis results."""
    metric_name: str
    correlation_coefficient: float
    p_value: float
    significance_level: str
    sample_size: int
    confidence_interval: Tuple[float, float]
    interpretation: str


class SentimentAnalyzer:
    """Lightweight sentiment analysis for user feedback."""
      def __init__(self):
        self.logger = RichLogger("SentimentAnalyzer") if CORE_UTILS_AVAILABLE else logging.getLogger(__name__)
        self.rich_manager = RichTextManager() if CORE_UTILS_AVAILABLE else None
        self.memory_tracker = MemoryTracker() if MemoryTracker else None
        
        # Initialize sentiment analysis tools
        self.analyzer = None
        self.vectorizer = None
        self.classifier = None
        self._initialize_sentiment_tools()
        
        # Fallback sentiment lexicon for when NLTK is unavailable
        self.positive_words = {
            'good', 'great', 'excellent', 'amazing', 'fantastic', 'love', 'awesome',
            'perfect', 'wonderful', 'brilliant', 'outstanding', 'superb', 'fast',
            'efficient', 'helpful', 'useful', 'smooth', 'easy', 'intuitive'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'slow', 'confusing',
            'difficult', 'broken', 'error', 'problem', 'issue', 'frustrating',
            'annoying', 'useless', 'complicated', 'poor', 'disappointing'
        }
    
    def _initialize_sentiment_tools(self):
        """Initialize sentiment analysis tools if available."""
        if NLTK_AVAILABLE:
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.analyzer = SentimentIntensityAnalyzer()
                self.logger.info("NLTK sentiment analyzer initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize NLTK analyzer: {e}")
        
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.classifier = MultinomialNB()
            self.logger.info("Scikit-learn sentiment classifier initialized")
    
    def analyze_sentiment(self, text: str) -> Tuple[float, SentimentPolarity]:
        """
        Analyze sentiment of text input.
        
        Args:
            text: Text to analyze
            
        Returns:
            Tuple of (sentiment_score, sentiment_polarity)
            Score ranges from -1 (very negative) to 1 (very positive)
        """
        if not text or not isinstance(text, str):
            return 0.0, SentimentPolarity.NEUTRAL
        
        text = text.lower().strip()
        
        # Try NLTK analyzer first
        if self.analyzer:
            try:
                scores = self.analyzer.polarity_scores(text)
                compound_score = scores['compound']
                polarity = self._score_to_polarity(compound_score)
                return compound_score, polarity
            except Exception as e:
                self.logger.warning(f"NLTK sentiment analysis failed: {e}")
        
        # Fallback to simple lexicon-based analysis
        return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Tuple[float, SentimentPolarity]:
        """Simple lexicon-based sentiment analysis fallback."""
        words = text.split()
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0, SentimentPolarity.NEUTRAL
        
        # Calculate score (-1 to 1)
        score = (positive_count - negative_count) / len(words)
        score = max(-1.0, min(1.0, score * 5))  # Scale and clamp
        
        polarity = self._score_to_polarity(score)
        return score, polarity
    
    def _score_to_polarity(self, score: float) -> SentimentPolarity:
        """Convert sentiment score to polarity enum."""
        if score <= -0.6:
            return SentimentPolarity.VERY_NEGATIVE
        elif score <= -0.2:
            return SentimentPolarity.NEGATIVE
        elif score >= 0.6:
            return SentimentPolarity.VERY_POSITIVE
        elif score >= 0.2:
            return SentimentPolarity.POSITIVE
        else:
            return SentimentPolarity.NEUTRAL


class FeedbackAnalyzer:
    """Analyzes feedback patterns and correlations with performance metrics."""
    
    def __init__(self):
        self.logger = RichLogger("FeedbackAnalyzer")
        self.memory_tracker = MemoryTracker()
        
        # ML models for analysis
        self.satisfaction_predictor = LinearRegression() if SKLEARN_AVAILABLE else None
        self.scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self.is_trained = False
        
        # Analysis cache
        self.correlation_cache = {}
        self.trend_cache = {}
        
    def analyze_performance_correlation(self, 
                                      feedback_data: List[FeedbackEntry],
                                      performance_metrics: Dict[str, List[float]]) -> Dict[str, PerformanceCorrelation]:
        """
        Analyze correlation between feedback and performance metrics.
        
        Args:
            feedback_data: List of feedback entries
            performance_metrics: Dictionary of metric names to value lists
            
        Returns:
            Dictionary of correlation analyses by metric name
        """
        correlations = {}
        
        if not feedback_data or not performance_metrics:
            return correlations
        
        # Extract numerical feedback scores
        feedback_scores = []
        feedback_timestamps = []
        
        for entry in feedback_data:
            if entry.sentiment_score is not None:
                feedback_scores.append(entry.sentiment_score)
                feedback_timestamps.append(entry.timestamp)
            elif isinstance(entry.content, (int, float)):
                feedback_scores.append(float(entry.content))
                feedback_timestamps.append(entry.timestamp)
        
        if len(feedback_scores) < 5:  # Need minimum samples for correlation
            self.logger.warning("Insufficient feedback data for correlation analysis")
            return correlations
        
        # Analyze each performance metric
        for metric_name, metric_values in performance_metrics.items():
            if len(metric_values) != len(feedback_scores):
                continue
                
            correlation = self._calculate_correlation(feedback_scores, metric_values, metric_name)
            if correlation:
                correlations[metric_name] = correlation
        
        return correlations
    
    def _calculate_correlation(self, 
                             feedback_scores: List[float], 
                             metric_values: List[float],
                             metric_name: str) -> Optional[PerformanceCorrelation]:
        """Calculate correlation between feedback and a specific metric."""
        try:
            # Use numpy for correlation calculation
            correlation_coeff = np.corrcoef(feedback_scores, metric_values)[0, 1]
            
            # Simple p-value approximation (for demonstration)
            n = len(feedback_scores)
            t_stat = correlation_coeff * np.sqrt((n - 2) / (1 - correlation_coeff**2))
            p_value = 2 * (1 - abs(t_stat) / np.sqrt(n - 2))  # Simplified
            
            # Determine significance
            if p_value < 0.01:
                significance = "highly_significant"
            elif p_value < 0.05:
                significance = "significant"
            else:
                significance = "not_significant"
            
            # Confidence interval (simplified)
            margin = 1.96 / np.sqrt(n - 3)  # Simplified 95% CI
            ci_lower = correlation_coeff - margin
            ci_upper = correlation_coeff + margin
            
            # Interpretation
            if abs(correlation_coeff) > 0.7:
                interpretation = "strong"
            elif abs(correlation_coeff) > 0.3:
                interpretation = "moderate"
            else:
                interpretation = "weak"
            
            if correlation_coeff > 0:
                interpretation += "_positive"
            else:
                interpretation += "_negative"
            
            return PerformanceCorrelation(
                metric_name=metric_name,
                correlation_coefficient=correlation_coeff,
                p_value=p_value,
                significance_level=significance,
                sample_size=n,
                confidence_interval=(ci_lower, ci_upper),
                interpretation=interpretation
            )
            
        except Exception as e:
            self.logger.error(f"Correlation calculation failed for {metric_name}: {e}")
            return None
    
    def analyze_satisfaction_trends(self, 
                                  feedback_data: List[FeedbackEntry],
                                  time_window_days: int = 30) -> SatisfactionMetrics:
        """
        Analyze satisfaction trends over a specified time window.
        
        Args:
            feedback_data: List of feedback entries
            time_window_days: Time window for analysis in days
            
        Returns:
            Satisfaction metrics with trend analysis
        """
        if not feedback_data:
            # Return empty metrics for no data
            now = datetime.now()
            return SatisfactionMetrics(
                user_id="unknown",
                period_start=now - timedelta(days=time_window_days),
                period_end=now,
                total_feedback_count=0,
                average_rating=0.0
            )
        
        # Filter data to time window
        end_time = datetime.now()
        start_time = end_time - timedelta(days=time_window_days)
        
        window_feedback = [
            entry for entry in feedback_data 
            if start_time <= entry.timestamp <= end_time
        ]
        
        if not window_feedback:
            return SatisfactionMetrics(
                user_id=feedback_data[0].user_id,
                period_start=start_time,
                period_end=end_time,
                total_feedback_count=0,
                average_rating=0.0
            )
        
        # Calculate metrics
        total_count = len(window_feedback)
        user_id = window_feedback[0].user_id
        
        # Calculate average rating
        ratings = []
        sentiment_counts = defaultdict(int)
        
        for entry in window_feedback:
            if entry.sentiment_score is not None:
                ratings.append(entry.sentiment_score)
            elif isinstance(entry.content, (int, float)):
                ratings.append(float(entry.content))
            
            if entry.sentiment_polarity:
                sentiment_counts[entry.sentiment_polarity.name] += 1
        
        average_rating = np.mean(ratings) if ratings else 0.0
        
        # Analyze trend
        trend_direction = self._calculate_trend_direction(window_feedback)
        
        # Calculate satisfaction score (0-100)
        satisfaction_score = self._calculate_satisfaction_score(ratings, sentiment_counts)
        
        # Calculate confidence level
        confidence_level = min(1.0, total_count / 10.0)  # More data = higher confidence
        
        return SatisfactionMetrics(
            user_id=user_id,
            period_start=start_time,
            period_end=end_time,
            total_feedback_count=total_count,
            average_rating=average_rating,
            sentiment_distribution=dict(sentiment_counts),
            trend_direction=trend_direction,
            satisfaction_score=satisfaction_score,
            confidence_level=confidence_level
        )
    
    def _calculate_trend_direction(self, feedback_data: List[FeedbackEntry]) -> str:
        """Calculate trend direction from temporal feedback data."""
        if len(feedback_data) < 3:
            return "stable"
        
        # Sort by timestamp
        sorted_feedback = sorted(feedback_data, key=lambda x: x.timestamp)
        
        # Extract ratings over time
        ratings = []
        for entry in sorted_feedback:
            if entry.sentiment_score is not None:
                ratings.append(entry.sentiment_score)
            elif isinstance(entry.content, (int, float)):
                ratings.append(float(entry.content))
        
        if len(ratings) < 3:
            return "stable"
        
        # Simple linear trend analysis
        x = np.arange(len(ratings))
        slope = np.polyfit(x, ratings, 1)[0]
        
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        else:
            return "stable"
    
    def _calculate_satisfaction_score(self, 
                                    ratings: List[float], 
                                    sentiment_counts: Dict[str, int]) -> float:
        """Calculate overall satisfaction score (0-100)."""
        if not ratings and not sentiment_counts:
            return 50.0  # Neutral baseline
        
        score = 50.0  # Start with neutral
        
        # Factor in average rating
        if ratings:
            avg_rating = np.mean(ratings)
            score += avg_rating * 25  # Scale to 0-50 contribution
        
        # Factor in sentiment distribution
        total_sentiment = sum(sentiment_counts.values())
        if total_sentiment > 0:
            weighted_sentiment = (
                sentiment_counts.get('VERY_POSITIVE', 0) * 2 +
                sentiment_counts.get('POSITIVE', 0) * 1 +
                sentiment_counts.get('NEUTRAL', 0) * 0 +
                sentiment_counts.get('NEGATIVE', 0) * -1 +
                sentiment_counts.get('VERY_NEGATIVE', 0) * -2
            ) / total_sentiment
            
            score += weighted_sentiment * 25  # Scale to 0-50 contribution
        
        return max(0.0, min(100.0, score))


class FeedbackCollector:
    """Collects and manages user feedback from multiple sources."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = RichLogger("FeedbackCollector")
        self.rich_manager = RichTextManager()
        self.memory_tracker = MemoryTracker()
        
        # Storage configuration
        self.storage_path = Path(storage_path or "data/feedback")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Database for persistent storage
        self.db_path = self.storage_path / "feedback.db"
        self._initialize_database()
        
        # In-memory feedback cache
        self.feedback_cache = deque(maxlen=1000)  # Keep recent feedback in memory
        self.user_sessions = {}
        
        # Callback system for feedback events
        self.feedback_callbacks: List[Callable[[FeedbackEntry], None]] = []
        
        # Background processing
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
    def _initialize_database(self):
        """Initialize SQLite database for feedback storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS feedback (
                        feedback_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        feedback_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        context TEXT,
                        sentiment_score REAL,
                        sentiment_polarity INTEGER,
                        associated_metrics TEXT,
                        processed BOOLEAN DEFAULT FALSE
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_timestamp 
                    ON feedback (user_id, timestamp)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session 
                    ON feedback (session_id)
                """)
                
                conn.commit()
                self.logger.info("Feedback database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize feedback database: {e}")
    
    def collect_explicit_feedback(self, 
                                user_id: str,
                                session_id: str,
                                feedback_type: FeedbackType,
                                content: Union[str, int, float],
                                context: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect explicit feedback from user.
        
        Args:
            user_id: Unique user identifier
            session_id: Current session identifier
            feedback_type: Type of feedback being provided
            content: Feedback content (rating, text, etc.)
            context: Additional context information
            
        Returns:
            Feedback entry ID
        """
        feedback_entry = FeedbackEntry(
            feedback_id=f"fb_{int(time.time() * 1000)}_{user_id}",
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            feedback_type=feedback_type,
            content=content,
            context=context or {}
        )
        
        # Store feedback
        self._store_feedback(feedback_entry)
        
        # Add to cache
        self.feedback_cache.append(feedback_entry)
        
        # Trigger callbacks
        self._trigger_feedback_callbacks(feedback_entry)
        
        self.logger.info(f"Collected explicit feedback: {feedback_type.value} from user {user_id}")
        return feedback_entry.feedback_id
    
    def collect_implicit_feedback(self,
                                user_id: str,
                                session_id: str,
                                behavior_data: Dict[str, Any],
                                performance_metrics: Optional[Dict[str, float]] = None) -> str:
        """
        Collect implicit feedback from user behavior.
        
        Args:
            user_id: Unique user identifier
            session_id: Current session identifier
            behavior_data: Behavioral data (clicks, time spent, etc.)
            performance_metrics: Associated performance metrics
            
        Returns:
            Feedback entry ID
        """
        feedback_entry = FeedbackEntry(
            feedback_id=f"imp_{int(time.time() * 1000)}_{user_id}",
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.BEHAVIORAL_IMPLICIT,
            content=behavior_data,
            associated_metrics=performance_metrics or {}
        )
        
        # Store feedback
        self._store_feedback(feedback_entry)
        
        # Add to cache
        self.feedback_cache.append(feedback_entry)
        
        self.logger.debug(f"Collected implicit feedback from user {user_id}")
        return feedback_entry.feedback_id
    
    def _store_feedback(self, feedback_entry: FeedbackEntry):
        """Store feedback entry in database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO feedback (
                        feedback_id, user_id, session_id, timestamp,
                        feedback_type, content, context, sentiment_score,
                        sentiment_polarity, associated_metrics, processed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    feedback_entry.feedback_id,
                    feedback_entry.user_id,
                    feedback_entry.session_id,
                    feedback_entry.timestamp.isoformat(),
                    feedback_entry.feedback_type.value,
                    json.dumps(feedback_entry.content),
                    json.dumps(feedback_entry.context),
                    feedback_entry.sentiment_score,
                    feedback_entry.sentiment_polarity.value if feedback_entry.sentiment_polarity else None,
                    json.dumps(feedback_entry.associated_metrics),
                    feedback_entry.processed
                ))
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Failed to store feedback: {e}")
    
    def get_user_feedback(self, 
                         user_id: str, 
                         days_back: int = 30,
                         feedback_types: Optional[List[FeedbackType]] = None) -> List[FeedbackEntry]:
        """
        Retrieve feedback for a specific user.
        
        Args:
            user_id: User identifier
            days_back: Number of days to look back
            feedback_types: Filter by specific feedback types
            
        Returns:
            List of feedback entries
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            query = """
                SELECT * FROM feedback 
                WHERE user_id = ? AND timestamp >= ?
            """
            params = [user_id, cutoff_date.isoformat()]
            
            if feedback_types:
                type_placeholders = ','.join('?' * len(feedback_types))
                query += f" AND feedback_type IN ({type_placeholders})"
                params.extend([ft.value for ft in feedback_types])
            
            query += " ORDER BY timestamp DESC"
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                feedback_entries = []
                for row in rows:
                    entry = self._row_to_feedback_entry(row)
                    if entry:
                        feedback_entries.append(entry)
                
                return feedback_entries
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve user feedback: {e}")
            return []
    
    def _row_to_feedback_entry(self, row: sqlite3.Row) -> Optional[FeedbackEntry]:
        """Convert database row to FeedbackEntry object."""
        try:
            return FeedbackEntry(
                feedback_id=row['feedback_id'],
                user_id=row['user_id'],
                session_id=row['session_id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                feedback_type=FeedbackType(row['feedback_type']),
                content=json.loads(row['content']),
                context=json.loads(row['context']) if row['context'] else {},
                sentiment_score=row['sentiment_score'],
                sentiment_polarity=SentimentPolarity(row['sentiment_polarity']) if row['sentiment_polarity'] is not None else None,
                associated_metrics=json.loads(row['associated_metrics']) if row['associated_metrics'] else {},
                processed=bool(row['processed'])
            )
        except Exception as e:
            self.logger.error(f"Failed to convert row to feedback entry: {e}")
            return None
    
    def register_feedback_callback(self, callback: Callable[[FeedbackEntry], None]):
        """Register a callback to be called when feedback is received."""
        self.feedback_callbacks.append(callback)
    
    def _trigger_feedback_callbacks(self, feedback_entry: FeedbackEntry):
        """Trigger all registered feedback callbacks."""
        for callback in self.feedback_callbacks:
            try:
                callback(feedback_entry)
            except Exception as e:
                self.logger.error(f"Feedback callback failed: {e}")
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Get overall feedback statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total feedback count
                total_count = conn.execute("SELECT COUNT(*) FROM feedback").fetchone()[0]
                
                # Feedback by type
                type_counts = conn.execute("""
                    SELECT feedback_type, COUNT(*) 
                    FROM feedback 
                    GROUP BY feedback_type
                """).fetchall()
                
                # Recent activity (last 7 days)
                week_ago = (datetime.now() - timedelta(days=7)).isoformat()
                recent_count = conn.execute("""
                    SELECT COUNT(*) FROM feedback 
                    WHERE timestamp >= ?
                """, (week_ago,)).fetchone()[0]
                
                return {
                    'total_feedback': total_count,
                    'feedback_by_type': dict(type_counts),
                    'recent_feedback_7d': recent_count,
                    'cache_size': len(self.feedback_cache)
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get feedback stats: {e}")
            return {}


class ComprehensiveFeedbackSystem:
    """
    Main feedback system that orchestrates collection, analysis, and integration.
    
    This system provides:
    - Multi-modal feedback collection (explicit and implicit)
    - Real-time sentiment analysis
    - Performance correlation tracking
    - Long-term satisfaction monitoring
    - Integration with ML adaptation systems
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        self.logger = RichLogger("ComprehensiveFeedbackSystem")
        self.rich_manager = RichTextManager()
        self.memory_tracker = MemoryTracker()
        
        # Initialize components
        self.collector = FeedbackCollector(storage_path)
        self.sentiment_analyzer = SentimentAnalyzer()
        self.feedback_analyzer = FeedbackAnalyzer()
        
        # Processing configuration
        self.auto_process = True
        self.processing_interval = 60  # Process feedback every 60 seconds
        
        # Integration callbacks
        self.adaptation_callbacks: List[Callable[[SatisfactionMetrics], None]] = []
        
        # Background processing
        self.processing_thread = None
        self.stop_processing = threading.Event()
        
        # Start background processing
        if self.auto_process:
            self.start_background_processing()
        
        # Register internal feedback callback
        self.collector.register_feedback_callback(self._process_new_feedback)
        
        self.logger.info("Comprehensive Feedback System initialized")
    
    def collect_rating_feedback(self, 
                              user_id: str,
                              session_id: str,
                              rating: Union[int, float],
                              max_rating: Union[int, float] = 5,
                              category: str = "general",
                              context: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect explicit rating feedback from user.
        
        Args:
            user_id: Unique user identifier
            session_id: Current session identifier
            rating: Numeric rating provided by user
            max_rating: Maximum possible rating value
            category: Category of rating (e.g., "performance", "ui", "general")
            context: Additional context information
            
        Returns:
            Feedback entry ID
        """
        # Normalize rating to 0-1 scale
        normalized_rating = float(rating) / float(max_rating)
        
        feedback_context = context or {}
        feedback_context.update({
            'category': category,
            'original_rating': rating,
            'max_rating': max_rating,
            'normalized_rating': normalized_rating
        })
        
        return self.collector.collect_explicit_feedback(
            user_id=user_id,
            session_id=session_id,
            feedback_type=FeedbackType.EXPLICIT_RATING,
            content=normalized_rating,
            context=feedback_context
        )
    
    def collect_text_feedback(self,
                            user_id: str,
                            session_id: str,
                            text: str,
                            category: str = "general",
                            context: Optional[Dict[str, Any]] = None) -> str:
        """
        Collect text feedback with automatic sentiment analysis.
        
        Args:
            user_id: Unique user identifier
            session_id: Current session identifier
            text: Text feedback from user
            category: Category of feedback
            context: Additional context information
            
        Returns:
            Feedback entry ID
        """
        feedback_context = context or {}
        feedback_context.update({
            'category': category,
            'text_length': len(text)
        })
        
        # Analyze sentiment
        sentiment_score, sentiment_polarity = self.sentiment_analyzer.analyze_sentiment(text)
        
        feedback_entry = FeedbackEntry(
            feedback_id=f"txt_{int(time.time() * 1000)}_{user_id}",
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.now(),
            feedback_type=FeedbackType.TEXT_FEEDBACK,
            content=text,
            context=feedback_context,
            sentiment_score=sentiment_score,
            sentiment_polarity=sentiment_polarity
        )
        
        # Store and process
        self.collector._store_feedback(feedback_entry)
        self.collector.feedback_cache.append(feedback_entry)
        self.collector._trigger_feedback_callbacks(feedback_entry)
        
        self.logger.info(f"Collected text feedback with sentiment {sentiment_polarity.name}")
        return feedback_entry.feedback_id
    
    def collect_behavioral_feedback(self,
                                  user_id: str,
                                  session_id: str,
                                  interaction_data: Dict[str, Any],
                                  performance_metrics: Optional[Dict[str, float]] = None) -> str:
        """
        Collect implicit behavioral feedback.
        
        Args:
            user_id: Unique user identifier
            session_id: Current session identifier
            interaction_data: User interaction data (clicks, time, etc.)
            performance_metrics: Associated system performance metrics
            
        Returns:
            Feedback entry ID
        """
        return self.collector.collect_implicit_feedback(
            user_id=user_id,
            session_id=session_id,
            behavior_data=interaction_data,
            performance_metrics=performance_metrics
        )
    
    def analyze_user_satisfaction(self, 
                                user_id: str,
                                time_window_days: int = 30) -> SatisfactionMetrics:
        """
        Analyze user satisfaction over specified time window.
        
        Args:
            user_id: User to analyze
            time_window_days: Time window for analysis
            
        Returns:
            Satisfaction metrics and trends
        """
        # Get user feedback
        feedback_data = self.collector.get_user_feedback(user_id, time_window_days)
        
        # Analyze satisfaction trends
        satisfaction_metrics = self.feedback_analyzer.analyze_satisfaction_trends(
            feedback_data, time_window_days
        )
        
        self.logger.info(f"Analyzed satisfaction for user {user_id}: "
                        f"score={satisfaction_metrics.satisfaction_score:.1f}, "
                        f"trend={satisfaction_metrics.trend_direction}")
        
        return satisfaction_metrics
    
    def analyze_performance_correlations(self,
                                       user_id: str,
                                       performance_metrics: Dict[str, List[float]],
                                       time_window_days: int = 30) -> Dict[str, PerformanceCorrelation]:
        """
        Analyze correlations between feedback and performance metrics.
        
        Args:
            user_id: User to analyze
            performance_metrics: Performance metrics to correlate with
            time_window_days: Time window for analysis
            
        Returns:
            Performance correlation analysis results
        """
        # Get user feedback
        feedback_data = self.collector.get_user_feedback(user_id, time_window_days)
        
        # Analyze correlations
        correlations = self.feedback_analyzer.analyze_performance_correlation(
            feedback_data, performance_metrics
        )
        
        self.logger.info(f"Analyzed {len(correlations)} performance correlations for user {user_id}")
        return correlations
    
    def _process_new_feedback(self, feedback_entry: FeedbackEntry):
        """Process newly received feedback entry."""
        try:
            # Analyze sentiment if not already done
            if (feedback_entry.feedback_type == FeedbackType.TEXT_FEEDBACK and 
                feedback_entry.sentiment_score is None):
                
                if isinstance(feedback_entry.content, str):
                    sentiment_score, sentiment_polarity = self.sentiment_analyzer.analyze_sentiment(
                        feedback_entry.content
                    )
                    feedback_entry.sentiment_score = sentiment_score
                    feedback_entry.sentiment_polarity = sentiment_polarity
            
            # Mark as processed
            feedback_entry.processed = True
            
            # Trigger adaptation callbacks if satisfaction metrics change significantly
            self._check_satisfaction_changes(feedback_entry.user_id)
            
        except Exception as e:
            self.logger.error(f"Failed to process feedback entry: {e}")
    
    def _check_satisfaction_changes(self, user_id: str):
        """Check if satisfaction metrics have changed significantly."""
        try:
            # Get recent satisfaction metrics
            current_metrics = self.analyze_user_satisfaction(user_id, time_window_days=7)
            
            # Trigger adaptation callbacks
            for callback in self.adaptation_callbacks:
                try:
                    callback(current_metrics)
                except Exception as e:
                    self.logger.error(f"Adaptation callback failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to check satisfaction changes: {e}")
    
    def register_adaptation_callback(self, callback: Callable[[SatisfactionMetrics], None]):
        """Register callback for satisfaction changes that should trigger adaptation."""
        self.adaptation_callbacks.append(callback)
    
    def start_background_processing(self):
        """Start background processing thread."""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.stop_processing.clear()
        self.processing_thread = threading.Thread(
            target=self._background_processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        self.logger.info("Started background feedback processing")
    
    def stop_background_processing(self):
        """Stop background processing thread."""
        self.stop_processing.set()
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        self.logger.info("Stopped background feedback processing")
    
    def _background_processing_loop(self):
        """Background processing loop for feedback analysis."""
        while not self.stop_processing.wait(self.processing_interval):
            try:
                # Process unprocessed feedback
                self._process_pending_feedback()
                
                # Cleanup old data
                self._cleanup_old_data()
                
            except Exception as e:
                self.logger.error(f"Background processing error: {e}")
    
    def _process_pending_feedback(self):
        """Process any pending feedback entries."""
        # Implementation for batch processing of pending feedback
        pass
    
    def _cleanup_old_data(self):
        """Clean up old feedback data to manage storage."""
        # Implementation for data cleanup
        pass
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status and statistics."""
        try:
            feedback_stats = self.collector.get_feedback_stats()
            
            status = {
                'feedback_collector': {
                    'total_feedback': feedback_stats.get('total_feedback', 0),
                    'recent_feedback_7d': feedback_stats.get('recent_feedback_7d', 0),
                    'cache_size': feedback_stats.get('cache_size', 0),
                    'feedback_by_type': feedback_stats.get('feedback_by_type', {})
                },
                'sentiment_analyzer': {
                    'nltk_available': NLTK_AVAILABLE,
                    'sklearn_available': SKLEARN_AVAILABLE,
                    'analyzer_type': 'nltk' if NLTK_AVAILABLE else 'fallback'
                },
                'feedback_analyzer': {
                    'correlation_cache_size': len(self.feedback_analyzer.correlation_cache),
                    'trend_cache_size': len(self.feedback_analyzer.trend_cache),
                    'is_trained': self.feedback_analyzer.is_trained
                },
                'background_processing': {
                    'enabled': self.auto_process,
                    'running': self.processing_thread and self.processing_thread.is_alive(),
                    'interval_seconds': self.processing_interval
                },
                'memory_usage': self.memory_tracker.get_memory_usage(),
                'system_health': 'healthy'
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {'system_health': 'error', 'error': str(e)}


# Example usage and testing functions
def demonstrate_feedback_system():
    """Demonstrate the comprehensive feedback system capabilities."""
    # Initialize system
    feedback_system = ComprehensiveFeedbackSystem()
    
    # Simulate user feedback collection
    user_id = "test_user_001"
    session_id = "session_123"
    
    # Collect rating feedback
    feedback_system.collect_rating_feedback(
        user_id=user_id,
        session_id=session_id,
        rating=4,
        max_rating=5,
        category="performance",
        context={"feature": "text_generation", "quality_setting": "high"}
    )
    
    # Collect text feedback
    feedback_system.collect_text_feedback(
        user_id=user_id,
        session_id=session_id,
        text="The system is working great! Very fast and accurate results.",
        category="general"
    )
    
    # Collect behavioral feedback
    feedback_system.collect_behavioral_feedback(
        user_id=user_id,
        session_id=session_id,
        interaction_data={
            "clicks": 15,
            "time_spent_seconds": 180,
            "pages_visited": 3,
            "features_used": ["text_generation", "image_processing"]
        },
        performance_metrics={
            "response_time_ms": 250,
            "memory_usage_mb": 1200,
            "cpu_usage_percent": 45
        }
    )
    
    # Analyze satisfaction
    satisfaction = feedback_system.analyze_user_satisfaction(user_id)
    print(f"User satisfaction: {satisfaction.satisfaction_score:.1f}/100 ({satisfaction.trend_direction})")
    
    # Get system status
    status = feedback_system.get_system_status()
    print(f"System status: {status}")
    
    return feedback_system


if __name__ == "__main__":
    # Run demonstration
    system = demonstrate_feedback_system()
    
    # Show system status
    import pprint
    pprint.pprint(system.get_system_status())
