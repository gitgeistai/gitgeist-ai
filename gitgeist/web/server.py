# gitgeist/web/server.py
import json
from pathlib import Path
from typing import Dict, List

from gitgeist.core.config import GitgeistConfig
from gitgeist.core.workspace import WorkspaceManager
from gitgeist.memory.vector_store import GitgeistMemory
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

if FASTAPI_AVAILABLE:
    app = FastAPI(title="Gitgeist Dashboard", version="0.1.0")

    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Main dashboard page"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gitgeist Dashboard</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; }
                .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .metric { display: inline-block; margin: 10px 20px; text-align: center; }
                .metric-value { font-size: 2em; font-weight: bold; color: #2196F3; }
                .metric-label { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="/static/logo.png" alt="Gitgeist Logo" width="64" height="64" style="margin-bottom: 10px;">
                    <h1>🧠 Gitgeist Dashboard</h1>
                </div>
                
                <div class="card">
                    <h2>System Overview</h2>
                    <div id="metrics">Loading...</div>
                </div>
                
                <div class="card">
                    <h2>Repositories</h2>
                    <div id="repositories">Loading...</div>
                </div>
            </div>
            
            <script>
                async function loadDashboard() {
                    try {
                        const metrics = await fetch('/api/metrics').then(r => r.json());
                        
                        document.getElementById('metrics').innerHTML = `
                            <div class="metric">
                                <div class="metric-value">${metrics.repositories}</div>
                                <div class="metric-label">Repositories</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value">${metrics.commits}</div>
                                <div class="metric-label">Commits Stored</div>
                            </div>
                        `;
                        
                    } catch (error) {
                        console.error('Failed to load dashboard:', error);
                    }
                }
                
                loadDashboard();
            </script>
        </body>
        </html>
        """

    @app.get("/api/metrics")
    async def get_metrics() -> Dict:
        """Get system metrics"""
        try:
            workspace = WorkspaceManager()
            repositories = workspace.list_repositories()
            
            config = GitgeistConfig.load()
            memory = GitgeistMemory(config.data_dir)
            memory_stats = memory.get_memory_stats()
            
            return {
                "repositories": len(repositories),
                "commits": memory_stats.get("commits_stored", 0),
                "languages": 29
            }
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {"repositories": 0, "commits": 0, "languages": 0}

def start_server(host: str = "127.0.0.1", port: int = 8080):
    """Start the web dashboard server"""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available. Install with: pip install fastapi uvicorn")
    
    logger.info(f"Starting Gitgeist dashboard at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port)