#!/usr/bin/env python3
"""
Security Infrastructure Performance Benchmark

This script benchmarks the security infrastructure performance
specifically for GTX 1050 Ti hardware constraints and provides
detailed performance analysis and optimization recommendations.

Created: 2025-01-27
Author: ImpressionCore Development Team
"""

import asyncio
import time
import sys
import json
import statistics
import psutil
import gc
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Import core utilities
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.core.utils.rich_logging import RichLogger
from src.core.utils.rich_status_animation import RichStatusAnimation


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation_name: str
    duration_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    throughput_ops_per_sec: float
    success: bool
    error_message: Optional[str] = None


class SecurityPerformanceBenchmark:
    """
    Comprehensive performance benchmark for security infrastructure.
    
    Benchmarks:
    - Component initialization performance
    - Event processing throughput
    - Memory usage patterns
    - Dashboard rendering performance
    - Concurrent operation handling
    - Resource cleanup efficiency
    """
    
    def __init__(self):
        """Initialize the performance benchmark suite."""
        self.logger = RichLogger("SecurityBenchmark")
        self.status = RichStatusAnimation()
        
        # Benchmark configuration
        self.config = {
            'gtx_1050_ti_memory_mb': 4096,  # 4GB VRAM
            'system_memory_limit_mb': 48,   # Our allocation
            'benchmark_duration_seconds': 60,
            'warmup_duration_seconds': 5,
            'cpu_cores': psutil.cpu_count(),
            'target_throughput_events_per_sec': 1000,
            'max_response_time_ms': 100,
            'stress_test_multiplier': 10
        }
        
        # Results storage
        self.benchmark_results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'configuration': self.config,
            'performance_metrics': [],
            'summary_statistics': {},
            'recommendations': [],
            'hardware_analysis': {}
        }
        
        # Performance tracking
        self.baseline_memory = 0
        self.peak_memory = 0
        self.baseline_cpu = 0
        self.peak_cpu = 0
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for benchmarking context."""
        try:
            return {
                'cpu_count': psutil.cpu_count(),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'platform': sys.platform,
                'python_version': sys.version.split()[0]
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def run_complete_benchmark(self):
        """Run the complete security infrastructure benchmark."""
        try:
            self.logger.info("🚀 Starting Security Infrastructure Performance Benchmark")
            self.status.start("Initializing benchmark environment...")
            
            # Get baseline metrics
            await self._capture_baseline_metrics()
            
            # Phase 1: Component Initialization Benchmark
            await self._benchmark_component_initialization()
            
            # Phase 2: Event Processing Throughput Benchmark
            await self._benchmark_event_processing()
            
            # Phase 3: Dashboard Performance Benchmark
            await self._benchmark_dashboard_performance()
            
            # Phase 4: Memory Management Benchmark
            await self._benchmark_memory_management()
            
            # Phase 5: Concurrent Operations Benchmark
            await self._benchmark_concurrent_operations()
            
            # Phase 6: Stress Test Benchmark
            await self._benchmark_stress_test()
            
            # Phase 7: Resource Cleanup Benchmark
            await self._benchmark_resource_cleanup()
            
            # Generate performance analysis
            await self._analyze_performance_results()
            
            # Generate recommendations
            await self._generate_optimization_recommendations()
            
            # Save benchmark report
            await self._save_benchmark_report()
            
            self.status.stop()
            self.logger.info("✅ Security Infrastructure Benchmark Complete")
            
            return True
            
        except Exception as e:
            self.status.stop()
            self.logger.error(f"❌ Benchmark failed: {e}")
            return False
    
    async def _capture_baseline_metrics(self):
        """Capture baseline system metrics."""
        self.status.update("Capturing baseline metrics...")
        
        try:
            # Wait for system to stabilize
            await asyncio.sleep(2)
            
            # Capture baseline
            process = psutil.Process()
            self.baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            self.baseline_cpu = process.cpu_percent()
            
            # System-wide metrics
            system_memory = psutil.virtual_memory()
            system_cpu = psutil.cpu_percent(interval=1)
            
            baseline_info = {
                'process_memory_mb': self.baseline_memory,
                'process_cpu_percent': self.baseline_cpu,
                'system_memory_percent': system_memory.percent,
                'system_cpu_percent': system_cpu,
                'timestamp': datetime.now().isoformat()
            }
            
            self.benchmark_results['baseline_metrics'] = baseline_info
            self.logger.info(f"📊 Baseline Memory: {self.baseline_memory:.2f} MB")
            self.logger.info(f"📊 Baseline CPU: {self.baseline_cpu:.1f}%")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to capture baseline metrics: {e}")
            raise
    
    async def _benchmark_component_initialization(self):
        """Benchmark security component initialization performance."""
        self.status.update("Benchmarking component initialization...")
        
        try:
            from security.monitoring import SecurityMonitoringOrchestrator
            from security.dashboard import SecurityDashboardOrchestrator
            
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_init_")
            
            try:
                test_config = {
                    'database_path': f"{temp_dir}/benchmark.db",
                    'temp_dir': temp_dir,
                    'memory_limit_mb': self.config['system_memory_limit_mb'],
                    'log_level': 'ERROR'  # Minimize logging overhead
                }
                
                # Benchmark monitoring initialization
                await self._benchmark_operation(
                    "monitoring_initialization",
                    self._init_monitoring_component,
                    SecurityMonitoringOrchestrator,
                    test_config
                )
                
                # Benchmark dashboard initialization
                await self._benchmark_operation(
                    "dashboard_initialization",
                    self._init_dashboard_component,
                    SecurityDashboardOrchestrator,
                    test_config
                )
                
                self.logger.info("✅ Component initialization benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Component initialization benchmark failed: {e}")
            raise
    
    async def _init_monitoring_component(self, component_class, config):
        """Initialize monitoring component for benchmarking."""
        component = component_class(config)
        await component.initialize()
        status = await component.get_status()
        await component.shutdown()
        return status.get('initialized', False)
    
    async def _init_dashboard_component(self, component_class, config):
        """Initialize dashboard component for benchmarking."""
        component = component_class(config)
        await component.initialize()
        status = await component.get_status()
        await component.shutdown()
        return status.get('initialized', False)
    
    async def _benchmark_event_processing(self):
        """Benchmark event processing throughput."""
        self.status.update("Benchmarking event processing throughput...")
        
        try:
            from security.monitoring import SecurityMonitoringOrchestrator
            
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_events_")
            
            try:
                test_config = {
                    'database_path': f"{temp_dir}/benchmark.db",
                    'temp_dir': temp_dir,
                    'memory_limit_mb': self.config['system_memory_limit_mb'],
                    'log_level': 'ERROR'
                }
                
                monitoring = SecurityMonitoringOrchestrator(test_config)
                await monitoring.initialize()
                
                # Test different event loads
                event_counts = [10, 50, 100, 500, 1000]
                
                for event_count in event_counts:
                    await self._benchmark_operation(
                        f"event_processing_{event_count}_events",
                        self._process_events_batch,
                        monitoring,
                        event_count
                    )
                
                await monitoring.shutdown()
                
                self.logger.info("✅ Event processing benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Event processing benchmark failed: {e}")
            raise
    
    async def _process_events_batch(self, monitoring, event_count):
        """Process a batch of events for benchmarking."""
        events = []
        for i in range(event_count):
            event = {
                'event_type': 'benchmark_event',
                'severity': 'info',
                'details': {
                    'iteration': i,
                    'timestamp': datetime.now().isoformat(),
                    'benchmark': True
                }
            }
            events.append(monitoring.log_security_event(**event))
        
        await asyncio.gather(*events)
        return event_count
    
    async def _benchmark_dashboard_performance(self):
        """Benchmark dashboard rendering and data retrieval performance."""
        self.status.update("Benchmarking dashboard performance...")
        
        try:
            from security.monitoring import SecurityMonitoringOrchestrator
            from security.dashboard import SecurityDashboardOrchestrator
            
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_dashboard_")
            
            try:
                test_config = {
                    'database_path': f"{temp_dir}/benchmark.db",
                    'temp_dir': temp_dir,
                    'memory_limit_mb': self.config['system_memory_limit_mb'],
                    'log_level': 'ERROR'
                }
                
                # Initialize components
                monitoring = SecurityMonitoringOrchestrator(test_config)
                dashboard = SecurityDashboardOrchestrator(test_config)
                
                await monitoring.initialize()
                await dashboard.initialize()
                
                # Generate test data
                for i in range(100):
                    await monitoring.log_security_event(
                        event_type='dashboard_benchmark',
                        severity='info',
                        details={'iteration': i}
                    )
                
                await asyncio.sleep(1)  # Allow processing
                
                # Benchmark dashboard operations
                operations = [
                    ("get_dashboard_data", dashboard.get_dashboard_data),
                    ("get_active_alerts", dashboard.get_active_alerts),
                    ("update_metrics", dashboard.update_metrics),
                    ("generate_compliance_report", dashboard.generate_compliance_report)
                ]
                
                for op_name, op_func in operations:
                    await self._benchmark_operation(
                        f"dashboard_{op_name}",
                        self._execute_dashboard_operation,
                        op_func
                    )
                
                await monitoring.shutdown()
                await dashboard.shutdown()
                
                self.logger.info("✅ Dashboard performance benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Dashboard performance benchmark failed: {e}")
            raise
    
    async def _execute_dashboard_operation(self, operation_func):
        """Execute a dashboard operation for benchmarking."""
        result = await operation_func()
        return result is not None
    
    async def _benchmark_memory_management(self):
        """Benchmark memory usage patterns and garbage collection."""
        self.status.update("Benchmarking memory management...")
        
        try:
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_memory_")
            
            try:
                # Test memory allocation patterns
                await self._benchmark_operation(
                    "memory_allocation_test",
                    self._test_memory_allocation,
                    temp_dir
                )
                
                # Test garbage collection efficiency
                await self._benchmark_operation(
                    "garbage_collection_test",
                    self._test_garbage_collection
                )
                
                self.logger.info("✅ Memory management benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Memory management benchmark failed: {e}")
            raise
    
    async def _test_memory_allocation(self, temp_dir):
        """Test memory allocation patterns."""
        from security.monitoring import SecurityMonitoringOrchestrator
        from security.dashboard import SecurityDashboardOrchestrator
        
        test_config = {
            'database_path': f"{temp_dir}/memory_test.db",
            'temp_dir': temp_dir,
            'memory_limit_mb': self.config['system_memory_limit_mb'],
            'log_level': 'ERROR'
        }
        
        # Create multiple components to test memory scaling
        components = []
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        for i in range(5):
            monitoring = SecurityMonitoringOrchestrator(test_config)
            dashboard = SecurityDashboardOrchestrator(test_config)
            
            await monitoring.initialize()
            await dashboard.initialize()
            
            components.extend([monitoring, dashboard])
            
            # Generate some activity
            for j in range(10):
                await monitoring.log_security_event(
                    event_type='memory_test',
                    severity='info',
                    details={'component': i, 'event': j}
                )
        
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        
        # Cleanup
        for component in components:
            await component.shutdown()
        
        return memory_increase <= self.config['system_memory_limit_mb']
    
    async def _test_garbage_collection(self):
        """Test garbage collection efficiency."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy objects to test GC
        data_structures = []
        for i in range(1000):
            data = {
                'large_data': [j for j in range(1000)],
                'timestamp': datetime.now(),
                'metadata': {'id': i, 'type': 'test'}
            }
            data_structures.append(data)
        
        # Force garbage collection
        del data_structures
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_recovered = initial_memory - final_memory
        
        return memory_recovered >= 0  # Should not increase significantly
    
    async def _benchmark_concurrent_operations(self):
        """Benchmark performance under concurrent operations."""
        self.status.update("Benchmarking concurrent operations...")
        
        try:
            from security.monitoring import SecurityMonitoringOrchestrator
            from security.dashboard import SecurityDashboardOrchestrator
            
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_concurrent_")
            
            try:
                test_config = {
                    'database_path': f"{temp_dir}/concurrent.db",
                    'temp_dir': temp_dir,
                    'memory_limit_mb': self.config['system_memory_limit_mb'],
                    'log_level': 'ERROR'
                }
                
                monitoring = SecurityMonitoringOrchestrator(test_config)
                dashboard = SecurityDashboardOrchestrator(test_config)
                
                await monitoring.initialize()
                await dashboard.initialize()
                
                # Test different concurrency levels
                concurrency_levels = [1, 5, 10, 20, 50]
                
                for concurrency in concurrency_levels:
                    await self._benchmark_operation(
                        f"concurrent_operations_{concurrency}_tasks",
                        self._execute_concurrent_operations,
                        monitoring,
                        dashboard,
                        concurrency
                    )
                
                await monitoring.shutdown()
                await dashboard.shutdown()
                
                self.logger.info("✅ Concurrent operations benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Concurrent operations benchmark failed: {e}")
            raise
    
    async def _execute_concurrent_operations(self, monitoring, dashboard, concurrency_level):
        """Execute concurrent operations for benchmarking."""
        tasks = []
        
        # Create mixed workload
        for i in range(concurrency_level):
            # Event logging tasks
            event_task = asyncio.create_task(
                monitoring.log_security_event(
                    event_type='concurrent_test',
                    severity='info',
                    details={'task_id': i, 'type': 'event'}
                )
            )
            tasks.append(event_task)
            
            # Dashboard query tasks (every 5th task)
            if i % 5 == 0:
                dashboard_task = asyncio.create_task(
                    dashboard.get_dashboard_data()
                )
                tasks.append(dashboard_task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Count successful operations
        successful_ops = sum(1 for result in results if not isinstance(result, Exception))
        
        return successful_ops == len(tasks)
    
    async def _benchmark_stress_test(self):
        """Run stress test to find performance limits."""
        self.status.update("Running stress test benchmark...")
        
        try:
            from security.monitoring import SecurityMonitoringOrchestrator
            
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_stress_")
            
            try:
                test_config = {
                    'database_path': f"{temp_dir}/stress.db",
                    'temp_dir': temp_dir,
                    'memory_limit_mb': self.config['system_memory_limit_mb'],
                    'log_level': 'ERROR'
                }
                
                monitoring = SecurityMonitoringOrchestrator(test_config)
                await monitoring.initialize()
                
                # Stress test with high event rate
                stress_multiplier = self.config['stress_test_multiplier']
                target_events = self.config['target_throughput_events_per_sec'] * stress_multiplier
                
                await self._benchmark_operation(
                    f"stress_test_{target_events}_events",
                    self._execute_stress_test,
                    monitoring,
                    target_events
                )
                
                await monitoring.shutdown()
                
                self.logger.info("✅ Stress test benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Stress test benchmark failed: {e}")
            raise
    
    async def _execute_stress_test(self, monitoring, event_count):
        """Execute stress test with high event load."""
        start_time = time.time()
        
        # Create event batch
        tasks = []
        for i in range(event_count):
            task = asyncio.create_task(
                monitoring.log_security_event(
                    event_type='stress_test',
                    severity='info',
                    details={
                        'iteration': i,
                        'timestamp': time.time(),
                        'stress_test': True
                    }
                )
            )
            tasks.append(task)
        
        # Execute with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks),
                timeout=30.0  # 30 second timeout
            )
            
            duration = time.time() - start_time
            actual_throughput = event_count / duration
            
            return actual_throughput
            
        except asyncio.TimeoutError:
            self.logger.warning("⚠️ Stress test timed out")
            return 0
    
    async def _benchmark_resource_cleanup(self):
        """Benchmark resource cleanup efficiency."""
        self.status.update("Benchmarking resource cleanup...")
        
        try:
            temp_dir = tempfile.mkdtemp(prefix="security_benchmark_cleanup_")
            
            try:
                await self._benchmark_operation(
                    "resource_cleanup_test",
                    self._test_resource_cleanup,
                    temp_dir
                )
                
                self.logger.info("✅ Resource cleanup benchmark complete")
                
            finally:
                if Path(temp_dir).exists():
                    shutil.rmtree(temp_dir)
                    
        except Exception as e:
            self.logger.error(f"❌ Resource cleanup benchmark failed: {e}")
            raise
    
    async def _test_resource_cleanup(self, temp_dir):
        """Test resource cleanup efficiency."""
        from security.monitoring import SecurityMonitoringOrchestrator
        from security.dashboard import SecurityDashboardOrchestrator
        
        test_config = {
            'database_path': f"{temp_dir}/cleanup.db",
            'temp_dir': temp_dir,
            'memory_limit_mb': self.config['system_memory_limit_mb'],
            'log_level': 'ERROR'
        }
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy components multiple times
        for cycle in range(5):
            monitoring = SecurityMonitoringOrchestrator(test_config)
            dashboard = SecurityDashboardOrchestrator(test_config)
            
            await monitoring.initialize()
            await dashboard.initialize()
            
            # Generate activity
            for i in range(20):
                await monitoring.log_security_event(
                    event_type='cleanup_test',
                    severity='info',
                    details={'cycle': cycle, 'event': i}
                )
            
            await monitoring.shutdown()
            await dashboard.shutdown()
            
            # Force cleanup
            del monitoring, dashboard
            gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Should not increase significantly
        return memory_increase <= 10  # Allow 10MB increase
    
    async def _benchmark_operation(self, operation_name: str, operation_func, *args):
        """Benchmark a specific operation and record metrics."""
        try:
            # Capture pre-operation metrics
            process = psutil.Process()
            pre_memory = process.memory_info().rss / 1024 / 1024
            pre_cpu = process.cpu_percent()
            
            # Execute operation
            start_time = time.time()
            result = await operation_func(*args)
            end_time = time.time()
            
            # Capture post-operation metrics
            post_memory = process.memory_info().rss / 1024 / 1024
            post_cpu = process.cpu_percent()
            
            # Calculate metrics
            duration_ms = (end_time - start_time) * 1000
            memory_usage_mb = post_memory - pre_memory
            cpu_usage_percent = max(post_cpu - pre_cpu, 0)
            
            # Calculate throughput (operations per second)
            throughput = 1000 / duration_ms if duration_ms > 0 else 0
            
            # Create metrics object
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                duration_ms=duration_ms,
                memory_usage_mb=memory_usage_mb,
                cpu_usage_percent=cpu_usage_percent,
                throughput_ops_per_sec=throughput,
                success=True
            )
            
            self.benchmark_results['performance_metrics'].append(metrics.__dict__)
            
            # Update peak tracking
            self.peak_memory = max(self.peak_memory, post_memory)
            self.peak_cpu = max(self.peak_cpu, post_cpu)
            
            self.logger.debug(f"📊 {operation_name}: {duration_ms:.2f}ms, {memory_usage_mb:.2f}MB")
            
        except Exception as e:
            # Record failed operation
            metrics = PerformanceMetrics(
                operation_name=operation_name,
                duration_ms=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                throughput_ops_per_sec=0,
                success=False,
                error_message=str(e)
            )
            
            self.benchmark_results['performance_metrics'].append(metrics.__dict__)
            self.logger.error(f"❌ {operation_name} failed: {e}")
    
    async def _analyze_performance_results(self):
        """Analyze benchmark results and generate statistics."""
        self.status.update("Analyzing performance results...")
        
        try:
            metrics = self.benchmark_results['performance_metrics']
            successful_metrics = [m for m in metrics if m['success']]
            
            if not successful_metrics:
                self.logger.warning("⚠️ No successful operations to analyze")
                return
            
            # Calculate statistics
            durations = [m['duration_ms'] for m in successful_metrics]
            memory_usages = [m['memory_usage_mb'] for m in successful_metrics]
            cpu_usages = [m['cpu_usage_percent'] for m in successful_metrics]
            throughputs = [m['throughput_ops_per_sec'] for m in successful_metrics]
            
            summary_stats = {
                'total_operations': len(metrics),
                'successful_operations': len(successful_metrics),
                'failed_operations': len(metrics) - len(successful_metrics),
                'success_rate': len(successful_metrics) / len(metrics) * 100,
                
                'duration_statistics': {
                    'mean_ms': statistics.mean(durations),
                    'median_ms': statistics.median(durations),
                    'min_ms': min(durations),
                    'max_ms': max(durations),
                    'std_dev_ms': statistics.stdev(durations) if len(durations) > 1 else 0
                },
                
                'memory_statistics': {
                    'mean_mb': statistics.mean(memory_usages),
                    'median_mb': statistics.median(memory_usages),
                    'max_mb': max(memory_usages),
                    'total_increase_mb': self.peak_memory - self.baseline_memory
                },
                
                'cpu_statistics': {
                    'mean_percent': statistics.mean(cpu_usages),
                    'median_percent': statistics.median(cpu_usages),
                    'max_percent': max(cpu_usages),
                    'peak_usage_percent': self.peak_cpu
                },
                
                'throughput_statistics': {
                    'mean_ops_per_sec': statistics.mean(throughputs),
                    'median_ops_per_sec': statistics.median(throughputs),
                    'max_ops_per_sec': max(throughputs)
                }
            }
            
            self.benchmark_results['summary_statistics'] = summary_stats
            
            # Hardware utilization analysis
            memory_utilization = (self.peak_memory - self.baseline_memory) / self.config['system_memory_limit_mb'] * 100
            
            hardware_analysis = {
                'memory_utilization_percent': memory_utilization,
                'memory_efficiency': 'excellent' if memory_utilization < 50 else 'good' if memory_utilization < 80 else 'needs_optimization',
                'cpu_efficiency': 'excellent' if self.peak_cpu < 30 else 'good' if self.peak_cpu < 60 else 'needs_optimization',
                'gtx_1050_ti_compatibility': memory_utilization < 75,  # Leave headroom for GPU operations
                'performance_rating': self._calculate_performance_rating(summary_stats, memory_utilization)
            }
            
            self.benchmark_results['hardware_analysis'] = hardware_analysis
            
            self.logger.info("✅ Performance analysis complete")
            
        except Exception as e:
            self.logger.error(f"❌ Performance analysis failed: {e}")
            raise
    
    def _calculate_performance_rating(self, stats, memory_utilization):
        """Calculate overall performance rating."""
        try:
            # Performance criteria
            avg_response_time = stats['duration_statistics']['mean_ms']
            success_rate = stats['success_rate']
            avg_throughput = stats['throughput_statistics']['mean_ops_per_sec']
            
            # Score components (0-100 each)
            response_score = max(0, 100 - (avg_response_time / self.config['max_response_time_ms']) * 100)
            success_score = success_rate
            throughput_score = min(100, (avg_throughput / self.config['target_throughput_events_per_sec']) * 100)
            memory_score = max(0, 100 - memory_utilization)
            
            # Weighted average
            overall_score = (
                response_score * 0.3 +
                success_score * 0.3 +
                throughput_score * 0.2 +
                memory_score * 0.2
            )
            
            if overall_score >= 90:
                return 'excellent'
            elif overall_score >= 75:
                return 'good'
            elif overall_score >= 60:
                return 'acceptable'
            else:
                return 'needs_improvement'
                
        except Exception:
            return 'unknown'
    
    async def _generate_optimization_recommendations(self):
        """Generate optimization recommendations based on benchmark results."""
        self.status.update("Generating optimization recommendations...")
        
        try:
            stats = self.benchmark_results.get('summary_statistics', {})
            hardware = self.benchmark_results.get('hardware_analysis', {})
            recommendations = []
            
            # Memory optimization recommendations
            memory_utilization = hardware.get('memory_utilization_percent', 0)
            if memory_utilization > 80:
                recommendations.append({
                    'category': 'memory',
                    'priority': 'high',
                    'description': 'Memory utilization is high. Consider implementing more aggressive garbage collection or reducing component memory footprint.',
                    'suggestion': 'Implement memory pooling and optimize data structures for lower memory usage.'
                })
            elif memory_utilization > 60:
                recommendations.append({
                    'category': 'memory',
                    'priority': 'medium',
                    'description': 'Memory utilization is moderate. Monitor for potential memory leaks.',
                    'suggestion': 'Review memory allocation patterns and implement periodic cleanup routines.'
                })
            
            # Performance optimization recommendations
            avg_response_time = stats.get('duration_statistics', {}).get('mean_ms', 0)
            if avg_response_time > self.config['max_response_time_ms']:
                recommendations.append({
                    'category': 'performance',
                    'priority': 'high',
                    'description': f'Average response time ({avg_response_time:.2f}ms) exceeds target ({self.config["max_response_time_ms"]}ms).',
                    'suggestion': 'Implement caching, optimize database queries, or add request batching.'
                })
            
            # Throughput optimization recommendations
            avg_throughput = stats.get('throughput_statistics', {}).get('mean_ops_per_sec', 0)
            target_throughput = self.config['target_throughput_events_per_sec']
            if avg_throughput < target_throughput * 0.5:
                recommendations.append({
                    'category': 'throughput',
                    'priority': 'high',
                    'description': f'Throughput ({avg_throughput:.2f} ops/sec) is significantly below target ({target_throughput} ops/sec).',
                    'suggestion': 'Consider implementing async processing, connection pooling, or horizontal scaling.'
                })
            
            # Success rate recommendations
            success_rate = stats.get('success_rate', 100)
            if success_rate < 95:
                recommendations.append({
                    'category': 'reliability',
                    'priority': 'high',
                    'description': f'Operation success rate ({success_rate:.1f}%) is below acceptable threshold (95%).',
                    'suggestion': 'Implement better error handling, retry mechanisms, and monitoring for failure patterns.'
                })
            
            # GTX 1050 Ti specific recommendations
            if not hardware.get('gtx_1050_ti_compatibility', True):
                recommendations.append({
                    'category': 'hardware_compatibility',
                    'priority': 'critical',
                    'description': 'Memory usage patterns may not be compatible with GTX 1050 Ti constraints.',
                    'suggestion': 'Implement GPU memory management strategies and consider model quantization or pruning.'
                })
            
            # General optimization recommendations
            if hardware.get('performance_rating') in ['needs_improvement', 'acceptable']:
                recommendations.append({
                    'category': 'general',
                    'priority': 'medium',
                    'description': 'Overall performance could be improved.',
                    'suggestion': 'Profile critical code paths, implement performance monitoring, and consider architectural optimizations.'
                })
            
            self.benchmark_results['recommendations'] = recommendations
            
            self.logger.info(f"📋 Generated {len(recommendations)} optimization recommendations")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate recommendations: {e}")
            raise
    
    async def _save_benchmark_report(self):
        """Save comprehensive benchmark report."""
        self.status.update("Saving benchmark report...")
        
        try:
            # Add final metadata
            self.benchmark_results['benchmark_completion'] = {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': time.time() - time.mktime(datetime.fromisoformat(self.benchmark_results['timestamp']).timetuple()),
                'total_operations_benchmarked': len(self.benchmark_results['performance_metrics'])
            }
            
            # Save detailed JSON report
            report_file = Path(__file__).parent.parent / "security_performance_benchmark.json"
            with open(report_file, 'w') as f:
                json.dump(self.benchmark_results, f, indent=2)
            
            # Generate summary report
            summary_file = Path(__file__).parent.parent / "security_benchmark_summary.txt"
            await self._generate_summary_report(summary_file)
            
            self.logger.info(f"📊 Benchmark report saved to: {report_file}")
            self.logger.info(f"📋 Summary report saved to: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save benchmark report: {e}")
            raise
    
    async def _generate_summary_report(self, summary_file: Path):
        """Generate human-readable summary report."""
        try:
            stats = self.benchmark_results['summary_statistics']
            hardware = self.benchmark_results['hardware_analysis']
            recommendations = self.benchmark_results['recommendations']
            
            summary_content = f"""
# Security Infrastructure Performance Benchmark Summary

**Benchmark Date:** {self.benchmark_results['timestamp']}
**System Configuration:** GTX 1050 Ti Compatible Setup

## Overall Performance Rating: {hardware.get('performance_rating', 'unknown').upper()}

## Key Metrics

### Operation Statistics
- **Total Operations:** {stats.get('total_operations', 0)}
- **Success Rate:** {stats.get('success_rate', 0):.1f}%
- **Average Response Time:** {stats.get('duration_statistics', {}).get('mean_ms', 0):.2f}ms
- **Peak Throughput:** {stats.get('throughput_statistics', {}).get('max_ops_per_sec', 0):.1f} ops/sec

### Resource Utilization
- **Memory Utilization:** {hardware.get('memory_utilization_percent', 0):.1f}%
- **Peak Memory Usage:** {stats.get('memory_statistics', {}).get('total_increase_mb', 0):.2f}MB
- **Peak CPU Usage:** {stats.get('cpu_statistics', {}).get('peak_usage_percent', 0):.1f}%

### Hardware Compatibility
- **GTX 1050 Ti Compatible:** {'✅ Yes' if hardware.get('gtx_1050_ti_compatibility') else '❌ No'}
- **Memory Efficiency:** {hardware.get('memory_efficiency', 'unknown').title()}
- **CPU Efficiency:** {hardware.get('cpu_efficiency', 'unknown').title()}

## Recommendations ({len(recommendations)} total)

"""
            
            # Add recommendations by priority
            for priority in ['critical', 'high', 'medium', 'low']:
                priority_recs = [r for r in recommendations if r.get('priority') == priority]
                if priority_recs:
                    summary_content += f"\n### {priority.title()} Priority\n"
                    for rec in priority_recs:
                        summary_content += f"- **{rec['category'].title()}:** {rec['description']}\n"
                        summary_content += f"  *Suggestion:* {rec['suggestion']}\n\n"
            
            summary_content += f"""
## Conclusion

The security infrastructure has been benchmarked against GTX 1050 Ti hardware constraints.
Performance rating: **{hardware.get('performance_rating', 'unknown').upper()}**

For detailed metrics and recommendations, see the complete benchmark report.
"""
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary_content)
                
        except Exception as e:
            self.logger.error(f"❌ Failed to generate summary report: {e}")
            raise


async def main():
    """Main benchmark entry point."""
    benchmark = SecurityPerformanceBenchmark()
    
    try:
        success = await benchmark.run_complete_benchmark()
        
        if success:
            print("\n🎯 Security Infrastructure Performance Benchmark COMPLETED")
            print("📊 Check the generated reports for detailed analysis and recommendations")
            return 0
        else:
            print("\n⚠️ Performance Benchmark FAILED")
            print("❌ Check logs for error details")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️ Benchmark interrupted by user")
        return 130
    except Exception as e:
        print(f"\n💥 Benchmark failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
