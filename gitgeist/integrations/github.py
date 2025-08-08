# gitgeist/integrations/github.py
import json
import subprocess
from typing import Dict, List, Optional

import aiohttp

from gitgeist.utils.exceptions import GitgeistError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class GitHubIntegration:
    """GitHub API integration for PR and issue management"""

    def __init__(self, token: str = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Gitgeist-AI/1.0"
        }
        
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    async def create_pull_request(self, owner: str, repo: str, 
                                title: str, body: str, head: str, base: str = "main") -> Dict:
        """Create a pull request"""
        if not self.token:
            raise GitgeistError("GitHub token required for PR creation")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        data = {
            "title": title,
            "body": body,
            "head": head,
            "base": base
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as response:
                if response.status == 201:
                    return await response.json()
                else:
                    error_data = await response.json()
                    raise GitgeistError(f"Failed to create PR: {error_data.get('message', 'Unknown error')}")

    async def get_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get repository issues"""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {"state": state}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise GitgeistError(f"Failed to get issues: {response.status}")

    def get_repo_from_remote(self) -> Optional[tuple]:
        """Extract owner/repo from git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True
            )
            
            remote_url = result.stdout.strip()
            
            # Parse GitHub URL
            if "github.com" in remote_url:
                if remote_url.startswith("git@"):
                    # SSH format: git@github.com:owner/repo.git
                    parts = remote_url.split(":")[-1].replace(".git", "").split("/")
                elif remote_url.startswith("https://"):
                    # HTTPS format: https://github.com/owner/repo.git
                    parts = remote_url.replace("https://github.com/", "").replace(".git", "").split("/")
                else:
                    return None
                
                if len(parts) >= 2:
                    return parts[0], parts[1]
            
            return None
            
        except subprocess.CalledProcessError:
            return None

    async def auto_create_pr_from_branch(self, title: str = None, body: str = None) -> Optional[Dict]:
        """Automatically create PR from current branch"""
        repo_info = self.get_repo_from_remote()
        if not repo_info:
            raise GitgeistError("Could not determine GitHub repository from remote")
        
        owner, repo = repo_info
        
        # Get current branch
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=True
            )
            current_branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            raise GitgeistError("Could not determine current branch")
        
        if current_branch in ["main", "master"]:
            raise GitgeistError("Cannot create PR from main branch")
        
        # Generate title and body if not provided
        if not title:
            title = f"feat: {current_branch.replace('/', ' - ')}"
        
        if not body:
            # Get recent commits for body
            try:
                result = subprocess.run(
                    ["git", "log", "--oneline", "main..HEAD"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                commits = result.stdout.strip().split('\n')
                body = f"## Changes\n\n" + "\n".join(f"- {commit}" for commit in commits if commit)
            except subprocess.CalledProcessError:
                body = f"Pull request from branch: {current_branch}"
        
        return await self.create_pull_request(owner, repo, title, body, current_branch)