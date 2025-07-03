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
from app.core.performance_monitor import performance_monitor


class GitHubService:
    # ... (keep existing __init__ and other methods)

    def analyze_and_comment_on_pr(self, installation_id: int, repo_name: str, pr_number: int):
        """Main function to analyze PR and post comment with performance tracking"""
        start_time = time.time()

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

            # Comprehensive analysis (this will benefit from caching)
            analysis_start = time.time()
            analysis_result = self._analyze_pr_changes_comprehensive(files)
            analysis_duration = time.time() - analysis_start

            # Record analysis performance
            performance_monitor.record_analysis_time(
                "comprehensive_analysis", analysis_duration)

            # Generate and post comment
            comment_start = time.time()
            comment_body = self._generate_comprehensive_comment(
                analysis_result)
            pr.create_issue_comment(comment_body)
            comment_duration = time.time() - comment_start

            # Record comment generation performance
            performance_monitor.record_analysis_time(
                "comment_generation", comment_duration)

            total_duration = time.time() - start_time
            performance_monitor.record_response_time(total_duration)

            print(
                f"✅ Analysis complete for PR #{pr_number} in {total_duration:.2f}s")
            print(
                f"   📊 Analysis: {analysis_duration:.2f}s, Comment: {comment_duration:.2f}s")

        except Exception as e:
            performance_monitor.record_error()
            print(f"❌ Error in analysis: {str(e)}")

            # ... (keep existing error handling)
            raise

    def _analyze_pr_changes_comprehensive(self, files: List[Any]) -> Dict[str, Any]:
        """Comprehensive analysis with detailed performance tracking"""
        print("🧠 Running comprehensive analysis...")

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
            'overall_risk_score': 0,
            'performance_metrics': {
                'cache_hits': 0,
                'cache_misses': 0,
                'total_analysis_time_ms': 0
            }
        }

        # ... (keep existing analysis mode detection)

        total_quality_score = 0
        analyzed_files = 0
        total_analysis_start = time.time()

        # Analyze each file
        for file in files:
            file_start_time = time.time()
            print(f"🔍 Analyzing {file.filename}...")

            # ... (keep existing language detection and change counting)

            if not file.patch or file.additions > 1000 or self._is_binary_file(file.filename):
                print(
                    f"⏭️ Skipping {file.filename} (binary, too large, or no patch)")
                continue

            analyzed_files += 1

            # AI Analysis (will use cache if available)
            if self.ai_analyzer and self.ai_analyzer.is_ai_available():
                try:
                    ai_start = time.time()
                    ai_result = self.ai_analyzer.analyze_code_intelligence(
                        file.patch,
                        file.filename
                    )
                    ai_duration = time.time() - ai_start

                    # Check if result was cached
                    if isinstance(ai_result, dict) and ai_result.get('cached', False):
                        analysis['performance_metrics']['cache_hits'] += 1
                        print(
                            f"  🎯 AI analysis: CACHE HIT ({ai_duration*1000:.1f}ms)")
                    else:
                        analysis['performance_metrics']['cache_misses'] += 1
                        if isinstance(ai_result, dict):
                            ai_insights = ai_result.get('insights', ai_result)
                        else:
                            ai_insights = ai_result
                        print(
                            f"  🧠 AI analysis: CACHE MISS ({ai_duration*1000:.1f}ms)")

                    # Extract insights from result
                    if isinstance(ai_result, dict) and 'insights' in ai_result:
                        ai_insights = ai_result['insights']
                    else:
                        ai_insights = ai_result if isinstance(
                            ai_result, list) else []

                    for insight in ai_insights:
                        if isinstance(insight, dict):
                            insight['filename'] = file.filename
                            analysis['ai_insights'].append(insight)

                    performance_monitor.record_analysis_time(
                        "ai_analysis", ai_duration)

                except Exception as e:
                    print(f"⚠️ AI analysis failed for {file.filename}: {e}")

            # Smart Code Analysis (will use cache if available)
            if self.code_analyzer:
                try:
                    smart_start = time.time()
                    smart_result = self.code_analyzer.analyze_code_quality(
                        file.patch,
                        file.filename
                    )
                    smart_duration = time.time() - smart_start

                    # Check if result was cached
                    if isinstance(smart_result, dict) and smart_result.get('cached', False):
                        analysis['performance_metrics']['cache_hits'] += 1
                        print(
                            f"  🎯 Smart analysis: CACHE HIT ({smart_duration*1000:.1f}ms)")
                        smart_insights = smart_result.get(
                            'insights', smart_result)
                    else:
                        analysis['performance_metrics']['cache_misses'] += 1
                        smart_insights = smart_result if isinstance(
                            smart_result, list) else []
                        print(
                            f"  ⚡ Smart analysis: CACHE MISS ({smart_duration*1000:.1f}ms)")

                    for insight in smart_insights:
                        if isinstance(insight, dict):
                            insight['filename'] = file.filename
                            analysis['smart_insights'].append(insight)

                    # Complexity analysis
                    complexity_start = time.time()
                    complexity = self.code_analyzer.calculate_complexity_score(
                        file.patch)
                    complexity_duration = time.time() - complexity_start

                    if isinstance(complexity, dict) and complexity.get('cached', False):
                        analysis['performance_metrics']['cache_hits'] += 1
                    else:
                        analysis['performance_metrics']['cache_misses'] += 1

                    analysis['complexity_analysis'][file.filename] = complexity
                    complexity_score = complexity.get(
                        'score', complexity.get('complexity_score', 5))
                    total_quality_score += (10 - complexity_score)

                    performance_monitor.record_analysis_time(
                        "smart_analysis", smart_duration)
                    performance_monitor.record_analysis_time(
                        "complexity_analysis", complexity_duration)

                except Exception as e:
                    print(f"⚠️ Smart analysis failed for {file.filename}: {e}")

            # Security Analysis (will use cache if available)
            if self.security_scanner:
                try:
                    security_start = time.time()
                    security_result = self.security_scanner.scan_for_vulnerabilities(
                        file.patch,
                        file.filename
                    )
                    security_duration = time.time() - security_start

                    # Check if result was cached
                    if isinstance(security_result, dict) and security_result.get('cached', False):
                        analysis['performance_metrics']['cache_hits'] += 1
                        print(
                            f"  🎯 Security scan: CACHE HIT ({security_duration*1000:.1f}ms)")
                        vulnerabilities = security_result.get(
                            'insights', security_result)
                    else:
                        analysis['performance_metrics']['cache_misses'] += 1
                        vulnerabilities = security_result if isinstance(
                            security_result, list) else []
                        print(
                            f"  🔒 Security scan: CACHE MISS ({security_duration*1000:.1f}ms)")

                    analysis['security_vulnerabilities'].extend(
                        vulnerabilities)

                    # Count high severity issues for risk assessment
                    high_severity_count = len(
                        [v for v in vulnerabilities if v.get('severity') == 'high'])

                    performance_monitor.record_analysis_time(
                        "security_analysis", security_duration)

                except Exception as e:
                    print(
                        f"⚠️ Security analysis failed for {file.filename}: {e}")

            file_duration = time.time() - file_start_time
            print(f"  ✅ {file.filename} analyzed in {file_duration*1000:.1f}ms")

        # Calculate overall metrics
        if analyzed_files > 0:
            analysis['code_quality_score'] = round(
                total_quality_score / analyzed_files, 1)

        # Calculate overall risk score
        security_risk = len([v for v in analysis['security_vulnerabilities'] if v.get(
            'severity') == 'high']) * 3
        complexity_risk = len([c for c in analysis['complexity_analysis'].values()
                              if c.get('score', c.get('complexity_score', 0)) > 7]) * 2
        size_risk = 1 if analysis['total_additions'] > 500 else 0

        analysis['overall_risk_score'] = min(
            10, security_risk + complexity_risk + size_risk)

        total_analysis_duration = time.time() - total_analysis_start
        analysis['performance_metrics']['total_analysis_time_ms'] = round(
            total_analysis_duration * 1000, 2)

        # Calculate cache efficiency for this analysis
        total_cache_operations = analysis['performance_metrics']['cache_hits'] + \
            analysis['performance_metrics']['cache_misses']
        cache_hit_rate = (analysis['performance_metrics']['cache_hits'] /
                          total_cache_operations * 100) if total_cache_operations > 0 else 0

        print(f"✅ Comprehensive analysis complete:")
        print(f"   🤖 {len(analysis['ai_insights'])} AI insights")
        print(f"   🧠 {len(analysis['smart_insights'])} smart insights")
        print(
            f"   🔒 {len(analysis['security_vulnerabilities'])} security issues")
        print(f"   📊 Quality score: {analysis['code_quality_score']}/10")
        print(f"   ⚠️ Risk score: {analysis['overall_risk_score']}/10")
        print(f"   🎯 Cache efficiency: {cache_hit_rate:.1f}% hit rate")
        print(f"   ⏱️ Total time: {total_analysis_duration*1000:.1f}ms")

        return analysis

    def _generate_comprehensive_comment(self, analysis: Dict[str, Any]) -> str:
        """Generate comprehensive AI-powered PR comment with performance info"""
        comment = "## 🤖 AI Code Review Assistant\n\n"

        # Analysis mode indicator
        modes = analysis.get('analysis_modes', [])
        mode_emojis = {
            'lightweight_transformers': '🧠',
            'tfidf_analysis': '📊',
            'smart_heuristics': '⚡',
            'security_scanning': '🔒'
        }
        mode_display = ' + '.join([f"{mode_emojis.get(mode, '🔍')} {mode.replace('_', ' ').title()}"
                                  for mode in modes])

        # Add performance info
        perf_metrics = analysis.get('performance_metrics', {})
        cache_hit_rate = 0
        if perf_metrics.get('cache_hits', 0) + perf_metrics.get('cache_misses', 0) > 0:
            cache_hit_rate = perf_metrics['cache_hits'] / (
                perf_metrics['cache_hits'] + perf_metrics['cache_misses']) * 100

        comment += f"*Analysis powered by: {mode_display}*\n"
        comment += f"*⚡ Performance: {perf_metrics.get('total_analysis_time_ms', 0):.0f}ms total, {cache_hit_rate:.0f}% cache hit rate*\n\n"

        # Executive Summary
        risk_score = analysis.get('overall_risk_score', 0)
        if risk_score >= 7:
            risk_emoji, risk_level = "🔴", "High Risk"
        elif risk_score >= 4:
            risk_emoji, risk_level = "🟡", "Medium Risk"
        else:
            risk_emoji, risk_level = "🟢", "Low Risk"

        comment += f"## 📊 Executive Summary\n\n"
        comment += f"**{risk_emoji} Overall Risk: {risk_level} ({risk_score}/10)**\n\n"

        # Key metrics
        comment += f"**📈 Key Metrics:**\n"
        comment += f"- Files analyzed: {analysis['files_changed']}\n"
        comment += f"- Languages: {', '.join(sorted(analysis['languages'])) if analysis['languages'] else 'Mixed'}\n"
        comment += f"- Changes: +{analysis['total_additions']} / -{analysis['total_deletions']} lines\n"

        if analysis['code_quality_score'] > 0:
            quality_emoji = "🟢" if analysis['code_quality_score'] >= 7 else "🟡" if analysis['code_quality_score'] >= 4 else "🔴"
            comment += f"- Code quality: {quality_emoji} {analysis['code_quality_score']}/10\n"

        comment += "\n"

        # ... (keep all existing comment sections for security, AI insights, etc.)

        # Security Issues (Highest Priority)
        security_vulns = analysis.get('security_vulnerabilities', [])
        if security_vulns:
            comment += "## 🚨 Security Analysis\n\n"

            high_vulns = [v for v in security_vulns if v.get(
                'severity') == 'high']
            medium_vulns = [v for v in security_vulns if v.get(
                'severity') == 'medium']

            if high_vulns:
                comment += "### 🔴 Critical Issues (Immediate Action Required)\n"
                for vuln in high_vulns[:3]:
                    comment += f"- **{vuln.get('description', 'Security issue')}** in `{vuln.get('filename', 'unknown')}`"
                    if 'line' in vuln:
                        comment += f" (line {vuln['line']})"
                    comment += f"\n  💡 *{vuln.get('recommendation', 'Review security best practices')}*\n"
                comment += "\n"

            if medium_vulns:
                comment += "### 🟡 Medium Priority Issues\n"
                for vuln in medium_vulns[:2]:
                    comment += f"- {vuln.get('description', 'Security concern')} in `{vuln.get('filename', 'unknown')}`\n"
                comment += "\n"

        # AI Insights
        ai_insights = analysis.get('ai_insights', [])
        smart_insights = analysis.get('smart_insights', [])

        if ai_insights:
            comment += "## 🧠 AI Intelligence Analysis\n\n"

            for insight in ai_insights[:3]:  # Limit to top 3
                if isinstance(insight, dict):
                    message = insight.get('message', 'AI insight detected')
                    comment += f"- {message}\n"
            comment += "\n"

        if smart_insights:
            comment += "## ⚡ Smart Analysis\n\n"

            for insight in smart_insights[:3]:  # Limit to top 3
                if isinstance(insight, dict):
                    message = insight.get('message', 'Smart insight detected')
                    comment += f"- {message}\n"
            comment += "\n"

        # Suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            comment += "## 💡 Recommendations\n\n"
            for suggestion in suggestions[:3]:
                if isinstance(suggestion, dict):
                    message = suggestion.get(
                        'message', 'Recommendation available')
                    comment += f"- 💡 {message}\n"
            comment += "\n"

        # Positive feedback for good code
        if (risk_score <= 3 and len(security_vulns) == 0 and analysis.get('code_quality_score', 0) >= 7):
            comment += "## ✨ Excellent Work!\n\n"
            comment += "This PR demonstrates high-quality code with excellent patterns and no security concerns. Keep up the outstanding work! 🎉\n\n"

        # Footer with enhanced stats
        comment += "---\n"
        total_insights = len(ai_insights) + len(smart_insights)
        analysis_time = perf_metrics.get('total_analysis_time_ms', 0)

        comment += f"*🤖 Analysis complete: {total_insights} insights, {len(security_vulns)} security checks*\n"
        comment += f"*⚡ Performance: {analysis_time:.0f}ms analysis time, {cache_hit_rate:.0f}% cache efficiency*\n"
        comment += f"*🚀 Powered by Neural Code Review Assistant*"

        return comment


# Global service instance
github_service = GitHubService()
