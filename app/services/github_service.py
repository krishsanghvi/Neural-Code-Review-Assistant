import jwt
import time
import requests
import os
from github import Github, GithubIntegration
from typing import Optional, List, Dict, Any
from app.core.config import settings
from app.models.code_analyzer import SmartCodeAnalyzer
from app.models.lightweight_ai_analyzer import LightweightAIAnalyzer
from app.security.vulnerability_scanner import AdvancedSecurityScanner


class GitHubService:
    def __init__(self):
        """Initialize GitHub service with all AI components"""
        self.app_id = settings.github_app_id
        self.private_key = settings.github_private_key

        # Debug: Print key info (remove in production)
        print(f"🔑 GitHub App ID: {self.app_id}")
        print(f"🔑 Private key loaded: {'Yes' if self.private_key else 'No'}")
        print(
            f"🔑 Key length: {len(self.private_key)} characters" if self.private_key else "🔑 No key content")

        # Initialize all AI components
        print("🚀 Initializing AI Components...")

        try:
            # Lightweight AI analyzer (primary)
            self.ai_analyzer = LightweightAIAnalyzer()
            print("✅ Lightweight AI analyzer ready")
        except Exception as e:
            print(f"⚠️ Lightweight AI failed: {e}")
            self.ai_analyzer = None

        try:
            # Smart code analyzer (fallback)
            self.code_analyzer = SmartCodeAnalyzer()
            print("✅ Smart code analyzer ready")
        except Exception as e:
            print(f"⚠️ Smart analyzer failed: {e}")
            self.code_analyzer = None

        try:
            # Security scanner (always available)
            self.security_scanner = AdvancedSecurityScanner()
            print("✅ Security scanner ready")
        except Exception as e:
            print(f"⚠️ Security scanner failed: {e}")
            self.security_scanner = None

        print("🎉 All analyzers initialized!")

    def get_installation_access_token(self, installation_id: int) -> str:
        """Get access token for a specific installation"""
        if not self.private_key:
            raise ValueError("GitHub private key not found!")

        # Create JWT for GitHub App authentication
        payload = {
            'iat': int(time.time()) - 60,  # Issued at time
            # Expiration time (10 minutes)
            'exp': int(time.time()) + (10 * 60),
            'iss': self.app_id  # Issuer
        }

        try:
            # Create JWT token
            jwt_token = jwt.encode(
                payload, self.private_key, algorithm='RS256')
            print(f"🎫 JWT token created successfully")
        except Exception as e:
            print(f"❌ Failed to create JWT token: {e}")
            raise

        # Get installation access token
        headers = {
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            print(f"✅ Installation access token obtained")
            return response.json()['token']
        except Exception as e:
            print(f"❌ Failed to get installation token: {e}")
            raise

    def get_github_client(self, installation_id: int) -> Github:
        """Get authenticated GitHub client for installation"""
        access_token = self.get_installation_access_token(installation_id)
        return Github(access_token)

    def analyze_and_comment_on_pr(self, installation_id: int, repo_name: str, pr_number: int):
        """Main function to analyze PR and post comment"""
        try:
            print(
                f"🔍 Starting comprehensive analysis for PR #{pr_number} in {repo_name}")

            # Get GitHub client
            github_client = self.get_github_client(installation_id)
            repo = github_client.get_repo(repo_name)
            pr = repo.get_pull(pr_number)

            # Get PR files and changes
            files = list(pr.get_files())
            print(f"📁 Analyzing {len(files)} changed files")

            # Comprehensive analysis
            analysis_result = self._analyze_pr_changes_comprehensive(files)

            # Generate and post comment
            comment_body = self._generate_comprehensive_comment(
                analysis_result)
            pr.create_issue_comment(comment_body)

            print(f"✅ Comprehensive analysis complete for PR #{pr_number}")

        except Exception as e:
            print(f"❌ Error in analysis: {str(e)}")
            # Post a simple error comment instead of failing silently
            try:
                github_client = self.get_github_client(installation_id)
                repo = github_client.get_repo(repo_name)
                pr = repo.get_pull(pr_number)

                error_comment = f"""## 🤖 AI Code Review Assistant

⚠️ **Analysis temporarily unavailable**

I encountered an issue while analyzing this PR. The development team has been notified.

**What you can do:**
- Check back in a few minutes
- Ensure your changes follow coding best practices
- Run local tests before pushing

---
*🔧 Error ID: {str(e)[:50]}...*"""

                pr.create_issue_comment(error_comment)
            except:
                pass  # If we can't even post an error comment, just log it

            raise

    def _analyze_pr_changes_comprehensive(self, files: List[Any]) -> Dict[str, Any]:
        """Comprehensive analysis using all available analyzers"""
        print("🧠 Running comprehensive analysis...")

        # Initialize analysis results
        analysis = {
            'files_changed': len(files),
            'languages': set(),
            'total_additions': 0,
            'total_deletions': 0,
            'ai_insights': [],
            'smart_insights': [],
            'security_vulnerabilities': [],
            'complexity_analysis': {},
            'suggestions': [],
            'code_quality_score': 0,
            'analysis_modes': [],
            'file_analysis': {},
            'overall_risk_score': 0
        }

        # Determine available analysis modes
        if self.ai_analyzer and self.ai_analyzer.is_ai_available():
            analysis['analysis_modes'].append('lightweight_ai')
        if self.code_analyzer and hasattr(self.code_analyzer, 'is_heavy_ai_available'):
            if self.code_analyzer.is_heavy_ai_available():
                analysis['analysis_modes'].append('heavy_ai')
            else:
                analysis['analysis_modes'].append('smart_heuristics')
        if self.security_scanner:
            analysis['analysis_modes'].append('security_scanning')

        total_quality_score = 0
        analyzed_files = 0
        high_risk_files = 0

        # Analyze each file
        for file in files:
            print(f"🔍 Analyzing {file.filename}...")

            # Language detection
            file_ext = file.filename.split(
                '.')[-1].lower() if '.' in file.filename else ''
            language = self._detect_language(file.filename, file_ext)
            if language:
                analysis['languages'].add(language)

            # Count changes
            analysis['total_additions'] += file.additions
            analysis['total_deletions'] += file.deletions

            # Skip binary files, very large files, or files without patches
            if not file.patch or file.additions > 1000 or self._is_binary_file(file.filename):
                print(
                    f"⏭️ Skipping {file.filename} (binary, too large, or no patch)")
                continue

            analyzed_files += 1
            file_analysis = {
                'filename': file.filename,
                'language': language,
                'additions': file.additions,
                'deletions': file.deletions,
                'insights': [],
                'vulnerabilities': [],
                'complexity': {},
                'risk_score': 0
            }

            # AI Analysis (Primary)
            if self.ai_analyzer and self.ai_analyzer.is_ai_available():
                try:
                    print(f"🤖 AI analyzing {file.filename}...")
                    ai_insights = self.ai_analyzer.analyze_code_intelligence(
                        file.patch,
                        file.filename
                    )

                    for insight in ai_insights:
                        insight['filename'] = file.filename
                        analysis['ai_insights'].append(insight)
                        file_analysis['insights'].extend(ai_insights)
                except Exception as e:
                    print(f"⚠️ AI analysis failed for {file.filename}: {e}")

            # Smart Code Analysis (Secondary)
            if self.code_analyzer:
                try:
                    print(f"🧮 Smart analyzing {file.filename}...")
                    smart_insights = self.code_analyzer.analyze_code_quality(
                        file.patch,
                        file.filename
                    )

                    for insight in smart_insights:
                        insight['filename'] = file.filename
                        analysis['smart_insights'].append(insight)
                        file_analysis['insights'].extend(smart_insights)

                    # Complexity analysis
                    complexity = self.code_analyzer.calculate_complexity_score(
                        file.patch)
                    analysis['complexity_analysis'][file.filename] = complexity
                    file_analysis['complexity'] = complexity
                    total_quality_score += (10 - complexity.get('score',
                                            complexity.get('complexity_score', 5)))

                except Exception as e:
                    print(f"⚠️ Smart analysis failed for {file.filename}: {e}")

            # Security Analysis (Critical)
            if self.security_scanner:
                try:
                    print(f"🔒 Security scanning {file.filename}...")
                    vulnerabilities = self.security_scanner.scan_for_vulnerabilities(
                        file.patch,
                        file.filename
                    )
                    analysis['security_vulnerabilities'].extend(
                        vulnerabilities)
                    file_analysis['vulnerabilities'] = vulnerabilities

                    # Count high severity issues for risk assessment
                    high_severity_count = len(
                        [v for v in vulnerabilities if v['severity'] == 'high'])
                    if high_severity_count > 0:
                        high_risk_files += 1
                        file_analysis['risk_score'] = min(
                            10, high_severity_count * 3)

                except Exception as e:
                    print(
                        f"⚠️ Security analysis failed for {file.filename}: {e}")

            # File-level suggestions
            if file.additions > 100:
                suggestion = {
                    'type': 'maintainability',
                    'severity': 'info',
                    'message': f'Large change in {file.filename} ({file.additions} lines added). Consider breaking into smaller commits.',
                    'filename': file.filename
                }
                analysis['suggestions'].append(suggestion)

            if file.deletions > 50 and file.additions < 10:
                suggestion = {
                    'type': 'cleanup',
                    'severity': 'info',
                    'message': f'Significant code removal in {file.filename}. Ensure no breaking changes.',
                    'filename': file.filename
                }
                analysis['suggestions'].append(suggestion)

            # Store file analysis
            analysis['file_analysis'][file.filename] = file_analysis

        # Calculate overall metrics
        if analyzed_files > 0:
            analysis['code_quality_score'] = round(
                total_quality_score / analyzed_files, 1)

        # Calculate overall risk score
        security_risk = len(
            [v for v in analysis['security_vulnerabilities'] if v['severity'] == 'high']) * 3
        complexity_risk = len([c for c in analysis['complexity_analysis'].values()
                              if c.get('score', c.get('complexity_score', 0)) > 7]) * 2
        size_risk = 1 if analysis['total_additions'] > 500 else 0

        analysis['overall_risk_score'] = min(
            10, security_risk + complexity_risk + size_risk)

        # Generate PR-level suggestions
        if len(analysis['languages']) > 3:
            analysis['suggestions'].append({
                'type': 'architecture',
                'severity': 'info',
                'message': f'PR touches {len(analysis["languages"])} different languages. Consider splitting by technology.',
                'filename': 'PR-level'
            })

        if analysis['files_changed'] > 20:
            analysis['suggestions'].append({
                'type': 'scope',
                'severity': 'warning',
                'message': f'Large PR with {analysis["files_changed"]} files. Consider breaking into smaller, focused PRs.',
                'filename': 'PR-level'
            })

        print(f"✅ Comprehensive analysis complete:")
        print(f"   🔍 {len(analysis['ai_insights'])} AI insights")
        print(f"   🧠 {len(analysis['smart_insights'])} smart insights")
        print(
            f"   🔒 {len(analysis['security_vulnerabilities'])} security issues")
        print(f"   📊 Quality score: {analysis['code_quality_score']}/10")
        print(f"   ⚠️ Risk score: {analysis['overall_risk_score']}/10")

        return analysis

    def _detect_language(self, filename: str, file_ext: str) -> str:
        """Detect programming language from filename"""
        language_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'jsx': 'JavaScript',
            'ts': 'TypeScript',
            'tsx': 'TypeScript',
            'java': 'Java',
            'cpp': 'C++',
            'c': 'C',
            'h': 'C/C++',
            'hpp': 'C++',
            'cs': 'C#',
            'php': 'PHP',
            'rb': 'Ruby',
            'go': 'Go',
            'rs': 'Rust',
            'kt': 'Kotlin',
            'swift': 'Swift',
            'scala': 'Scala',
            'sh': 'Shell',
            'bash': 'Shell',
            'sql': 'SQL',
            'html': 'HTML',
            'css': 'CSS',
            'scss': 'SCSS',
            'less': 'LESS',
            'vue': 'Vue',
            'svelte': 'Svelte',
            'dart': 'Dart',
            'r': 'R',
            'matlab': 'MATLAB',
            'm': 'MATLAB'
        }

        return language_map.get(file_ext, 'Unknown')

    def _is_binary_file(self, filename: str) -> bool:
        """Check if file is likely binary"""
        binary_extensions = {
            'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'ico',
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
            'zip', 'tar', 'gz', 'rar', '7z',
            'mp3', 'mp4', 'avi', 'mov', 'wav',
            'exe', 'dll', 'so', 'dylib',
            'woff', 'woff2', 'ttf', 'eot'
        }

        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        return file_ext in binary_extensions

    def _generate_comprehensive_comment(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive AI-powered PR comment"""
        comment = "## 🤖 AI Code Review Assistant\n\n"

        # Analysis mode indicator
        modes = analysis.get('analysis_modes', [])
        mode_emojis = {
            'lightweight_ai': '🧠',
            'heavy_ai': '🚀',
            'smart_heuristics': '⚡',
            'security_scanning': '🔒'
        }
        mode_display = ' + '.join([f"{mode_emojis.get(mode, '🔍')} {mode.replace('_', ' ').title()}"
                                  for mode in modes])
        comment += f"*Analysis powered by: {mode_display}*\n\n"

        # Executive Summary
        comment += f"## 📊 Executive Summary\n\n"

        # Risk assessment
        risk_score = analysis.get('overall_risk_score', 0)
        if risk_score >= 7:
            risk_emoji = "🔴"
            risk_level = "High Risk"
        elif risk_score >= 4:
            risk_emoji = "🟡"
            risk_level = "Medium Risk"
        else:
            risk_emoji = "🟢"
            risk_level = "Low Risk"

        comment += f"**{risk_emoji} Overall Risk: {risk_level} ({risk_score}/10)**\n\n"

        # Key metrics
        comment += f"**📈 Key Metrics:**\n"
        comment += f"- Files analyzed: {analysis['files_changed']}\n"
        comment += f"- Languages: {', '.join(sorted(analysis['languages'])) if analysis['languages'] else 'Mixed/Unknown'}\n"
        comment += f"- Changes: +{analysis['total_additions']} / -{analysis['total_deletions']} lines\n"

        if analysis['code_quality_score'] > 0:
            quality_emoji = "🟢" if analysis['code_quality_score'] >= 7 else "🟡" if analysis['code_quality_score'] >= 4 else "🔴"
            comment += f"- Code quality: {quality_emoji} {analysis['code_quality_score']}/10\n"

        comment += "\n"

        # Security Issues (Highest Priority)
        security_vulns = analysis.get('security_vulnerabilities', [])
        if security_vulns:
            comment += "## 🚨 Security Analysis\n\n"

            # Group by severity
            high_vulns = [v for v in security_vulns if v['severity'] == 'high']
            medium_vulns = [
                v for v in security_vulns if v['severity'] == 'medium']
            low_vulns = [v for v in security_vulns if v['severity'] == 'low']

            if high_vulns:
                comment += "### 🔴 Critical Issues (Immediate Action Required)\n"
                for vuln in high_vulns[:3]:  # Limit to avoid overwhelming
                    comment += f"- **{vuln['description']}** in `{vuln['filename']}`"
                    if 'line' in vuln:
                        comment += f" (line {vuln['line']})"
                    comment += f"\n  💡 *{vuln['recommendation']}*\n"
                if len(high_vulns) > 3:
                    comment += f"  *...and {len(high_vulns) - 3} more critical issues*\n"
                comment += "\n"

            if medium_vulns:
                comment += "### 🟡 Medium Priority Issues\n"
                for vuln in medium_vulns[:2]:
                    comment += f"- {vuln['description']} in `{vuln['filename']}`\n"
                if len(medium_vulns) > 2:
                    comment += f"  *...and {len(medium_vulns) - 2} more medium issues*\n"
                comment += "\n"

            if low_vulns and len(high_vulns) == 0:
                comment += "### 🟢 Low Priority Issues\n"
                comment += f"- {len(low_vulns)} minor security considerations found\n\n"

        # AI Insights
        ai_insights = analysis.get('ai_insights', [])
        smart_insights = analysis.get('smart_insights', [])
        all_insights = ai_insights + smart_insights

        if all_insights:
            comment += "## 🧠 Intelligence Analysis\n\n"

            # Group insights by type and severity
            complexity_insights = [i for i in all_insights if i['type'] in [
                'complexity', 'ai_complexity']]
            pattern_insights = [i for i in all_insights if i['type'] in [
                'pattern', 'pattern_similarity', 'quality_patterns']]
            maintainability_insights = [
                i for i in all_insights if i['type'] in ['maintainability', 'code_smell']]

            if complexity_insights:
                comment += "### ⚡ Complexity & Performance\n"
                for insight in complexity_insights[:3]:
                    severity_emoji = {"warning": "⚠️", "info": "ℹ️", "error": "❌"}.get(
                        insight['severity'], "🔍")
                    comment += f"- {severity_emoji} {insight['message']}"
                    if 'filename' in insight:
                        comment += f" (`{insight['filename']}`)"
                    comment += "\n"
                comment += "\n"

            if pattern_insights:
                comment += "### 🔍 Code Patterns & Quality\n"
                for insight in pattern_insights[:3]:
                    severity_emoji = {"warning": "⚠️", "info": "ℹ️", "error": "❌"}.get(
                        insight['severity'], "🔍")
                    comment += f"- {severity_emoji} {insight['message']}\n"
                comment += "\n"

            if maintainability_insights:
                comment += "### 🛠️ Maintainability\n"
                for insight in maintainability_insights[:2]:
                    severity_emoji = {"warning": "⚠️", "info": "ℹ️", "error": "❌"}.get(
                        insight['severity'], "🔍")
                    comment += f"- {severity_emoji} {insight['message']}\n"
                comment += "\n"

        # Suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            comment += "## 💡 Recommendations\n\n"
            for suggestion in suggestions[:4]:  # Limit suggestions
                severity_emoji = {"warning": "⚠️", "info": "💡",
                                  "error": "❌"}.get(suggestion['severity'], "💡")
                comment += f"- {severity_emoji} {suggestion['message']}\n"
            comment += "\n"

        # Positive feedback for good code
        if (risk_score <= 3 and
            len(security_vulns) == 0 and
                analysis.get('code_quality_score', 0) >= 7):
            comment += "## ✨ Excellent Work!\n\n"
            comment += "This PR demonstrates high-quality code with:\n"
            comment += "- ✅ No security issues detected\n"
            comment += "- ✅ Good code quality patterns\n"
            comment += "- ✅ Appropriate complexity levels\n"
            comment += "\nKeep up the outstanding work! 🎉\n\n"

        # Footer with stats
        comment += "---\n"
        total_insights = len(ai_insights) + len(smart_insights)
        comment += f"*🤖 Analysis complete: {total_insights} insights, {len(security_vulns)} security checks, {len(analysis['files_changed'])} files reviewed*\n"
        comment += f"*⚡ Powered by Neural Code Review Assistant ({', '.join(modes)})*"

        return comment


# Global service instance
github_service = GitHubService()
