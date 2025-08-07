# gitgeist/core/caching.py
import hashlib
import json
import pickle
import time
from pathlib import Path
from typing import Any, Dict, Optional

from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages caching for expensive operations"""

    def __init__(self, cache_dir: Path = None):
        self.cache_dir = cache_dir or Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = 3600  # 1 hour default TTL

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key hash"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            # Check TTL
            if time.time() - data['timestamp'] > self.ttl:
                cache_path.unlink()  # Remove expired cache
                return None
            
            logger.debug(f"Cache hit for key: {key[:20]}...")
            return data['value']
            
        except Exception as e:
            logger.error(f"Cache get failed for {key}: {e}")
            return None

    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set cached value"""
        try:
            cache_path = self._get_cache_path(key)
            
            data = {
                'value': value,
                'timestamp': time.time(),
                'ttl': ttl or self.ttl
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            logger.debug(f"Cache set for key: {key[:20]}...")
            return True
            
        except Exception as e:
            logger.error(f"Cache set failed for {key}: {e}")
            return False

    def invalidate(self, key: str) -> bool:
        """Invalidate cached value"""
        try:
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
                logger.debug(f"Cache invalidated for key: {key[:20]}...")
                return True
        except Exception as e:
            logger.error(f"Cache invalidation failed for {key}: {e}")
        return False

    def clear_expired(self) -> int:
        """Clear expired cache entries"""
        cleared = 0
        try:
            current_time = time.time()
            
            for cache_file in self.cache_dir.glob("*.cache"):
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)
                    
                    if current_time - data['timestamp'] > data.get('ttl', self.ttl):
                        cache_file.unlink()
                        cleared += 1
                        
                except Exception:
                    # Remove corrupted cache files
                    cache_file.unlink()
                    cleared += 1
            
            if cleared > 0:
                logger.info(f"Cleared {cleared} expired cache entries")
                
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
        
        return cleared

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.cache"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                'entries': len(cache_files),
                'total_size_mb': total_size / (1024 * 1024),
                'cache_dir': str(self.cache_dir)
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {'entries': 0, 'total_size_mb': 0, 'cache_dir': str(self.cache_dir)}


class FileAnalysisCache:
    """Specialized cache for file analysis results"""

    def __init__(self, cache_manager: CacheManager = None):
        self.cache = cache_manager or CacheManager()

    def get_file_analysis(self, filepath: str, file_hash: str) -> Optional[Dict]:
        """Get cached file analysis"""
        key = f"file_analysis:{filepath}:{file_hash}"
        return self.cache.get(key)

    def set_file_analysis(self, filepath: str, file_hash: str, analysis: Dict) -> bool:
        """Cache file analysis"""
        key = f"file_analysis:{filepath}:{file_hash}"
        return self.cache.set(key, analysis, ttl=7200)  # 2 hours

    def get_file_hash(self, filepath: str) -> Optional[str]:
        """Get file content hash"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {filepath}: {e}")
            return None

    def is_file_cached(self, filepath: str) -> bool:
        """Check if file analysis is cached and valid"""
        file_hash = self.get_file_hash(filepath)
        if not file_hash:
            return False
        
        cached = self.get_file_analysis(filepath, file_hash)
        return cached is not None


class CommitCache:
    """Cache for commit-related operations"""

    def __init__(self, cache_manager: CacheManager = None):
        self.cache = cache_manager or CacheManager()

    def get_commit_analysis(self, commit_hash: str) -> Optional[Dict]:
        """Get cached commit analysis"""
        key = f"commit_analysis:{commit_hash}"
        return self.cache.get(key)

    def set_commit_analysis(self, commit_hash: str, analysis: Dict) -> bool:
        """Cache commit analysis"""
        key = f"commit_analysis:{commit_hash}"
        return self.cache.set(key, analysis, ttl=86400)  # 24 hours

    def get_diff_analysis(self, diff_hash: str) -> Optional[Dict]:
        """Get cached diff analysis"""
        key = f"diff_analysis:{diff_hash}"
        return self.cache.get(key)

    def set_diff_analysis(self, diff_hash: str, analysis: Dict) -> bool:
        """Cache diff analysis"""
        key = f"diff_analysis:{diff_hash}"
        return self.cache.set(key, analysis, ttl=3600)  # 1 hour