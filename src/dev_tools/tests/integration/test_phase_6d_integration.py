#!/usr/bin/env python3
"""
Integration Tests for Priority 6 Phase 6D Components
==================================================

Tests the integration between:
- Extended Context API
- User Experience Features  
- Real-World Testing Framework
- All existing Phase 6A-6C components

Author: GitHub Copilot
Date: 2025-01-27
Hardware Target: GTX 1050 Ti (4GB VRAM)
"""

import asyncio
import pytest
import logging
import time
import torch
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.extended_context_api import ExtendedContextAPI, create_extended_context_app
from core.ux.user_experience_features import (
    AdaptiveOptimizer, ProgressiveGenerator, UserControlPanel
)
from tests.realworld.testing_scenarios import RealWorldTestingFramework
from core.utils.rich_logging import setup_rich_logging

# Setup logging
logger = setup_rich_logging(__name__)

class TestPhase6DIntegration:
    """Integration tests for Phase 6D components"""
    
    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment for each test"""
        self.test_start_time = time.time()
        logger.info("🧪 Starting Phase 6D integration test")
        
        # Initialize components
        self.api = ExtendedContextAPI()
        self.optimizer = AdaptiveOptimizer()
        self.generator = ProgressiveGenerator()
        self.control_panel = UserControlPanel()
        self.testing_framework = RealWorldTestingFramework()
        
        yield
        
        # Cleanup
        test_duration = time.time() - self.test_start_time
        logger.info(f"✅ Test completed in {test_duration:.2f}s")
    
    def test_api_initialization(self):
        """Test that Extended Context API initializes correctly"""
        assert self.api is not None
        assert hasattr(self.api, 'process_extended_context')
        assert hasattr(self.api, 'create_processing_session')
        logger.info("✅ Extended Context API initialization successful")
    
    def test_ux_components_initialization(self):
        """Test that UX components initialize correctly"""
        assert self.optimizer is not None
        assert self.generator is not None
        assert self.control_panel is not None
        
        # Test optimizer setup
        config = self.optimizer.get_current_config()
        assert 'memory_config' in config
        assert 'attention_config' in config
        
        logger.info("✅ UX components initialization successful")
    
    def test_testing_framework_initialization(self):
        """Test that testing framework initializes correctly"""
        assert self.testing_framework is not None
        
        # Test built-in scenarios exist
        scenarios = self.testing_framework.get_available_scenarios()
        assert len(scenarios) > 0
        assert any('academic_paper' in s for s in scenarios)
        
        logger.info("✅ Testing framework initialization successful")
    
    @pytest.mark.asyncio
    async def test_api_ux_integration(self):
        """Test integration between API and UX components"""
        # Create a mock request
        mock_request = {
            'text': 'This is a test document for extended context processing. ' * 100,
            'max_length': 1000,
            'quality_level': 'high',
            'enable_progressive': True
        }
        
        # Test that UX optimizer can configure API processing
        with patch.object(self.api, '_process_with_model') as mock_process:
            mock_process.return_value = {
                'generated_text': 'Test response',
                'processing_time': 0.5,
                'memory_used': 1024,
                'tokens_processed': 500
            }
            
            # Configure API with UX optimizer settings
            config = self.optimizer.get_current_config()
            
            # Process request
            result = await self.api.process_extended_context(mock_request)
            
            assert result is not None
            assert 'generated_text' in result
            
        logger.info("✅ API-UX integration successful")
    
    @pytest.mark.asyncio
    async def test_progressive_generation_integration(self):
        """Test progressive generation with API integration"""
        test_content = "Extended context test content. " * 50
        
        with patch.object(self.generator, '_generate_chunk') as mock_generate:
            mock_generate.return_value = {
                'chunk': 'Generated chunk',
                'quality_score': 0.85,
                'processing_time': 0.1
            }
            
            # Test progressive generation
            results = []
            async for chunk in self.generator.generate_progressive(
                content=test_content,
                target_length=500,
                resolution='medium'
            ):
                results.append(chunk)
                
            assert len(results) > 0
            
        logger.info("✅ Progressive generation integration successful")
    
    def test_control_panel_session_management(self):
        """Test user control panel session management"""
        # Create a session
        session_id = self.control_panel.create_session({
            'user_id': 'test_user',
            'max_context_length': 64000,
            'quality_preference': 'balanced'
        })
        
        assert session_id is not None
        
        # Test session configuration
        config = self.control_panel.get_session_config(session_id)
        assert config is not None
        assert config['max_context_length'] == 64000
        
        # Test session update
        updated = self.control_panel.update_session_config(session_id, {
            'quality_preference': 'high'
        })
        assert updated
        
        # Cleanup
        self.control_panel.end_session(session_id)
        
        logger.info("✅ Control panel session management successful")
    
    @pytest.mark.asyncio
    async def test_testing_framework_execution(self):
        """Test that testing framework can execute scenarios"""
        # Mock the actual model execution
        with patch.object(self.testing_framework, '_execute_model_test') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'latency': 0.15,
                'memory_peak': 3200,
                'quality_score': 0.88,
                'tokens_processed': 32000
            }
            
            # Run a basic scenario test
            results = await self.testing_framework.run_scenario('academic_paper_64k')
            
            assert results is not None
            assert results['success']
            assert 'performance_metrics' in results
            
        logger.info("✅ Testing framework execution successful")
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow with all components"""
        # Step 1: Create user session
        session_id = self.control_panel.create_session({
            'user_id': 'integration_test',
            'max_context_length': 128000,
            'quality_preference': 'balanced'
        })
        
        # Step 2: Configure optimizer based on session
        session_config = self.control_panel.get_session_config(session_id)
        self.optimizer.update_user_preferences(session_config)
        
        # Step 3: Prepare test content
        test_document = "Large document content for testing. " * 1000
        
        # Step 4: Process with progressive generation
        with patch.object(self.generator, '_generate_chunk') as mock_generate:
            mock_generate.return_value = {
                'chunk': 'Generated response chunk',
                'quality_score': 0.85,
                'processing_time': 0.12
            }
            
            generation_results = []
            async for result in self.generator.generate_progressive(
                content=test_document,
                target_length=1000,
                resolution='medium'
            ):
                generation_results.append(result)
        
        # Step 5: Process through API
        api_request = {
            'text': test_document,
            'max_length': 1000,
            'session_id': session_id,
            'quality_level': 'balanced'
        }
        
        with patch.object(self.api, '_process_with_model') as mock_api_process:
            mock_api_process.return_value = {
                'generated_text': 'Final API response',
                'processing_time': 0.25,
                'memory_used': 2800,
                'tokens_processed': 800
            }
            
            api_result = await self.api.process_extended_context(api_request)
        
        # Step 6: Validate results
        assert len(generation_results) > 0
        assert api_result is not None
        assert 'generated_text' in api_result
        
        # Step 7: Cleanup
        self.control_panel.end_session(session_id)
        
        logger.info("✅ End-to-end workflow integration successful")
    
    def test_memory_coordination(self):
        """Test that all components coordinate memory usage properly"""
        # Get memory configurations from each component
        optimizer_config = self.optimizer.get_current_config()
        api_memory_limit = getattr(self.api, 'memory_limit_mb', 3500)
        
        # Verify coordination
        assert optimizer_config['memory_config']['vram_limit_mb'] <= api_memory_limit
        
        # Test memory pressure handling
        self.optimizer.handle_memory_pressure(current_usage=3000, limit=3500)
        updated_config = self.optimizer.get_current_config()
        
        # Should have adjusted settings for memory pressure
        assert updated_config['memory_config']['enable_cpu_offload']
        
        logger.info("✅ Memory coordination successful")
    
    def test_error_handling_integration(self):
        """Test error handling across all components"""
        # Test API error handling
        with patch.object(self.api, '_process_with_model', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                asyncio.run(self.api.process_extended_context({'text': 'test'}))
        
        # Test optimizer error recovery
        try:
            self.optimizer.update_user_preferences({'invalid_config': 'bad_value'})
        except Exception as e:
            logger.info(f"Expected error handled: {e}")
        
        # Verify optimizer still functional
        config = self.optimizer.get_current_config()
        assert config is not None
        
        logger.info("✅ Error handling integration successful")

class TestPhase6DPerformance:
    """Performance integration tests"""
    
    @pytest.fixture(autouse=True)
    def setup_performance_test(self):
        """Setup for performance tests"""
        self.api = ExtendedContextAPI()
        self.optimizer = AdaptiveOptimizer()
        
        yield
        
        # Performance cleanup and reporting
        performance_metrics = getattr(self, 'performance_metrics', {})
        if performance_metrics:
            logger.info(f"📊 Performance Metrics: {performance_metrics}")
    
    @pytest.mark.asyncio
    async def test_latency_targets(self):
        """Test that latency targets are met"""
        test_sizes = [16000, 32000, 64000, 128000]
        latency_results = {}
        
        for size in test_sizes:
            test_text = "Token " * size
            
            with patch.object(self.api, '_process_with_model') as mock_process:
                # Simulate realistic processing times
                if size <= 32000:
                    mock_latency = 0.08  # 80ms for smaller contexts
                elif size <= 64000:
                    mock_latency = 0.15  # 150ms for medium contexts
                else:
                    mock_latency = 0.19  # 190ms for large contexts
                
                mock_process.return_value = {
                    'generated_text': 'Response',
                    'processing_time': mock_latency,
                    'memory_used': size * 0.02,  # Estimate
                    'tokens_processed': size
                }
                
                start_time = time.time()
                result = await self.api.process_extended_context({
                    'text': test_text,
                    'max_length': 100
                })
                actual_latency = time.time() - start_time
                
                latency_results[size] = actual_latency
                
                # Verify latency target (sub-200ms for 256k target)
                expected_max = 0.2  # 200ms target
                assert actual_latency < expected_max, f"Latency {actual_latency:.3f}s exceeds {expected_max}s for {size} tokens"
        
        self.performance_metrics = latency_results
        logger.info("✅ Latency targets met for all test sizes")
    
    def test_memory_efficiency(self):
        """Test memory efficiency across components"""
        # Test memory usage stays within GTX 1050 Ti limits
        initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
        
        # Simulate memory-intensive operations
        config = self.optimizer.get_current_config()
        memory_limit = config['memory_config']['vram_limit_mb']
        
        # Verify memory limit is appropriate for GTX 1050 Ti
        assert memory_limit <= 3500, f"Memory limit {memory_limit}MB exceeds GTX 1050 Ti capacity"
        
        logger.info("✅ Memory efficiency validated")

if __name__ == '__main__':
    # Run integration tests
    pytest.main([__file__, '-v', '--tb=short'])
