import jwt
import time
import requests
from github import Github, GithubIntegration
from typing import Optional
from app.core.config import settings


class GitHubService:
    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key

    def get_installation_access_token(self, installation_id: int) -> str:
        """Get access token for a specific installation"""
        # Create JWT for GitHub App authentication
        payload = {
            'iat': int(time.time()) - 60,  # Issued at time
            # Expiration time (10 minutes)
            'exp': int(time.time()) + (10 * 60),
            'iss': self.app_id  # Issuer
        }

        # Create JWT token
        jwt_token = jwt.encode(payload, self.private_key, algorithm='RS256')

        # Get installation access token
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        return response.json()['token']

    def get_github_client(self, installation_id: int) -> Github:
        """Get authenticated GitHub client for installation"""
        access_token = self.get_installation_access_token(installation_id)
        return Github(access_token)

    def analyze_and_comment_on_pr(self, installation_id: int, repo_name: str, pr_number: int):
        """Main function to analyze PR and post comment"""
        try:
            # Get GitHub client
            github_client = self.get_github_client(installation_id)
            repo = github_client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get PR files and changes
            files = pr.get_files()

            # Simple analysis (we'll make this smarter later)
            analysis_result = self._analyze_pr_changes(files)

            # Post comment
            comment_body = self._generate_comment(analysis_result)
            pr.create_issue_comment(comment_body)

            print(
                f"✅ Successfully commented on PR #{pr_number} in {repo_name}")

        except Exception as e:
            print(f"❌ Error processing PR: {str(e)}")
            raise

    def _analyze_pr_changes(self, files) -> dict:
        """Analyze the PR changes (basic version)"""
        analysis = {
            'files_changed': len(list(files)),
            'languages': set(),
            'total_additions': 0,
            'total_deletions': 0,
            'security_issues': [],
            'suggestions': []
        }

        for file in files:
            # Detect language
            if file.filename.endswith('.py'):
                analysis['languages'].add('Python')
            elif file.filename.endswith('.js'):
                analysis['languages'].add('JavaScript')
            elif file.filename.endswith('.java'):
                analysis['languages'].add('Java')

            # Count changes
            analysis['total_additions'] += file.additions
            analysis['total_deletions'] += file.deletions

            # Basic security checks
            if file.patch and 'password' in file.patch.lower():
                analysis['security_issues'].append(
                    '🔒 Potential hardcoded password detected')

            if file.patch and 'api_key' in file.patch.lower():
                analysis['security_issues'].append(
                    '🔑 Potential API key in code')

            # Basic suggestions
            if file.additions > 100:
                analysis['suggestions'].append(
                    f'📝 Large file change in {file.filename} - consider breaking into smaller commits')

        return analysis

    def _generate_comment(self, analysis: dict) -> str:
        """Generate the PR comment based on analysis"""
        comment = "## 🤖 AI Code Review\n\n"

        # Summary
        comment += f"**📊 Summary:**\n"
        comment += f"- Files changed: {analysis['files_changed']}\n"
        comment += f"- Languages: {', '.join(analysis['languages']) if analysis['languages'] else 'Unknown'}\n"
        comment += f"- Lines added: +{analysis['total_additions']}\n"
        comment += f"- Lines deleted: -{analysis['total_deletions']}\n\n"

        # Security issues
        if analysis['security_issues']:
            comment += "**🚨 Security Issues:**\n"
            for issue in analysis['security_issues']:
                comment += f"- {issue}\n"
            comment += "\n"

        # Suggestions
        if analysis['suggestions']:
            comment += "**💡 Suggestions:**\n"
            for suggestion in analysis['suggestions']:
                comment += f"- {suggestion}\n"
            comment += "\n"

        # Positive feedback
        if not analysis['security_issues'] and not analysis['suggestions']:
            comment += "**✅ Looks good!** No immediate issues detected.\n\n"

        comment += "---\n"
        comment += "*This review was generated by Neural Code Review Assistant*"

        return comment


# Global service instance
github_service = GitHubService()
