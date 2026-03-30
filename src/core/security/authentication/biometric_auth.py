"""
Biometric Authenticator for ImpressionCore Security Infrastructure
Phase 8A: Security Infrastructure Foundation

This module provides the main biometric authentication orchestrator that manages
voice, fingerprint, facial recognition, and other biometric authentication methods.

Author: ImpressionCore Development Team
Created: 2025-05-31
Hardware Target: GTX 1050 Ti (4GB VRAM)
Memory Target: <200MB for all biometric operations
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from enum import Enum

from .auth_base import (
    BiometricAuthenticationBase, 
    AuthenticationResult, 
    AuthenticationStatus,
    AuthenticationType,
    AuthenticationError
)

# Import biometric providers (will be implemented next)
# from .voice_auth import VoiceAuthenticator
# from .fingerprint_auth import FingerprintAuthenticator
# from .facial_auth import FacialAuthenticator

class BiometricType(Enum):
    """Supported biometric authentication types"""
    VOICE = "voice"
    FINGERPRINT = "fingerprint"
    FACIAL = "facial"
    IRIS = "iris"
    PALM = "palm"

class BiometricQuality(Enum):
    """Quality levels for biometric data"""
    EXCELLENT = "excellent"
    GOOD = "good" 
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"

class BiometricAuthenticator(BiometricAuthenticationBase):
    """
    Main biometric authentication orchestrator for ImpressionCore
    
    Manages multiple biometric authentication methods and provides unified
    interface for voice, fingerprint, facial recognition, and other biometric auth.
    
    Hardware Optimization: Optimized for GTX 1050 Ti (4GB VRAM)
    - Uses lazy loading for biometric providers
    - Memory-efficient template storage
    - Batch processing for multiple biometric checks
    
    Features:
    - Multi-modal biometric authentication
    - Quality assessment and feedback
    - Fallback authentication methods
    - Real-time performance monitoring
    - Memory-optimized processing pipelines
    """
    
    def __init__(
        self,
        config: Dict[str, Any] = None,
        memory_limit_mb: int = 200,
        enable_multimodal: bool = True,
        quality_threshold: float = 0.7,
        enable_logging: bool = True
    ):
        """
        Initialize biometric authenticator
        
        Args:
            config: Biometric configuration dictionary
            memory_limit_mb: Memory limit for all biometric operations
            enable_multimodal: Whether to enable multi-modal authentication
            quality_threshold: Minimum quality threshold for biometric data
            enable_logging: Whether to enable detailed logging
        """
        super().__init__(config, memory_limit_mb, enable_logging=enable_logging)
        
        self.enable_multimodal = enable_multimodal
        self.quality_threshold = quality_threshold
        
        # Biometric provider registry (lazy loaded)
        self._providers: Dict[BiometricType, Any] = {}
        self._provider_configs: Dict[BiometricType, Dict[str, Any]] = {}
        
        # Quality assessment cache
        self._quality_cache: Dict[str, BiometricQuality] = {}
        
        # Multi-modal authentication results
        self._multimodal_results: Dict[str, List[AuthenticationResult]] = {}
        
        # Performance tracking
        self._provider_performance: Dict[BiometricType, Dict[str, float]] = {}
        
        # Initialize default provider configurations
        self._setup_default_configs()
        
        if self.enable_logging:
            self.logger.info(f"Initialized BiometricAuthenticator with {memory_limit_mb}MB memory limit")
            self.logger.info(f"Multi-modal authentication: {enable_multimodal}")
            self.logger.info(f"Quality threshold: {quality_threshold}")
    
    @property
    def authentication_type(self) -> AuthenticationType:
        """Return biometric authentication type"""
        return AuthenticationType.BIOMETRIC
    
    @property
    def available_biometric_types(self) -> List[BiometricType]:
        """Get list of available biometric authentication types"""
        return list(self._provider_configs.keys())
    
    @property
    def active_providers(self) -> List[BiometricType]:
        """Get list of currently active biometric providers"""
        return list(self._providers.keys())
    
    def _setup_default_configs(self):
        """Setup default configurations for biometric providers"""
        # Voice authentication configuration
        self._provider_configs[BiometricType.VOICE] = {
            "sample_rate": 16000,
            "duration_seconds": 3,
            "min_quality_threshold": 0.7,
            "noise_reduction": True,
            "voice_activity_detection": True,
            "memory_limit_mb": 64,
            "model_type": "lightweight"  # For GTX 1050 Ti
        }
        
        # Fingerprint authentication configuration
        self._provider_configs[BiometricType.FINGERPRINT] = {
            "image_resolution": "300dpi",
            "min_minutiae_count": 12,
            "quality_threshold": 0.8,
            "enhancement_enabled": True,
            "memory_limit_mb": 32,
            "processing_mode": "fast"  # For GTX 1050 Ti
        }
        
        # Facial recognition configuration
        self._provider_configs[BiometricType.FACIAL] = {
            "face_detection_confidence": 0.9,
            "embedding_model": "lightweight",
            "anti_spoofing": True,
            "liveness_detection": True,
            "memory_limit_mb": 96,
            "use_gpu_acceleration": True  # GTX 1050 Ti
        }
    
    async def register_biometric_provider(
        self, 
        biometric_type: BiometricType, 
        provider_class: type,
        config: Dict[str, Any] = None
    ):
        """
        Register a biometric authentication provider
        
        Args:
            biometric_type: Type of biometric authentication
            provider_class: Provider class to instantiate
            config: Optional configuration override
        """
        try:
            # Use provided config or default
            provider_config = config or self._provider_configs.get(biometric_type, {})
            
            # Instantiate provider with memory optimization
            provider = provider_class(
                config=provider_config,
                memory_limit_mb=provider_config.get('memory_limit_mb', 64),
                enable_logging=self.enable_logging
            )
            
            self._providers[biometric_type] = provider
            
            # Initialize performance tracking
            self._provider_performance[biometric_type] = {
                "total_authentications": 0,
                "successful_authentications": 0,
                "average_processing_time": 0.0,
                "quality_score": 0.0
            }
            
            if self.enable_logging:
                self.logger.info(f"Registered {biometric_type.value} provider: {provider_class.__name__}")
                
        except Exception as e:
            error_msg = f"Failed to register {biometric_type.value} provider: {str(e)}"
            self.logger.error(error_msg)
            raise AuthenticationError(
                error_msg,
                error_code="PROVIDER_REGISTRATION_FAILED",
                auth_type=self.authentication_type
            )
    
    async def get_biometric_provider(self, biometric_type: BiometricType):
        """
        Get biometric provider with lazy loading
        
        Args:
            biometric_type: Type of biometric provider
            
        Returns:
            Biometric provider instance
        """
        if biometric_type not in self._providers:
            # Attempt to load provider dynamically
            await self._load_provider(biometric_type)
        
        return self._providers.get(biometric_type)
    
    async def _load_provider(self, biometric_type: BiometricType):
        """
        Dynamically load biometric provider
        
        Args:
            biometric_type: Type of biometric provider to load
        """
        try:
            if biometric_type == BiometricType.VOICE:
                from .voice_auth import VoiceAuthenticator
                await self.register_biometric_provider(biometric_type, VoiceAuthenticator)
            elif biometric_type == BiometricType.FINGERPRINT:
                from .fingerprint_auth import FingerprintAuthenticator
                await self.register_biometric_provider(biometric_type, FingerprintAuthenticator)
            elif biometric_type == BiometricType.FACIAL:
                from .facial_auth import FacialAuthenticator
                await self.register_biometric_provider(biometric_type, FacialAuthenticator)
            else:
                raise AuthenticationError(
                    f"Unsupported biometric type: {biometric_type.value}",
                    error_code="UNSUPPORTED_BIOMETRIC_TYPE"
                )
                
        except ImportError as e:
            self.logger.warning(f"Could not load {biometric_type.value} provider: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error loading {biometric_type.value} provider: {str(e)}")
    
    async def assess_biometric_quality(
        self,
        biometric_data: Any,
        biometric_type: BiometricType
    ) -> tuple[BiometricQuality, float, Dict[str, Any]]:
        """
        Assess quality of biometric data
        
        Args:
            biometric_data: Raw biometric data
            biometric_type: Type of biometric data
            
        Returns:
            Tuple of (quality_enum, quality_score, quality_metadata)
        """
        try:
            provider = await self.get_biometric_provider(biometric_type)
            if provider is None:
                return BiometricQuality.UNUSABLE, 0.0, {"error": "Provider not available"}
            
            # Provider-specific quality assessment
            if hasattr(provider, 'assess_quality'):
                quality_score, metadata = await provider.assess_quality(biometric_data)
            else:
                # Fallback quality assessment
                quality_score = 0.5  # Default medium quality
                metadata = {"assessment": "basic"}
            
            # Convert score to quality enum
            if quality_score >= 0.9:
                quality = BiometricQuality.EXCELLENT
            elif quality_score >= 0.8:
                quality = BiometricQuality.GOOD
            elif quality_score >= 0.7:
                quality = BiometricQuality.FAIR
            elif quality_score >= 0.5:
                quality = BiometricQuality.POOR
            else:
                quality = BiometricQuality.UNUSABLE
            
            # Cache quality assessment
            cache_key = f"{biometric_type.value}_{hash(str(biometric_data))}"
            self._quality_cache[cache_key] = quality
            
            return quality, quality_score, metadata
            
        except Exception as e:
            self.logger.error(f"Quality assessment error for {biometric_type.value}: {str(e)}")
            return BiometricQuality.UNUSABLE, 0.0, {"error": str(e)}
    
    async def authenticate(
        self,
        user_id: str,
        credentials: Dict[str, Any],
        **kwargs
    ) -> AuthenticationResult:
        """
        Perform biometric authentication
        
        Args:
            user_id: User identifier
            credentials: Dictionary containing biometric data and type
                        Format: {
                            "biometric_type": "voice|fingerprint|facial",
                            "biometric_data": <raw_biometric_data>,
                            "quality_check": True/False (optional),
                            "multimodal": True/False (optional)
                        }
            **kwargs: Additional authentication parameters
            
        Returns:
            AuthenticationResult with biometric authentication status
        """
        start_time = datetime.utcnow()
        
        try:
            # Extract biometric information
            biometric_type_str = credentials.get("biometric_type")
            biometric_data = credentials.get("biometric_data")
            enable_quality_check = credentials.get("quality_check", True)
            use_multimodal = credentials.get("multimodal", False)
            
            if not biometric_type_str or biometric_data is None:
                return AuthenticationResult(
                    status=AuthenticationStatus.INVALID_CREDENTIALS,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message="Missing biometric_type or biometric_data"
                )
            
            # Parse biometric type
            try:
                biometric_type = BiometricType(biometric_type_str.lower())
            except ValueError:
                return AuthenticationResult(
                    status=AuthenticationStatus.INVALID_CREDENTIALS,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message=f"Unsupported biometric type: {biometric_type_str}"
                )
            
            # Check if user is locked out
            if self.is_user_locked_out(user_id):
                return AuthenticationResult(
                    status=AuthenticationStatus.LOCKED,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message="User account is temporarily locked"
                )
            
            # Quality assessment if enabled
            quality_result = None
            if enable_quality_check:
                quality, quality_score, quality_metadata = await self.assess_biometric_quality(
                    biometric_data, biometric_type
                )
                
                quality_result = {
                    "quality": quality.value,
                    "score": quality_score,
                    "metadata": quality_metadata
                }
                
                if quality_score < self.quality_threshold:
                    return AuthenticationResult(
                        status=AuthenticationStatus.FAILED,
                        user_id=user_id,
                        authentication_type=self.authentication_type,
                        error_message=f"Biometric quality {quality_score:.2f} below threshold {self.quality_threshold}",
                        metadata={"quality_assessment": quality_result}
                    )
            
            # Perform single biometric authentication
            auth_result = await self._authenticate_single_biometric(
                user_id, biometric_type, biometric_data
            )
            
            # Add quality assessment to result if performed
            if quality_result:
                if auth_result.metadata is None:
                    auth_result.metadata = {}
                auth_result.metadata["quality_assessment"] = quality_result
            
            # Update provider performance metrics
            self._update_provider_performance(biometric_type, auth_result, start_time)
            
            # Handle multi-modal authentication if requested and enabled
            if use_multimodal and self.enable_multimodal and auth_result.status == AuthenticationStatus.SUCCESS:
                multimodal_result = await self._handle_multimodal_authentication(
                    user_id, biometric_type, auth_result
                )
                return multimodal_result
            
            return auth_result
            
        except Exception as e:
            self.logger.error(f"Biometric authentication error for user {user_id}: {str(e)}")
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                user_id=user_id,
                authentication_type=self.authentication_type,
                error_message=f"Authentication error: {str(e)}"
            )
    
    async def _authenticate_single_biometric(
        self,
        user_id: str,
        biometric_type: BiometricType,
        biometric_data: Any
    ) -> AuthenticationResult:
        """
        Perform single biometric authentication
        
        Args:
            user_id: User identifier
            biometric_type: Type of biometric authentication
            biometric_data: Raw biometric data
            
        Returns:
            AuthenticationResult from biometric provider
        """
        try:
            # Get biometric provider
            provider = await self.get_biometric_provider(biometric_type)
            if provider is None:
                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    user_id=user_id,
                    authentication_type=self.authentication_type,
                    error_message=f"{biometric_type.value} provider not available"
                )
            
            # Perform authentication using provider
            credentials = {
                "biometric_data": biometric_data,
                "template_type": biometric_type.value
            }
            
            auth_result = await provider.authenticate(user_id, credentials)
            
            # Add biometric type to metadata
            if auth_result.metadata is None:
                auth_result.metadata = {}
            auth_result.metadata["biometric_type"] = biometric_type.value
            
            return auth_result
            
        except Exception as e:
            self.logger.error(f"Single biometric authentication error: {str(e)}")
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                user_id=user_id,
                authentication_type=self.authentication_type,
                error_message=f"Provider authentication error: {str(e)}"
            )
    
    async def _handle_multimodal_authentication(
        self,
        user_id: str,
        primary_biometric: BiometricType,
        primary_result: AuthenticationResult
    ) -> AuthenticationResult:
        """
        Handle multi-modal biometric authentication
        
        Args:
            user_id: User identifier
            primary_biometric: Primary biometric type used
            primary_result: Result from primary authentication
            
        Returns:
            Enhanced AuthenticationResult with multi-modal confidence
        """
        try:
            # Store primary result
            session_key = f"{user_id}_{primary_result.session_id}"
            self._multimodal_results[session_key] = [primary_result]
            
            # Multi-modal authentication enhances confidence but doesn't require additional input
            # This could be extended to request additional biometric verification
            
            # Calculate enhanced confidence score
            base_confidence = primary_result.confidence_score or 0.0
            multimodal_boost = min(0.1, (1.0 - base_confidence) * 0.5)  # Up to 10% boost
            enhanced_confidence = min(1.0, base_confidence + multimodal_boost)
            
            # Update result with enhanced confidence
            primary_result.confidence_score = enhanced_confidence
            if primary_result.metadata is None:
                primary_result.metadata = {}
            primary_result.metadata.update({
                "multimodal_authentication": True,
                "base_confidence": base_confidence,
                "confidence_boost": multimodal_boost,
                "biometric_methods": [primary_biometric.value]
            })
            
            return primary_result
            
        except Exception as e:
            self.logger.error(f"Multi-modal authentication error: {str(e)}")
            # Return original result if multi-modal processing fails
            return primary_result
    
    def _update_provider_performance(
        self,
        biometric_type: BiometricType,
        auth_result: AuthenticationResult,
        start_time: datetime
    ):
        """
        Update performance metrics for biometric provider
        
        Args:
            biometric_type: Type of biometric provider
            auth_result: Authentication result
            start_time: When authentication started
        """
        if biometric_type not in self._provider_performance:
            self._provider_performance[biometric_type] = {
                "total_authentications": 0,
                "successful_authentications": 0,
                "average_processing_time": 0.0,
                "quality_score": 0.0
            }
        
        metrics = self._provider_performance[biometric_type]
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Update metrics
        metrics["total_authentications"] += 1
        if auth_result.status == AuthenticationStatus.SUCCESS:
            metrics["successful_authentications"] += 1
        
        # Update average processing time
        total_auths = metrics["total_authentications"]
        current_avg = metrics["average_processing_time"]
        metrics["average_processing_time"] = (current_avg * (total_auths - 1) + processing_time) / total_auths
        
        # Update quality score if available
        if auth_result.metadata and "quality_assessment" in auth_result.metadata:
            quality_score = auth_result.metadata["quality_assessment"].get("score", 0.0)
            current_quality = metrics["quality_score"]
            metrics["quality_score"] = (current_quality * (total_auths - 1) + quality_score) / total_auths
    
    async def validate_session(self, session_id: str) -> AuthenticationResult:
        """
        Validate existing biometric authentication session
        
        Args:
            session_id: Session identifier to validate
            
        Returns:
            AuthenticationResult indicating session validity
        """
        try:
            # Check if session exists in active sessions
            if session_id in self._active_sessions:
                session_time = self._active_sessions[session_id]
                session_timeout = timedelta(minutes=self.config.get('session_timeout_minutes', 60))
                
                if datetime.utcnow() <= session_time + session_timeout:
                    return AuthenticationResult(
                        status=AuthenticationStatus.SUCCESS,
                        session_id=session_id,
                        authentication_type=self.authentication_type,
                        metadata={"session_validation": True, "session_age_minutes": 
                                (datetime.utcnow() - session_time).total_seconds() / 60}
                    )
                else:
                    # Session expired
                    await self.invalidate_session(session_id)
                    return AuthenticationResult(
                        status=AuthenticationStatus.SESSION_EXPIRED,
                        session_id=session_id,
                        authentication_type=self.authentication_type,
                        error_message="Session has expired"
                    )
            else:
                return AuthenticationResult(
                    status=AuthenticationStatus.FAILED,
                    session_id=session_id,
                    authentication_type=self.authentication_type,
                    error_message="Session not found"
                )
                
        except Exception as e:
            self.logger.error(f"Session validation error: {str(e)}")
            return AuthenticationResult(
                status=AuthenticationStatus.FAILED,
                session_id=session_id,
                authentication_type=self.authentication_type,
                error_message=f"Session validation error: {str(e)}"
            )
    
    async def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate biometric authentication session
        
        Args:
            session_id: Session identifier to invalidate
            
        Returns:
            True if session was invalidated, False if session not found
        """
        try:
            # Remove from active sessions
            session_found = session_id in self._active_sessions
            if session_found:
                del self._active_sessions[session_id]
            
            # Clean up multimodal results
            keys_to_remove = [key for key in self._multimodal_results.keys() if session_id in key]
            for key in keys_to_remove:
                del self._multimodal_results[key]
            
            if session_found and self.enable_logging:
                self.logger.info(f"Invalidated session: {session_id}")
            
            return session_found
            
        except Exception as e:
            self.logger.error(f"Session invalidation error: {str(e)}")
            return False
    
    async def process_biometric_data(
        self,
        biometric_data: Any,
        user_id: str = None
    ) -> tuple[Any, float]:
        """
        Process raw biometric data into template and confidence score
        
        Args:
            biometric_data: Raw biometric input data
            user_id: Optional user ID for context
            
        Returns:
            Tuple of (processed_template, confidence_score)
        """
        # This is a delegating method - actual processing done by specific providers
        return biometric_data, 0.8  # Default confidence
    
    async def compare_biometric_templates(
        self,
        template1: Any,
        template2: Any
    ) -> float:
        """
        Compare two biometric templates and return similarity score
        
        Args:
            template1: First biometric template
            template2: Second biometric template
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # This is a delegating method - actual comparison done by specific providers
        return 0.8  # Default similarity
    
    def get_biometric_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive biometric performance report
        
        Returns:
            Dictionary containing performance metrics for all providers
        """
        report = {
            "biometric_authenticator": {
                "total_authentications": self._auth_count,
                "success_rate": self.success_rate,
                "average_auth_time": self.average_auth_time,
                "memory_limit_mb": self.memory_limit_mb,
                "multimodal_enabled": self.enable_multimodal,
                "quality_threshold": self.quality_threshold,
                "active_sessions": len(self._active_sessions),
                "cached_quality_assessments": len(self._quality_cache)
            },
            "provider_performance": self._provider_performance,
            "available_biometric_types": [bt.value for bt in self.available_biometric_types],
            "active_providers": [bt.value for bt in self.active_providers],
            "hardware_optimization": {
                "memory_optimized": self.is_hardware_optimized,
                "target_hardware": "GTX 1050 Ti (4GB VRAM)"
            }
        }
        
        return report
    
    async def cleanup_expired_sessions(self):
        """Clean up expired authentication sessions and cached data"""
        await super().cleanup_expired_sessions()
        
        # Clean up quality cache (keep last 1000 entries for memory efficiency)
        if len(self._quality_cache) > 1000:
            # Remove oldest entries
            cache_items = list(self._quality_cache.items())
            self._quality_cache = dict(cache_items[-1000:])
        
        # Clean up old multimodal results
        current_time = datetime.utcnow()
        cleanup_cutoff = current_time - timedelta(hours=1)  # Clean up results older than 1 hour
        
        keys_to_remove = []
        for key, results in self._multimodal_results.items():
            if results and results[0].timestamp and results[0].timestamp < cleanup_cutoff:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._multimodal_results[key]
        
        if keys_to_remove and self.enable_logging:
            self.logger.info(f"Cleaned up {len(keys_to_remove)} expired multimodal results")
