#!/usr/bin/env python3
"""
ImpressionCore Production Inference Server Test Client
=====================================================

Simple test client for the ImpressionCore production inference server.
Tests the validated model with various inference scenarios.

Author: GitHub Copilot
Date: 2025-06-12
Version: 1.0.0
"""

import requests
import json
import time
import random
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class InferenceServerClient:
    """Test client for the production inference server."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        """Initialize the test client."""
        self.server_url = server_url
        self.session = requests.Session()
    
    def wait_for_server(self, timeout: int = 30) -> bool:
        """Wait for the server to be ready."""
        print(f"⏳ Waiting for server at {self.server_url}")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.server_url}/health")
                if response.status_code == 200:
                    print("✅ Server is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                pass
            
            time.sleep(1)
        
        print("❌ Server not ready within timeout")
        return False
    
    def test_single_inference(self) -> Dict[str, Any]:
        """Test single inference request."""
        print("\n🧪 Testing Single Inference")
        
        # Generate random 128-dimensional embedding
        test_embedding = np.random.randn(128).tolist()
        
        request_data = {
            "input_embedding": test_embedding,
            "request_id": f"test_single_{int(time.time())}"
        }
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.server_url}/inference",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Single inference successful:")
                print(f"   - Response time: {response_time:.2f}ms")
                print(f"   - Server inference time: {result.get('inference_time_ms', 'N/A')}ms")
                print(f"   - Output dimension: {len(result.get('result', []))}")
                print(f"   - Request ID: {result.get('request_id', 'N/A')}")
                return result
            else:
                print(f"❌ Single inference failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
        
        except Exception as e:
            print(f"❌ Single inference error: {str(e)}")
            return {}
    
    def test_batch_inference(self, batch_size: int = 5) -> Dict[str, Any]:
        """Test batch inference requests."""
        print(f"\n🧪 Testing Batch Inference (size: {batch_size})")
        
        # Generate multiple test embeddings
        requests_data = []
        for i in range(batch_size):
            test_embedding = np.random.randn(128).tolist()
            requests_data.append({
                "input_embedding": test_embedding,
                "request_id": f"test_batch_{i}_{int(time.time())}"
            })
        
        batch_request = {"requests": requests_data}
        
        start_time = time.time()
        
        try:
            response = self.session.post(
                f"{self.server_url}/batch_inference",
                json=batch_request,
                headers={"Content-Type": "application/json"}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Batch inference successful:")
                print(f"   - Total response time: {response_time:.2f}ms")
                print(f"   - Batch size: {len(results)}")
                
                if results:
                    avg_inference_time = np.mean([r.get('inference_time_ms', 0) for r in results])
                    print(f"   - Average inference time: {avg_inference_time:.2f}ms")
                    print(f"   - Throughput: {batch_size / (response_time / 1000):.1f} requests/second")
                
                return {"results": results, "batch_size": batch_size, "total_time_ms": response_time}
            else:
                print(f"❌ Batch inference failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {}
        
        except Exception as e:
            print(f"❌ Batch inference error: {str(e)}")
            return {}
    
    def test_performance_benchmark(self, num_requests: int = 20) -> Dict[str, Any]:
        """Run performance benchmark."""
        print(f"\n🚀 Running Performance Benchmark ({num_requests} requests)")
        
        inference_times = []
        response_times = []
        
        for i in range(num_requests):
            test_embedding = np.random.randn(128).tolist()
            request_data = {
                "input_embedding": test_embedding,
                "request_id": f"benchmark_{i}"
            }
            
            start_time = time.time()
            
            try:
                response = self.session.post(
                    f"{self.server_url}/inference",
                    json=request_data,
                    headers={"Content-Type": "application/json"}
                )
                
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response.status_code == 200:
                    result = response.json()
                    inference_times.append(result.get('inference_time_ms', 0))
                    
                    if (i + 1) % 5 == 0:
                        print(f"   Completed {i + 1}/{num_requests} requests")
                
            except Exception as e:
                print(f"   Request {i} failed: {str(e)}")
        
        # Calculate statistics
        if inference_times and response_times:
            stats = {
                'total_requests': num_requests,
                'successful_requests': len(inference_times),
                'avg_inference_time_ms': np.mean(inference_times),
                'min_inference_time_ms': np.min(inference_times),
                'max_inference_time_ms': np.max(inference_times),
                'avg_response_time_ms': np.mean(response_times),
                'throughput_requests_per_second': len(inference_times) / (sum(response_times) / 1000)
            }
            
            print(f"\n📊 Performance Benchmark Results:")
            print(f"   - Successful requests: {stats['successful_requests']}/{num_requests}")
            print(f"   - Average inference time: {stats['avg_inference_time_ms']:.2f}ms")
            print(f"   - Min/Max inference time: {stats['min_inference_time_ms']:.2f}ms / {stats['max_inference_time_ms']:.2f}ms")
            print(f"   - Average response time: {stats['avg_response_time_ms']:.2f}ms")
            print(f"   - Throughput: {stats['throughput_requests_per_second']:.1f} requests/second")
            
            return stats
        else:
            print("❌ No successful requests in benchmark")
            return {}
    
    def get_server_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        print("\n📈 Getting Server Statistics")
        
        try:
            response = self.session.get(f"{self.server_url}/stats")
            
            if response.status_code == 200:
                stats = response.json()
                print(f"✅ Server stats retrieved:")
                print(f"   - Status: {stats.get('server_status', 'unknown')}")
                print(f"   - Total requests: {stats.get('total_requests', 0)}")
                print(f"   - Average inference time: {stats.get('average_inference_time_ms', 0):.2f}ms")
                print(f"   - Current memory usage: {stats.get('current_memory_mb', 0):.2f}MB")
                print(f"   - Device: {stats.get('device', 'unknown')}")
                
                return stats
            else:
                print(f"❌ Failed to get stats: {response.status_code}")
                return {}
        
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            return {}

def main():
    """Main test function."""
    print("🧪 ImpressionCore Production Inference Server Test Client")
    print("=" * 60)
    
    # Initialize client
    client = InferenceServerClient()
    
    # Wait for server to be ready
    if not client.wait_for_server():
        print("❌ Cannot connect to server. Make sure it's running.")
        return
    
    # Run tests
    try:
        # Test single inference
        single_result = client.test_single_inference()
        
        # Test batch inference
        batch_result = client.test_batch_inference(5)
        
        # Run performance benchmark
        benchmark_result = client.test_performance_benchmark(20)
        
        # Get server statistics
        server_stats = client.get_server_stats()
        
        # Summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        
        if single_result:
            print("✅ Single inference: PASSED")
        else:
            print("❌ Single inference: FAILED")
        
        if batch_result:
            print("✅ Batch inference: PASSED")
        else:
            print("❌ Batch inference: FAILED")
        
        if benchmark_result:
            print("✅ Performance benchmark: PASSED")
            print(f"   Average inference: {benchmark_result.get('avg_inference_time_ms', 0):.2f}ms")
            print(f"   Throughput: {benchmark_result.get('throughput_requests_per_second', 0):.1f} req/s")
        else:
            print("❌ Performance benchmark: FAILED")
        
        if server_stats:
            print("✅ Server statistics: PASSED")
        else:
            print("❌ Server statistics: FAILED")
        
        print("\n🎉 Test client execution complete!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test execution error: {str(e)}")

if __name__ == "__main__":
    main()
