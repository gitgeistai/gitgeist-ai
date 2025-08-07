# gitgeist/core/performance.py
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Any, Callable, Dict, List

from gitgeist.core.caching import CacheManager, FileAnalysisCache
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class PerformanceMonitor:
    """Monitors and optimizes performance"""

    def __init__(self):
        self.metrics = {}
        self.cache = CacheManager()

    def time_function(self, func_name: str = None):
        """Decorator to time function execution"""
        def decorator(func: Callable) -> Callable:
            name = func_name or f"{func.__module__}.{func.__name__}"
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time, "success")
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time, "error")
                    raise
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time, "success")
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self._record_metric(name, execution_time, "error")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper
        return decorator

    def _record_metric(self, name: str, execution_time: float, status: str):
        """Record performance metric"""
        if name not in self.metrics:
            self.metrics[name] = {
                "calls": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "errors": 0
            }
        
        metric = self.metrics[name]
        metric["calls"] += 1
        metric["total_time"] += execution_time
        metric["avg_time"] = metric["total_time"] / metric["calls"]
        metric["min_time"] = min(metric["min_time"], execution_time)
        metric["max_time"] = max(metric["max_time"], execution_time)
        
        if status == "error":
            metric["errors"] += 1
        
        # Log slow operations
        if execution_time > 2.0:
            logger.warning(f"Slow operation: {name} took {execution_time:.2f}s")

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return self.metrics.copy()

    def get_slowest_operations(self, limit: int = 5) -> List[Dict]:
        """Get slowest operations"""
        sorted_metrics = sorted(
            self.metrics.items(),
            key=lambda x: x[1]["avg_time"],
            reverse=True
        )
        
        return [
            {"name": name, **metrics}
            for name, metrics in sorted_metrics[:limit]
        ]


class BatchProcessor:
    """Processes operations in batches for better performance"""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    async def process_files_batch(self, file_paths: List[str], 
                                 processor_func: Callable) -> List[Any]:
        """Process multiple files in parallel"""
        if not file_paths:
            return []
        
        # Split into batches
        batch_size = max(1, len(file_paths) // self.max_workers)
        batches = [
            file_paths[i:i + batch_size]
            for i in range(0, len(file_paths), batch_size)
        ]
        
        # Process batches in parallel
        loop = asyncio.get_event_loop()
        tasks = []
        
        for batch in batches:
            task = loop.run_in_executor(
                self.executor,
                self._process_batch,
                batch,
                processor_func
            )
            tasks.append(task)
        
        batch_results = await asyncio.gather(*tasks)
        
        # Flatten results
        results = []
        for batch_result in batch_results:
            results.extend(batch_result)
        
        return results

    def _process_batch(self, file_paths: List[str], processor_func: Callable) -> List[Any]:
        """Process a batch of files"""
        results = []
        for file_path in file_paths:
            try:
                result = processor_func(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({"error": str(e), "file": file_path})
        
        return results

    def __del__(self):
        """Cleanup executor"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)


class OptimizedAnalyzer:
    """Optimized file analyzer with caching and batching"""

    def __init__(self):
        self.cache = FileAnalysisCache()
        self.batch_processor = BatchProcessor()
        self.monitor = PerformanceMonitor()

    @PerformanceMonitor().time_function("analyze_file_optimized")
    def analyze_file_optimized(self, file_path: str) -> Dict[str, Any]:
        """Analyze file with caching optimization"""
        # Check cache first
        file_hash = self.cache.get_file_hash(file_path)
        if file_hash:
            cached_result = self.cache.get_file_analysis(file_path, file_hash)
            if cached_result:
                logger.debug(f"Cache hit for {file_path}")
                return cached_result
        
        # Perform analysis
        from gitgeist.analysis.ast_parser import GitgeistASTParser
        parser = GitgeistASTParser()
        result = parser.analyze_file_structure(file_path)
        
        # Cache result
        if file_hash and result and "error" not in result:
            self.cache.set_file_analysis(file_path, file_hash, result)
        
        return result

    async def analyze_files_batch(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple files with optimization"""
        # Filter out cached files
        uncached_files = []
        cached_results = {}
        
        for file_path in file_paths:
            if self.cache.is_file_cached(file_path):
                file_hash = self.cache.get_file_hash(file_path)
                if file_hash:
                    cached_result = self.cache.get_file_analysis(file_path, file_hash)
                    if cached_result:
                        cached_results[file_path] = cached_result
                        continue
            
            uncached_files.append(file_path)
        
        logger.info(f"Cache hits: {len(cached_results)}, analyzing: {len(uncached_files)}")
        
        # Process uncached files in batches
        if uncached_files:
            batch_results = await self.batch_processor.process_files_batch(
                uncached_files,
                self.analyze_file_optimized
            )
            
            # Combine results
            all_results = []
            uncached_index = 0
            
            for file_path in file_paths:
                if file_path in cached_results:
                    all_results.append(cached_results[file_path])
                else:
                    all_results.append(batch_results[uncached_index])
                    uncached_index += 1
            
            return all_results
        
        # All cached
        return [cached_results[fp] for fp in file_paths]

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        cache_stats = self.cache.cache.get_stats()
        perf_metrics = self.monitor.get_metrics()
        
        return {
            "cache": cache_stats,
            "performance": perf_metrics,
            "slowest_operations": self.monitor.get_slowest_operations()
        }