"""Unit tests for the Intelligent User Profiles System (src/core/ux/user_profiles.py)."""

import os
import tempfile
import pytest
from src.core.ux.user_profiles import (
    UserPersonality,
    WorkloadType,
    UsageContext,
    UserProfile,
    UserSession,
    UserProfilesSystem,
    create_user_profiles_system
)


class TestUserProfilesSystem:
    """Suite of tests for the user profiles system."""

    @pytest.fixture
    def temp_data_dir(self):
        """Temporary directory for storing profile database."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_create_system_and_profiles(self, temp_data_dir):
        """System initializes and can create user profiles with defaults."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        assert system.enable_ml is False

        user_id = "user_test_1"
        profile = system.create_user_profile(user_id)
        
        assert isinstance(profile, UserProfile)
        assert profile.user_id == user_id
        assert profile.personality_type == UserPersonality.BALANCED
        assert profile.total_sessions == 0

        # Create again returns the cached profile
        profile2 = system.create_user_profile(user_id)
        assert profile is profile2

    def test_apply_initial_preferences(self, temp_data_dir):
        """System respects initial preferences when creating a user profile."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        
        initial = {
            "quality_vs_speed": 0.8,
            "personality_type": "quality_focused",
            "preferred_latency_ms": 350.0,
            "preferred_quality_threshold": 0.98
        }
        
        profile = system.create_user_profile("user_pref", initial)
        assert profile.quality_vs_speed_preference == 0.8
        assert profile.personality_type == UserPersonality.QUALITY_FOCUSED
        assert profile.preferred_latency_ms == 350.0
        assert profile.preferred_quality_threshold == 0.98

    def test_session_lifecycle_and_learning(self, temp_data_dir):
        """Sessions can be started, updated, ended, and trigger profile learning."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        user_id = "learner_1"
        session_id = "session_x"

        # Start session
        session = system.start_session(user_id, session_id, context=UsageContext.INTERACTIVE)
        assert isinstance(session, UserSession)
        assert session.session_id == session_id
        assert session.user_id == user_id
        assert session_id in system.active_sessions

        # Update metrics
        system.update_session_metrics(session_id, {
            "tokens_processed": 500,
            "latency_ms": 120,
            "quality_score": 0.96,
            "memory_usage_gb": 1.8,
            "feature_used": "imagination_loop",
            "manual_adjustment": {"resolution": "high"}
        })

        # Check in-progress session updates
        active_sess = system.active_sessions[session_id]
        assert active_sess.total_tokens_processed == 500
        assert active_sess.average_latency_ms == 120
        assert active_sess.quality_scores == [0.96]
        assert active_sess.memory_usage_peak_gb == 1.8
        assert active_sess.feature_usage["imagination_loop"] == 1
        assert len(active_sess.manual_adjustments) == 1

        # End session
        system.end_session(session_id, user_satisfaction=5.0)
        assert session_id not in system.active_sessions

        # Verify learning in profile
        profile = system.create_user_profile(user_id)
        assert profile.total_sessions == 1
        assert profile.preferred_quality_threshold == pytest.approx(0.96, rel=1e-2)
        assert profile.latency_tolerance_ms >= 120

    def test_personality_inference(self, temp_data_dir):
        """Rule-based personality inference detects different styles."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        
        # Test Power User inference (high manual control, feature explorer)
        user_id = "power_guy"
        session = system.start_session(user_id, "s_power")
        
        # Simulate many adjustments and feature usages
        for i in range(5):
            system.update_session_metrics("s_power", {"manual_adjustment": {"param": i}})
        for i in range(10):
            system.update_session_metrics("s_power", {"feature_used": f"feat_{i}"})
            
        system.end_session("s_power", user_satisfaction=4.0)
        profile = system.create_user_profile(user_id)
        # Verify personality update has been processed
        assert profile.personality_type == UserPersonality.POWER_USER

    def test_optimization_recommendations(self, temp_data_dir):
        """Recommendations adapt to user profiles and current contexts."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        
        # Default for unknown user
        default_recs = system.get_optimization_recommendations("unknown_user")
        assert default_recs["resolution_level"] == "adaptive"
        assert default_recs["target_latency_ms"] == 200.0

        # Recs for speed focused user
        user_speed = "speedy"
        profile = system.create_user_profile(user_speed, {
            "personality_type": "speed_focused",
            "preferred_latency_ms": 100.0,
            "latency_tolerance_ms": 100.0
        })
        speed_recs = system.get_optimization_recommendations(user_speed)
        assert speed_recs["resolution_level"] == "medium"
        assert speed_recs["target_latency_ms"] == 100.0

        # Quick task context override
        quick_recs = system.get_optimization_recommendations(user_speed, context=UsageContext.QUICK_TASK)
        assert quick_recs["target_latency_ms"] == pytest.approx(70.0)

    def test_predict_satisfaction(self, temp_data_dir):
        """Satisfaction predictions score alignment with preferences and personality."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        user_id = "quality_lover"
        profile = system.create_user_profile(user_id, {
            "personality_type": "quality_focused",
            "preferred_quality_threshold": 0.99
        })
        profile.latency_tolerance_ms = 100.0

        # Aligning config
        high_quality_config = {
            "preferred_quality_threshold": 0.99,
            "target_latency_ms": 300,
            "resolution_level": "ultra_high"
        }
        score_good = system.predict_user_satisfaction(user_id, high_quality_config)

        # Misaligning config
        low_quality_config = {
            "preferred_quality_threshold": 0.50,
            "target_latency_ms": 1200,
            "resolution_level": "low"
        }
        score_bad = system.predict_user_satisfaction(user_id, low_quality_config)

        assert score_good > score_bad

    def test_user_analytics(self, temp_data_dir):
        """User analytics exposes formatted profile summaries."""
        system = create_user_profiles_system(data_directory=temp_data_dir, enable_ml=False)
        user_id = "analytics_user"
        system.create_user_profile(user_id)

        analytics = system.get_user_analytics(user_id)
        assert "profile_summary" in analytics
        assert "preferences" in analytics
        assert "usage_patterns" in analytics
        assert analytics["profile_summary"]["user_id"] == user_id
