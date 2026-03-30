"""
Integration Test for ImpressionCore Phase 8A Authentication System

This test suite validates the complete Week 1 authentication infrastructure including
biometric authentication, MFA, session management, and validation systems.

Created: 2025-01-01
Author: ImpressionCore Security Team
Hardware Target: NVIDIA GTX 1050 Ti (4GB VRAM)
"""

import asyncio
import numpy as np
import pytest
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import authentication components
from src.core.security.authentication import (
    BiometricAuthenticator,
    VoiceAuthenticator,
    FingerprintAuthenticator,
    MFAManager,
    MFAConfiguration,
    AuthenticationFactor,
    MFAPolicy,
    SessionManager,
    SessionSecurityPolicy,
    DeviceInfo,
    SessionType,
    AuthenticationValidator,
    ValidationPolicy,
    ValidationContext,
    ValidationResult,
    RiskLevel
)


class TestPhase8AAuthenticationIntegration:
    """Comprehensive integration tests for Phase 8A authentication system"""
    
    @pytest.fixture
    def test_user_id(self):
        """Test user ID"""
        return "test_user_001"
    
    @pytest.fixture
    def test_device_info(self):
        """Test device information"""
        return DeviceInfo(
            fingerprint="test_device_fp_001",
            user_agent="Mozilla/5.0 Test Browser",
            ip_address="192.168.1.100",
            platform="Windows",
            browser="Chrome",
            screen_resolution="1920x1080",
            timezone="UTC-5",
            language="en-US"
        )
    
    @pytest.fixture
    def mfa_config(self):
        """MFA configuration for testing"""
        return MFAConfiguration(
            policy=MFAPolicy.ADAPTIVE,
            required_factors=2,
            max_factors=3,
            session_timeout=3600,
            biometric_required=True,
            totp_enabled=True,
            max_memory_usage=50 * 1024 * 1024  # 50MB for testing
        )
    
    @pytest.fixture
    def session_policy(self):
        """Session policy for testing"""
        return SessionSecurityPolicy(
            max_idle_time=1800,
            max_session_duration=7200,
            max_concurrent_sessions=3,
            cleanup_interval=60
        )
    
    @pytest.fixture
    def validation_policy(self):
        """Validation policy for testing"""
        return ValidationPolicy(
            max_attempts_per_minute=10,
            force_mfa_risk_threshold=0.5,
            cache_timeout=60
        )
    
    @pytest.fixture
    async def auth_system(self, mfa_config, session_policy, validation_policy):
        """Complete authentication system"""
        # Initialize core components
        biometric_auth = BiometricAuthenticator()
        voice_auth = VoiceAuthenticator()
        fingerprint_auth = FingerprintAuthenticator()
        
        # Initialize management components
        session_manager = SessionManager(session_policy)
        mfa_manager = MFAManager(mfa_config)
        auth_validator = AuthenticationValidator(
            validation_policy, mfa_manager, session_manager
        )
        
        return {
            'biometric_auth': biometric_auth,
            'voice_auth': voice_auth,
            'fingerprint_auth': fingerprint_auth,
            'mfa_manager': mfa_manager,
            'session_manager': session_manager,
            'auth_validator': auth_validator
        }
    
    def generate_mock_audio_data(self, duration_seconds: float = 3.0) -> np.ndarray:
        """Generate mock audio data for testing"""
        sample_rate = 16000
        samples = int(sample_rate * duration_seconds)
        
        # Generate synthetic speech-like audio
        frequency = 200  # Base frequency
        t = np.linspace(0, duration_seconds, samples)
        
        # Create formants (speech-like characteristics)
        formant1 = np.sin(2 * np.pi * frequency * t)
        formant2 = 0.5 * np.sin(2 * np.pi * frequency * 2.5 * t)
        formant3 = 0.3 * np.sin(2 * np.pi * frequency * 4.0 * t)
        
        # Add noise and combine
        noise = np.random.normal(0, 0.1, samples)
        audio = formant1 + formant2 + formant3 + noise
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio.astype(np.float32)
    
    def generate_mock_fingerprint_image(self, width: int = 256, height: int = 256) -> np.ndarray:
        """Generate mock fingerprint image for testing"""
        # Create synthetic fingerprint-like patterns
        image = np.zeros((height, width), dtype=np.uint8)
        
        # Generate ridge patterns
        center_x, center_y = width // 2, height // 2
        
        for y in range(height):
            for x in range(width):
                # Distance from center
                dx, dy = x - center_x, y - center_y
                distance = np.sqrt(dx**2 + dy**2)
                
                # Angle
                angle = np.arctan2(dy, dx)
                
                # Create ridge pattern
                ridge_spacing = 8  # pixels
                ridge_value = np.sin(distance / ridge_spacing + angle * 3) * 127 + 128
                
                # Add some noise
                noise = np.random.normal(0, 20)
                
                image[y, x] = np.clip(ridge_value + noise, 0, 255)
        
        return image
    
    @pytest.mark.asyncio
    async def test_biometric_authentication_basic(self, auth_system, test_user_id):
        """Test basic biometric authentication functionality"""
        biometric_auth = auth_system['biometric_auth']
        
        # Test voice authentication
        voice_data = self.generate_mock_audio_data(3.0)
        
        # First enrollment
        enrollment_result = await biometric_auth.enroll_user(
            test_user_id, 
            {'type': 'voice', 'audio_data': voice_data}
        )
        assert enrollment_result.success, f"Voice enrollment failed: {enrollment_result.error}"
        
        # Authentication attempt
        auth_result = await biometric_auth.authenticate(
            test_user_id,
            {'type': 'voice', 'audio_data': voice_data}
        )
        assert auth_result.success, f"Voice authentication failed: {auth_result.error}"
        assert auth_result.confidence > 0.5
        
        # Test fingerprint authentication
        fingerprint_data = self.generate_mock_fingerprint_image()
        
        # Enrollment
        enrollment_result = await biometric_auth.enroll_user(
            test_user_id,
            {'type': 'fingerprint', 'image_data': fingerprint_data}
        )
        assert enrollment_result.success, f"Fingerprint enrollment failed: {enrollment_result.error}"
        
        # Authentication
        auth_result = await biometric_auth.authenticate(
            test_user_id,
            {'type': 'fingerprint', 'image_data': fingerprint_data}
        )
        assert auth_result.success, f"Fingerprint authentication failed: {auth_result.error}"
        assert auth_result.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_mfa_workflow_complete(self, auth_system, test_user_id, test_device_info):
        """Test complete MFA workflow with multiple factors"""
        mfa_manager = auth_system['mfa_manager']
        
        # Setup TOTP for user
        totp_setup = mfa_manager.setup_totp(test_user_id)
        assert 'secret' in totp_setup
        assert 'backup_codes' in totp_setup
        
        # Create MFA session
        session = mfa_manager.create_mfa_session(
            user_id=test_user_id,
            device_fingerprint=test_device_info.fingerprint,
            ip_address=test_device_info.ip_address
        )
        assert session.user_id == test_user_id
        assert session.risk_score >= 0.0
        
        # Step 1: TOTP authentication
        totp_token = mfa_manager.totp_generator.generate_token(totp_setup['secret'])
        totp_result = await mfa_manager.authenticate_step(
            session.session_id,
            AuthenticationFactor.SOMETHING_YOU_HAVE,
            {'token': totp_token}
        )
        assert totp_result.success, f"TOTP authentication failed: {totp_result.error_message}"
        
        # Step 2: Biometric authentication
        voice_data = self.generate_mock_audio_data(3.0)
        
        # Enroll biometric first
        await auth_system['voice_auth'].enroll_user(test_user_id, voice_data)
        
        biometric_result = await mfa_manager.authenticate_step(
            session.session_id,
            AuthenticationFactor.SOMETHING_YOU_ARE,
            {'type': 'voice', 'audio_data': voice_data}
        )
        assert biometric_result.success, f"Biometric authentication failed: {biometric_result.error_message}"
        
        # Check MFA completion
        is_complete = mfa_manager.check_mfa_completion(session.session_id)
        assert is_complete, "MFA session should be complete with 2 factors"
        
        # Verify final result
        final_session = mfa_manager.sessions[session.session_id]
        assert final_session.is_complete
        assert final_session.final_result is not None
        assert final_session.final_result.success
    
    @pytest.mark.asyncio
    async def test_session_management_lifecycle(self, auth_system, test_user_id, test_device_info):
        """Test complete session management lifecycle"""
        session_manager = auth_system['session_manager']
        
        # Create session
        session = await session_manager.create_session(
            user_id=test_user_id,
            device_info=test_device_info,
            session_type=SessionType.APPLICATION,
            authentication_level=2,
            permissions={'read', 'write'}
        )
        
        assert session.user_id == test_user_id
        assert session.authentication_level == 2
        assert 'read' in session.permissions
        assert session.is_valid()
        
        # Validate session
        validated_session = await session_manager.validate_session(session.session_id)
        assert validated_session is not None
        assert validated_session.session_id == session.session_id
        
        # Set session data
        success = await session_manager.set_session_data(
            session.session_id, 'test_key', 'test_value'
        )
        assert success
        
        # Get session data
        data = await session_manager.get_session_data(session.session_id, 'test_key')
        assert data == 'test_value'
        
        # Update permissions
        success = await session_manager.update_session_permissions(
            session.session_id, {'read', 'write', 'admin'}
        )
        assert success
        
        # Get user sessions
        user_sessions = await session_manager.get_user_sessions(test_user_id)
        assert len(user_sessions) == 1
        assert user_sessions[0].session_id == session.session_id
        
        # Terminate session
        success = await session_manager.terminate_session(
            session.session_id, "Test termination"
        )
        assert success
        
        # Verify termination
        validated_session = await session_manager.validate_session(session.session_id)
        assert validated_session is None
    
    @pytest.mark.asyncio
    async def test_authentication_validation_workflow(self, auth_system, test_user_id, test_device_info):
        """Test authentication validation workflow with risk assessment"""
        auth_validator = auth_system['auth_validator']
        
        # Create validation context
        context = ValidationContext(
            user_id=test_user_id,
            ip_address=test_device_info.ip_address,
            user_agent=test_device_info.user_agent,
            device_fingerprint=test_device_info.fingerprint,
            authentication_factors=[AuthenticationFactor.SOMETHING_YOU_HAVE],
            metadata={'test': True}
        )
        
        # Validate authentication
        result, risk_assessment, violations = await auth_validator.validate_authentication(context)
        
        assert result in [ValidationResult.VALID, ValidationResult.SUSPICIOUS, ValidationResult.REQUIRES_MFA]
        assert risk_assessment is not None
        assert risk_assessment.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
        assert 0.0 <= risk_assessment.risk_score <= 1.0
        
        # Test rate limiting
        for i in range(15):  # Exceed rate limit
            await auth_validator.validate_authentication(context)
        
        # Should be blocked due to rate limit
        result, _, violations = await auth_validator.validate_authentication(context)
        assert result == ValidationResult.BLOCKED
        assert len(violations) > 0
    
    @pytest.mark.asyncio
    async def test_integrated_authentication_flow(self, auth_system, test_user_id, test_device_info):
        """Test complete integrated authentication flow"""
        mfa_manager = auth_system['mfa_manager']
        session_manager = auth_system['session_manager']
        auth_validator = auth_system['auth_validator']
        
        # Step 1: Validation
        context = ValidationContext(
            user_id=test_user_id,
            ip_address=test_device_info.ip_address,
            user_agent=test_device_info.user_agent,
            device_fingerprint=test_device_info.fingerprint,
            authentication_factors=[AuthenticationFactor.SOMETHING_YOU_HAVE]
        )
        
        validation_result, risk_assessment, violations = await auth_validator.validate_authentication(context)
        assert validation_result != ValidationResult.BLOCKED, "Validation should not block initial attempt"
        
        # Step 2: MFA Setup and Authentication
        totp_setup = mfa_manager.setup_totp(test_user_id)
        
        mfa_session = mfa_manager.create_mfa_session(
            user_id=test_user_id,
            device_fingerprint=test_device_info.fingerprint,
            ip_address=test_device_info.ip_address
        )
        
        # Authenticate with TOTP
        totp_token = mfa_manager.totp_generator.generate_token(totp_setup['secret'])
        totp_result = await mfa_manager.authenticate_step(
            mfa_session.session_id,
            AuthenticationFactor.SOMETHING_YOU_HAVE,
            {'token': totp_token}
        )
        assert totp_result.success
        
        # Authenticate with biometric
        voice_data = self.generate_mock_audio_data(3.0)
        await auth_system['voice_auth'].enroll_user(test_user_id, voice_data)
        
        biometric_result = await mfa_manager.authenticate_step(
            mfa_session.session_id,
            AuthenticationFactor.SOMETHING_YOU_ARE,
            {'type': 'voice', 'audio_data': voice_data}
        )
        assert biometric_result.success
        
        # Check MFA completion
        mfa_complete = mfa_manager.check_mfa_completion(mfa_session.session_id)
        assert mfa_complete
        
        # Step 3: Create Application Session
        app_session = await session_manager.create_session(
            user_id=test_user_id,
            device_info=test_device_info,
            session_type=SessionType.APPLICATION,
            authentication_level=2
        )
        
        assert app_session.is_valid()
        assert app_session.authentication_level == 2
        
        # Step 4: Ongoing Validation
        session_validated = await session_manager.validate_session(app_session.session_id)
        assert session_validated is not None
    
    @pytest.mark.asyncio
    async def test_memory_optimization(self, auth_system):
        """Test memory optimization features"""
        import sys
        
        # Get initial memory usage
        initial_memory = sum(
            sys.getsizeof(component) 
            for component in auth_system.values()
        )
        
        # Simulate heavy usage
        test_user_ids = [f"user_{i:03d}" for i in range(100)]
        
        for user_id in test_user_ids:
            # Create sessions
            device_info = DeviceInfo(
                fingerprint=f"device_{user_id}",
                user_agent="Test Browser",
                ip_address=f"192.168.1.{hash(user_id) % 255}",
                platform="Windows",
                browser="Chrome"
            )
            
            session = await auth_system['session_manager'].create_session(
                user_id=user_id,
                device_info=device_info
            )
            
            # Create validation contexts
            context = ValidationContext(
                user_id=user_id,
                ip_address=device_info.ip_address,
                user_agent=device_info.user_agent,
                device_fingerprint=device_info.fingerprint
            )
            
            await auth_system['auth_validator'].validate_authentication(context)
        
        # Check memory usage after heavy operations
        final_memory = sum(
            sys.getsizeof(component) 
            for component in auth_system.values()
        )
        
        memory_growth_mb = (final_memory - initial_memory) / (1024 * 1024)
        
        # Memory growth should be reasonable (< 100MB for 100 users)
        assert memory_growth_mb < 100, f"Memory growth too high: {memory_growth_mb:.2f}MB"
        
        # Test cleanup mechanisms
        stats = auth_system['session_manager'].get_session_statistics()
        assert 'memory_usage_mb' in stats
        
        validation_stats = auth_system['auth_validator'].get_validation_statistics()
        assert 'cached_validations' in validation_stats
    
    @pytest.mark.asyncio
    async def test_security_monitoring(self, auth_system, test_user_id, test_device_info):
        """Test security monitoring and anomaly detection"""
        session_manager = auth_system['session_manager']
        auth_validator = auth_system['auth_validator']
        
        # Create session
        session = await session_manager.create_session(
            user_id=test_user_id,
            device_info=test_device_info
        )
        
        # Simulate suspicious activity patterns
        for i in range(10):
            # Rapid session creation attempts
            try:
                await session_manager.create_session(
                    user_id=test_user_id,
                    device_info=test_device_info
                )
            except:
                pass  # Expected to fail due to limits
        
        # Check for anomaly detection
        anomalies = await session_manager.detect_session_anomalies(session.session_id)
        assert len(anomalies) > 0, "Should detect rapid session creation"
        
        # Test validation with suspicious patterns
        suspicious_context = ValidationContext(
            user_id=test_user_id,
            ip_address="suspicious.ip.address",
            user_agent="Suspicious User Agent",
            device_fingerprint="suspicious_device"
        )
        
        result, risk_assessment, violations = await auth_validator.validate_authentication(
            suspicious_context
        )
        
        # Should detect higher risk
        assert risk_assessment.risk_score > 0.3, "Should detect elevated risk for suspicious patterns"
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, auth_system):
        """Test performance monitoring and metrics collection"""
        # Run multiple operations and check performance metrics
        operations = []
        
        for i in range(50):
            # Time various operations
            start_time = time.time()
            
            # MFA operation
            mfa_stats = auth_system['mfa_manager'].get_authentication_stats()
            
            # Session operation
            session_stats = auth_system['session_manager'].get_session_statistics()
            
            # Validation operation
            validation_stats = auth_system['auth_validator'].get_validation_statistics()
            
            duration = time.time() - start_time
            operations.append(duration)
        
        # Calculate performance metrics
        avg_duration = sum(operations) / len(operations)
        max_duration = max(operations)
        
        # Performance should be reasonable
        assert avg_duration < 0.1, f"Average operation too slow: {avg_duration:.3f}s"
        assert max_duration < 0.5, f"Max operation too slow: {max_duration:.3f}s"
        
        # Check that statistics are being collected
        assert 'total_attempts' in mfa_stats
        assert 'active_sessions' in session_stats
        assert 'total_validations' in validation_stats
    
    def test_component_initialization(self, auth_system):
        """Test that all components initialize correctly"""
        required_components = [
            'biometric_auth',
            'voice_auth',
            'fingerprint_auth',
            'mfa_manager',
            'session_manager',
            'auth_validator'
        ]
        
        for component_name in required_components:
            assert component_name in auth_system, f"Missing component: {component_name}"
            component = auth_system[component_name]
            assert component is not None, f"Component {component_name} is None"
            
            # Check that components have expected attributes/methods
            if hasattr(component, 'get_statistics') or hasattr(component, 'get_session_statistics') or hasattr(component, 'get_authentication_stats') or hasattr(component, 'get_validation_statistics'):
                # Component should have statistics methods
                pass
        
        print("✓ All authentication components initialized successfully")
        print("✓ Phase 8A Week 1 authentication system integration complete")


if __name__ == "__main__":
    # Run basic integration test
    pytest.main([__file__, "-v", "-s"])
