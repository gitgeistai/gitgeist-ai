# gitgeist/core/git_handler.py
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from gitgeist.analysis.ast_parser import GitgeistASTParser
from gitgeist.utils.exceptions import GitError
from gitgeist.utils.logger import get_logger

logger = get_logger(__name__)


class GitHandler:
    """Enhanced Git operations with semantic analysis"""

    def __init__(self):
        self.ast_parser = GitgeistASTParser()

    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"], capture_output=True, check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False

    def get_git_status(self) -> Dict:
        """Get current git status with file categorization"""
        if not self.is_git_repo():
            raise GitError("Not a git repository")

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )

            files = {
                "modified": [],
                "added": [],
                "deleted": [],
                "renamed": [],
                "staged": [],
            }

            for line in result.stdout.strip().split("\n"):
                if not line:
                    continue

                index_status = line[0]
                work_status = line[1]
                filepath = line[3:]

                # Handle staged files
                if index_status != " ":
                    files["staged"].append(filepath)

                # Handle working directory changes
                if work_status == "M":
                    files["modified"].append(filepath)
                elif work_status == "?":
                    files["added"].append(filepath)
                elif work_status == "D":
                    files["deleted"].append(filepath)
                elif "R" in line[:2]:
                    files["renamed"].append(filepath)

            return files

        except subprocess.CalledProcessError as e:
            raise GitError(f"Git status failed: {e}")

    def get_file_diff(self, filepath: str, staged: bool = False) -> Optional[str]:
        """Get text diff for a specific file"""
        try:
            cmd = ["git", "diff"]
            if staged:
                cmd.append("--staged")
            cmd.append(filepath)

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout if result.stdout.strip() else None

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get diff for {filepath}: {e}")
            return None

    def get_file_content_at_commit(
        self, filepath: str, commit: str = "HEAD"
    ) -> Optional[str]:
        """Get file content at specific commit"""
        try:
            cmd = ["git", "show", f"{commit}:{filepath}"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError:
            # File might not exist at that commit
            return None

    def get_semantic_diff(self, filepath: str, staged: bool = False) -> Optional[Dict]:
        """Get semantic diff using AST analysis"""
        language = self.ast_parser.detect_language(filepath)
        if not language:
            return None

        try:
            # Get old version (from git)
            old_content = self.get_file_content_at_commit(filepath)
            if old_content is None:
                # New file
                old_content = ""

            # Get new version (from working directory or staging area)
            if staged:
                # Get staged version
                try:
                    result = subprocess.run(
                        ["git", "show", f":{filepath}"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    new_content = result.stdout
                except subprocess.CalledProcessError:
                    return None
            else:
                # Get working directory version
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        new_content = f.read()
                except (IOError, UnicodeDecodeError) as e:
                    logger.error(f"Failed to read {filepath}: {e}")
                    return None

            # Perform semantic diff
            semantic_diff = self.ast_parser.semantic_diff(
                old_content, new_content, language
            )

            # Add file metadata
            semantic_diff.update(
                {
                    "filepath": filepath,
                    "language": language,
                    "old_lines": len(old_content.split("\n")) if old_content else 0,
                    "new_lines": len(new_content.split("\n")),
                }
            )

            return semantic_diff

        except Exception as e:
            logger.error(f"Semantic diff failed for {filepath}: {e}")
            return None

    def get_diff_stats(self) -> Dict:
        """Get detailed diff statistics"""
        try:
            result = subprocess.run(
                ["git", "diff", "--stat"], capture_output=True, text=True, check=True
            )

            lines = result.stdout.strip().split("\n")
            stats = {"files_changed": 0, "insertions": 0, "deletions": 0, "files": []}

            for line in lines:
                if not line:
                    continue

                if " file" in line and "changed" in line:
                    # Parse summary line: "X files changed, Y insertions(+), Z deletions(-)"
                    parts = line.split(",")
                    if parts:
                        stats["files_changed"] = int(parts[0].split()[0])

                    for part in parts[1:]:
                        part = part.strip()
                        if "insertion" in part:
                            stats["insertions"] = int(part.split()[0])
                        elif "deletion" in part:
                            stats["deletions"] = int(part.split()[0])
                elif "|" in line and not line.startswith(" "):
                    # Parse file-specific stats: "filename | 5 ++---"
                    parts = line.split("|")
                    if len(parts) == 2:
                        filename = parts[0].strip()
                        changes = parts[1].strip()
                        stats["files"].append({"name": filename, "changes": changes})

            return stats

        except subprocess.CalledProcessError as e:
            logger.error(f"Git diff --stat failed: {e}")
            return {"error": str(e)}

    def get_enhanced_diff_summary(self) -> Dict:
        """Get comprehensive diff summary with both text and semantic analysis"""
        try:
            files = self.get_git_status()

            summary = {
                "text_changes": {},
                "semantic_changes": {},
                "summary": {
                    "total_files": 0,
                    "code_files": 0,
                    "functions_added": 0,
                    "functions_removed": 0,
                    "functions_modified": 0,
                    "classes_added": 0,
                    "classes_removed": 0,
                    "classes_modified": 0,
                    "languages": set(),
                },
            }

            # Process all changed files
            all_files = files.get("modified", []) + files.get("added", [])
            summary["summary"]["total_files"] = len(all_files)

            for filepath in all_files:
                # Get text diff
                text_diff = self.get_file_diff(filepath)
                if text_diff:
                    lines = text_diff.split("\n")
                    additions = len([l for l in lines if l.startswith("+")])
                    deletions = len([l for l in lines if l.startswith("-")])

                    summary["text_changes"][filepath] = {
                        "diff": text_diff,
                        "lines_added": additions,
                        "lines_removed": deletions,
                    }

                # Get semantic diff if it's a code file
                semantic_diff = self.get_semantic_diff(filepath)
                if semantic_diff and "error" not in semantic_diff:
                    summary["semantic_changes"][filepath] = semantic_diff
                    summary["summary"]["code_files"] += 1

                    # Add language
                    if semantic_diff.get("language"):
                        summary["summary"]["languages"].add(semantic_diff["language"])

                    # Aggregate semantic changes
                    summary["summary"]["functions_added"] += len(
                        semantic_diff.get("functions_added", [])
                    )
                    summary["summary"]["functions_removed"] += len(
                        semantic_diff.get("functions_removed", [])
                    )
                    summary["summary"]["functions_modified"] += len(
                        semantic_diff.get("functions_modified", [])
                    )
                    summary["summary"]["classes_added"] += len(
                        semantic_diff.get("classes_added", [])
                    )
                    summary["summary"]["classes_removed"] += len(
                        semantic_diff.get("classes_removed", [])
                    )
                    summary["summary"]["classes_modified"] += len(
                        semantic_diff.get("classes_modified", [])
                    )

            # Convert set to list for JSON serialization
            summary["summary"]["languages"] = list(summary["summary"]["languages"])

            return summary

        except Exception as e:
            logger.error(f"Enhanced diff summary failed: {e}")
            return {"error": str(e)}

    def stage_files(self, files: List[str] = None) -> bool:
        """Stage files for commit"""
        try:
            if files:
                cmd = ["git", "add"] + files
            else:
                cmd = ["git", "add", "."]

            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Staged files: {files or 'all'}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to stage files: {e}")
            return False

    def create_commit(self, message: str, stage_all: bool = True) -> bool:
        """Create a git commit"""
        try:
            # Stage files if requested
            if stage_all:
                if not self.stage_files():
                    return False

            # Check if there's anything to commit
            status = self.get_git_status()
            if (
                not status.get("staged")
                and not status.get("modified")
                and not status.get("added")
            ):
                logger.warning("No changes to commit")
                return False

            # Create commit
            cmd = ["git", "commit", "-m", message]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            logger.info(f"✅ Commit created: {message}")
            logger.debug(f"Git output: {result.stdout}")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Commit failed: {e}")
            if e.stderr:
                logger.error(f"Git error: {e.stderr}")
            return False

    def get_recent_commits(self, count: int = 5) -> List[Dict]:
        """Get recent commit history"""
        try:
            cmd = [
                "git",
                "log",
                f"-{count}",
                "--pretty=format:%H|%s|%an|%ad",
                "--date=short",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 4:
                        commits.append(
                            {
                                "hash": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                                "date": parts[3],
                            }
                        )

            return commits

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get recent commits: {e}")
            return []

    def has_uncommitted_changes(self) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
            # git diff --quiet returns 0 if no changes, 1 if changes exist
            return result.returncode != 0
        except subprocess.CalledProcessError:
            return True  # Assume changes if command fails
        except:
            return False


# Usage example
if __name__ == "__main__":
    git_handler = GitHandler()

    if git_handler.is_git_repo():
        print("✅ Git repository detected")

        # Get enhanced diff summary
        summary = git_handler.get_enhanced_diff_summary()
        if "error" not in summary:
            print(f"Files changed: {summary['summary']['total_files']}")
            print(f"Code files: {summary['summary']['code_files']}")
            print(f"Functions added: {summary['summary']['functions_added']}")
            print(f"Languages: {summary['summary']['languages']}")
        else:
            print(f"Error: {summary['error']}")
    else:
        print("❌ Not a git repository")
