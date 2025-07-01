import jwt
import time
import requests
from github import Github, GithubIntegration
from typing import Optional
from app.core.config import settings
from app.models.code_analyzer import SmartCodeAnalyzer  # ← Fixed import
from app.security.vulnerability_scanner import AdvancedSecurityScanner


class GitHubService:
    def __init__(self):
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key

        # Initialize smart analyzer (Railway-optimized)
        print("🚀 Initializing Smart Code Analyzer...")
        self.code_analyzer = SmartCodeAnalyzer()  # ← Fixed class name
        self.security_scanner = AdvancedSecurityScanner()
        print("✅ Smart analyzer ready!")

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
            print(
                f"🔍 Starting smart analysis for PR #{pr_number} in {repo_name}")

            # Get GitHub client
            github_client = self.get_github_client(installation_id)
            repo = github_client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get PR files and changes
            files = pr.get_files()

            # Smart analysis
            analysis_result = self._analyze_pr_changes_with_smart_ai(files)

            # Post comment
            comment_body = self._generate_smart_comment(analysis_result)
            pr.create_issue_comment(comment_body)

            print(f"✅ Smart analysis complete for PR #{pr_number}")

        except Exception as e:
            print(f"❌ Error in smart analysis: {str(e)}")
            raise

    def _analyze_pr_changes_with_smart_ai(self, files) -> dict:
        """Smart analysis optimized for Railway free tier"""
        print("🧠 Running smart analysis...")

        analysis = {
            'files_changed': len(list(files)),
            'languages': set(),
            'total_additions': 0,
            'total_deletions': 0,
            'smart_insights': [],
            'security_vulnerabilities': [],
            'complexity_analysis': {},
            'suggestions': [],
            'code_quality_score': 0,
            'analysis_mode': 'heavy_ai' if self.code_analyzer.is_heavy_ai_available() else 'lightweight'
        }

        total_quality_score = 0
        analyzed_files = 0

        for file in files:
            # Detect language
            if file.filename.endswith('.py'):
                analysis['languages'].add('Python')
            elif file.filename.endswith(('.js', '.jsx')):
                analysis['languages'].add('JavaScript')
            elif file.filename.endswith(('.ts', '.tsx')):
                analysis['languages'].add('TypeScript')
            elif file.filename.endswith('.java'):
                analysis['languages'].add('Java')
            elif file.filename.endswith(('.cpp', '.c', '.h')):
                analysis['languages'].add('C/C++')

            # Count changes
            analysis['total_additions'] += file.additions
            analysis['total_deletions'] += file.deletions

            # Skip binary files and very large files
            if not file.patch or file.additions > 500:
                continue

            analyzed_files += 1

            # Smart Code Quality Analysis
            print(f"🔍 Analyzing {file.filename} with Smart Analyzer...")
            code_insights = self.code_analyzer.analyze_code_quality(
                file.patch,
                file.filename
            )

            for insight in code_insights:
                insight['filename'] = file.filename
                analysis['smart_insights'].append(insight)

            # Calculate complexity
            complexity = self.code_analyzer.calculate_complexity_score(
                file.patch)
            analysis['complexity_analysis'][file.filename] = complexity
            total_quality_score += (10 - complexity['score'])

            # Security Vulnerability Scanning
            print(f"🔒 Scanning {file.filename} for security issues...")
            vulnerabilities = self.security_scanner.scan_for_vulnerabilities(
                file.patch,
                file.filename
            )
            analysis['security_vulnerabilities'].extend(vulnerabilities)

            # General suggestions based on file changes
            if file.additions > 100:
                analysis['suggestions'].append({
                    'type': 'maintainability',
                    'message': f'Large change in {file.filename} ({file.additions} lines added). Consider breaking into smaller commits.',
                    'filename': file.filename
                })

        # Calculate overall code quality score
        if analyzed_files > 0:
            analysis['code_quality_score'] = round(
                total_quality_score / analyzed_files, 1)

        print(
            f"✅ Smart analysis complete: {len(analysis['smart_insights'])} insights, {len(analysis['security_vulnerabilities'])} security issues")

        return analysis

    def _generate_smart_comment(self, analysis: dict) -> str:
        """Generate smart AI-powered PR comment"""
        comment = "## 🤖 AI Code Review Assistant\n\n"

        # Show which mode we're using
        mode_emoji = "🧠" if analysis['analysis_mode'] == 'heavy_ai' else "🚀"
        comment += f"*{mode_emoji} Analysis mode: {analysis['analysis_mode'].replace('_', ' ').title()}*\n\n"

        # Summary with smart enhancement
        comment += f"**📊 Analysis Summary:**\n"
        comment += f"- Files analyzed: {analysis['files_changed']}\n"
        comment += f"- Languages: {', '.join(analysis['languages']) if analysis['languages'] else 'Mixed/Unknown'}\n"
        comment += f"- Changes: +{analysis['total_additions']} / -{analysis['total_deletions']} lines\n"

        if analysis['code_quality_score'] > 0:
            quality_emoji = "🟢" if analysis['code_quality_score'] >= 7 else "🟡" if analysis['code_quality_score'] >= 4 else "🔴"
            comment += f"- Code quality score: {quality_emoji} {analysis['code_quality_score']}/10\n"

        comment += "\n"

        # Security vulnerabilities (highest priority)
        if analysis['security_vulnerabilities']:
            comment += "## 🚨 Security Issues\n\n"

            high_vulns = [
                v for v in analysis['security_vulnerabilities'] if v['severity'] == 'high']
            medium_vulns = [
                v for v in analysis['security_vulnerabilities'] if v['severity'] == 'medium']
            low_vulns = [
                v for v in analysis['security_vulnerabilities'] if v['severity'] == 'low']

            if high_vulns:
                comment += "**🔴 High Severity:**\n"
                for vuln in high_vulns[:3]:  # Limit to 3 to avoid spam
                    comment += f"- **{vuln['description']}** in `{vuln['filename']}` (line {vuln.get('line', 'unknown')})\n"
                    comment += f"  💡 *{vuln['recommendation']}*\n"
                comment += "\n"

            if medium_vulns:
                comment += "**🟡 Medium Severity:**\n"
                for vuln in medium_vulns[:2]:
                    comment += f"- {vuln['description']} in `{vuln['filename']}`\n"
                comment += "\n"

        # Smart Insights
        if analysis['smart_insights']:
            comment += "## 🧠 Smart Insights\n\n"

            # Group insights by type
            complexity_insights = [
                i for i in analysis['smart_insights'] if i['type'] == 'complexity']
            pattern_insights = [
                i for i in analysis['smart_insights'] if i['type'] == 'pattern']
            maintainability_insights = [
                i for i in analysis['smart_insights'] if i['type'] == 'maintainability']
            code_smell_insights = [
                i for i in analysis['smart_insights'] if i['type'] == 'code_smell']

            if complexity_insights:
                comment += "**⚡ Complexity Analysis:**\n"
                for insight in complexity_insights[:2]:
                    comment += f"- {insight['message']} (`{insight['filename']}`)\n"
                comment += "\n"

            if pattern_insights:
                comment += "**🔍 Code Patterns:**\n"
                for insight in pattern_insights[:3]:
                    comment += f"- {insight['message']}\n"
                comment += "\n"

            if code_smell_insights:
                comment += "**👃 Code Smells:**\n"
                for insight in code_smell_insights[:2]:
                    comment += f"- {insight['message']}\n"
                comment += "\n"

        # Suggestions
        if analysis['suggestions']:
            comment += "## 💡 Suggestions\n\n"
            for suggestion in analysis['suggestions'][:3]:
                comment += f"- {suggestion['message']}\n"
            comment += "\n"

        # Positive feedback
        if (not analysis['security_vulnerabilities'] and
            not any(i['severity'] == 'warning' for i in analysis['smart_insights']) and
                analysis['code_quality_score'] >= 7):
            comment += "## ✨ Great Work!\n\n"
            comment += "Your code looks good! No major issues detected. Keep up the excellent work! 🎉\n\n"

        # Footer
        comment += "---\n"
        comment += f"*🤖 Powered by Smart Analysis Engine ({analysis['analysis_mode'].title()})*\n"
        if analysis['analysis_mode'] == 'lightweight':
            comment += "*💰 Optimized for efficient cloud deployment*"

        return comment


# Global service instance
github_service = GitHubService()
