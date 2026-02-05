import requests
import time
import statistics
import json
from typing import List, Dict
import matplotlib.pyplot as plt
import os

class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
    
    def measure_request_time(self, endpoint: str, method: str = "GET", data: Dict = None) -> float:
        """Measure time for a single request"""
        import time
        
        try:
            start_time = time.perf_counter()
            
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
            elif method == "POST":
                response = requests.post(f"{self.base_url}{endpoint}", json=data, timeout=10)
            elif method == "PUT":
                response = requests.put(f"{self.base_url}{endpoint}", json=data, timeout=10)
            elif method == "DELETE":
                response = requests.delete(f"{self.base_url}{endpoint}", timeout=10)
            
            end_time = time.perf_counter()
            response.raise_for_status()
            return (end_time - start_time) * 1000  # Return in milliseconds
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def run_performance_test(self, test_name: str, endpoint: str, method: str = "GET", data: Dict = None, iterations: int = 50) -> Dict:
        """Run performance test with multiple iterations"""
        print(f"\n🧪 Running {test_name}...")
        print(f"   Endpoint: {method} {endpoint}")
        print(f"   Iterations: {iterations}")
        
        times = []
        successful_requests = 0
        
        for i in range(iterations):
            time_taken = self.measure_request_time(endpoint, method, data)
            if time_taken is not None:
                times.append(time_taken)
                successful_requests += 1
            
            # Small delay between requests
            time.sleep(0.1)
            
            if (i + 1) % 10 == 0:
                print(f"   Completed {i + 1}/{iterations} requests")
        
        if not times:
            return {"error": "No successful requests"}
        
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "successful_requests": successful_requests,
            "avg_time_ms": statistics.mean(times),
            "median_time_ms": statistics.median(times),
            "min_time_ms": min(times),
            "max_time_ms": max(times),
            "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
            "all_times": times
        }
        
        self.results[test_name] = result
        return result
    
    def test_cache_behavior(self):
        """Test cache hit vs cache miss behavior"""
        print("\n🎯 Testing Cache Behavior...")
        
        # Clear cache first by making a POST request (if possible) or just measure first request
        print("\n1. First request (cache miss):")
        first_request_time = self.measure_request_time("/fruits")
        
        print("\n2. Subsequent requests (cache hits):")
        cache_hit_times = []
        for i in range(10):
            time_taken = self.measure_request_time("/fruits")
            if time_taken is not None:
                cache_hit_times.append(time_taken)
            time.sleep(0.1)
        
        if cache_hit_times:
            print(f"\n📊 Cache Analysis:")
            print(f"   First request (cache miss): {first_request_time:.2f}ms")
            print(f"   Average cache hit time: {statistics.mean(cache_hit_times):.2f}ms")
            print(f"   Performance improvement: {((first_request_time - statistics.mean(cache_hit_times)) / first_request_time * 100):.1f}%")
            
            return {
                "cache_miss_time": first_request_time,
                "avg_cache_hit_time": statistics.mean(cache_hit_times),
                "performance_improvement_percent": (first_request_time - statistics.mean(cache_hit_times)) / first_request_time * 100
            }
        
        return None
    
    def generate_report(self, save_to_file: bool = True):
        """Generate performance comparison report"""
        print("\n📋 PERFORMANCE REPORT")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            print(f"\n🧪 {test_name.upper()}")
            print(f"   Endpoint: {result['method']} {result['endpoint']}")
            print(f"   Success Rate: {result['successful_requests']}/{result['iterations']} ({result['successful_requests']/result['iterations']*100:.1f}%)")
            print(f"   Average Time: {result['avg_time_ms']:.2f}ms")
            print(f"   Median Time: {result['median_time_ms']:.2f}ms")
            print(f"   Min Time: {result['min_time_ms']:.2f}ms")
            print(f"   Max Time: {result['max_time_ms']:.2f}ms")
            print(f"   Std Dev: {result['std_dev_ms']:.2f}ms")
        
        # Save report to file
        if save_to_file:
            report_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "results": self.results
            }
            
            with open("performance_report.json", "w") as f:
                json.dump(report_data, f, indent=2)
            
            print(f"\n💾 Report saved to 'performance_report.json'")
    
    def plot_results(self):
        """Create performance comparison charts"""
        if not self.results:
            print("No results to plot!")
            return
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Plot 1: Average response times
            test_names = list(self.results.keys())
            avg_times = [self.results[name]["avg_time_ms"] for name in test_names]
            
            bars = ax1.bar(test_names, avg_times, color=['#3498db', '#e74c3c', '#2ecc71'])
            ax1.set_title('Average Response Time Comparison')
            ax1.set_ylabel('Time (ms)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar, time_val in zip(bars, avg_times):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{time_val:.1f}ms', ha='center', va='bottom')
            
            # Plot 2: Response time distribution
            for test_name in test_names:
                times = self.results[test_name]["all_times"]
                ax2.hist(times, bins=10, alpha=0.7, label=test_name)
            
            ax2.set_title('Response Time Distribution')
            ax2.set_xlabel('Time (ms)')
            ax2.set_ylabel('Frequency')
            ax2.legend()
            
            plt.tight_layout()
            plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
            print(f"📊 Performance charts saved to 'performance_comparison.png'")
            
        except ImportError:
            print("⚠️  Matplotlib not installed. Install with: pip install matplotlib")
        except Exception as e:
            print(f"⚠️  Error creating charts: {e}")

def main():
    """Main function to run performance tests"""
    tester = PerformanceTester()
    
    print("🚀 Starting FastAPI Redis Performance Test")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        ("GET Fruits - Cold Cache", "/fruits", "GET"),
        ("GET Fruits - Warm Cache", "/fruits", "GET"),
    ]
    
    # Run tests
    for test_name, endpoint, method in test_scenarios:
        tester.run_performance_test(test_name, endpoint, method, iterations=30)
        
        # Clear cache between tests (by making a POST request)
        if test_name == "GET Fruits - Cold Cache":
            try:
                # Try to add a test fruit to invalidate cache
                test_fruit = {"name": f"test_fruit_{int(time.time())}", "category": "test"}
                requests.post(f"{tester.base_url}/fruits", json=test_fruit)
                # Then delete it
                requests.delete(f"{tester.base_url}/fruits/{test_fruit['name']}")
                print("   Cache cleared for next test")
            except:
                print("   Could not clear cache, continuing...")
    
    # Test cache behavior specifically
    cache_analysis = tester.test_cache_behavior()
    
    # Generate report
    tester.generate_report()
    
    # Create charts
    tester.plot_results()
    
    print("\n✅ Performance testing completed!")
    print("\n📝 Summary:")
    print("   - Check 'performance_report.json' for detailed results")
    print("   - Check 'performance_comparison.png' for visual charts")
    
    if cache_analysis:
        print(f"\n🎯 Cache Performance:")
        print(f"   - Cache miss time: {cache_analysis['cache_miss_time']:.2f}ms")
        print(f"   - Cache hit time: {cache_analysis['avg_cache_hit_time']:.2f}ms")
        print(f"   - Performance improvement: {cache_analysis['performance_improvement_percent']:.1f}%")

if __name__ == "__main__":
    main()
