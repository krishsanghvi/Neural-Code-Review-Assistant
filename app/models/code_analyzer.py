import re
import ast
import logging
import os
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class SmartCodeAnalyzer:
    """Smart code analyzer optimized for resource constraints"""

    def __init__(self):
        """Initialize with lightweight mode for Railway/Render free tier"""
        self.use_heavy_ai = os.getenv(
            "USE_HEAVY_AI", "false").lower() == "true"

        if self.use_heavy_ai:
            print("⚠️ Heavy AI mode requested but not recommended for free tier")
        else:
            print("🚀 Using smart heuristics mode (resource-optimized)")

    def is_heavy_ai_available(self) -> bool:
        return False  # Always false for free tier compatibility

    def analyze_code_quality(self, code: str, filename: str = "") -> List[Dict]:
        """Smart analysis - lightweight but intelligent"""
        insights = []

        try:
            # Smart complexity analysis
            complexity = self._calculate_smart_complexity(code)

            # High complexity warning
            if complexity['score'] > 7:
                insights.append({
                    'type': 'complexity',
                    'severity': 'warning',
                    'message': f'🧮 High complexity detected (score: {complexity["score"]:.1f}/10). Consider breaking down large functions.',
                    'metrics': complexity
                })

            # Function length analysis
            if complexity['lines_of_code'] > 50:
                insights.append({
                    'type': 'maintainability',
                    'severity': 'info',
                    'message': f'📏 Long code block ({complexity["lines_of_code"]} lines). Consider splitting for better readability.'
                })

            # Deep nesting detection
            if complexity['nesting_depth'] > 4:
                insights.append({
                    'type': 'readability',
                    'severity': 'warning',
                    'message': f'🪆 Deep nesting detected ({complexity["nesting_depth"]} levels). Consider refactoring to reduce complexity.'
                })

            # Smart pattern analysis
            pattern_insights = self._analyze_smart_patterns(code, filename)
            insights.extend(pattern_insights)

            # Code smell detection
            smell_insights = self._detect_code_smells(code)
            insights.extend(smell_insights)

        except Exception as e:
            logger.error(f"Smart analysis failed: {e}")
            insights.append({
                'type': 'analysis_error',
                'severity': 'info',
                'message': '⚠️ Some analysis features temporarily unavailable'
            })

        return insights

    def _calculate_smart_complexity(self, code: str) -> Dict:
        """Calculate complexity without heavy dependencies"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        # Count complexity indicators
        complexity_indicators = [
            'if ', 'elif ', 'else:', 'while ', 'for ', 'try:', 'except:',
            'def ', 'class ', 'with ', 'match ', 'case ', 'lambda'
        ]

        complexity_score = 1  # Base complexity
        nesting_depth = 0
        max_nesting = 0

        for line in lines:
            # Count indentation for nesting (assuming 4 spaces)
            indent_level = (len(line) - len(line.lstrip())) // 4
            nesting_depth = max(nesting_depth, indent_level)
            max_nesting = max(max_nesting, indent_level)

            # Count complexity keywords
            for indicator in complexity_indicators:
                if indicator in line.lower():
                    complexity_score += 1

        # Adjust score based on length and nesting
        length_penalty = len(lines) / 20
        nesting_penalty = max_nesting * 0.5
        final_score = min(10, complexity_score +
                          length_penalty + nesting_penalty)

        return {
            'score': round(final_score, 1),
            'lines_of_code': len(lines),
            'nesting_depth': max_nesting,
            'complexity_indicators': complexity_score,
            'method': 'smart_heuristics'
        }

    def _analyze_smart_patterns(self, code: str, filename: str) -> List[Dict]:
        """Smart pattern analysis without heavy models"""
        insights = []

        # Enhanced pattern detection
        smart_patterns = {
            'logging_vs_print': {
                'pattern': r'print\s*\(',
                'count_threshold': 1,
                'message': "🖨️ Print statements detected. Consider using logging for production code.",
                'severity': 'info'
            },
            'exception_handling': {
                'pattern': r'except\s*:(?!\s*\n\s*raise)',
                'count_threshold': 1,
                'message': "🚫 Broad exception handling detected. Consider catching specific exceptions.",
                'severity': 'warning'
            },
            'todo_fixme': {
                'pattern': r'#\s*(TODO|FIXME|HACK|XXX)',
                'count_threshold': 1,
                'message': "📝 TODO/FIXME comments found. Consider addressing before merging.",
                'severity': 'info'
            },
            'magic_numbers': {
                'pattern': r'\b(?!0|1|2|10|100|1000)\d{2,}\b',
                'count_threshold': 3,
                'message': "🔢 Magic numbers detected. Consider using named constants.",
                'severity': 'info'
            },
            'long_lines': {
                'pattern': r'.{120,}',
                'count_threshold': 2,
                'message': "📏 Long lines detected (>120 chars). Consider breaking for readability.",
                'severity': 'info'
            },
            'deep_nesting_pattern': {
                'pattern': r'^\s{16,}',  # 4+ levels of indentation
                'count_threshold': 1,
                'message': "🪆 Deep nesting detected. Consider extracting methods or early returns.",
                'severity': 'warning'
            },
            'good_practices': {
                'pattern': r'(with\s+open|logging\.|@\w+|def\s+test_)',
                'count_threshold': 1,
                'message': "✨ Good coding practices detected (context managers, logging, decorators, tests).",
                'severity': 'info'
            }
        }

        for pattern_name, pattern_info in smart_patterns.items():
            matches = re.findall(pattern_info['pattern'], code, re.MULTILINE)
            if len(matches) >= pattern_info['count_threshold']:
                insights.append({
                    'type': 'pattern',
                    'severity': pattern_info['severity'],
                    'message': pattern_info['message'],
                    'count': len(matches),
                    'pattern': pattern_name
                })

        return insights

    def _detect_code_smells(self, code: str) -> List[Dict]:
        """Detect common code smells"""
        insights = []

        try:
            # Long parameter lists
            long_param_pattern = r'def\s+\w+\s*\([^)]{80,}\)'
            if re.search(long_param_pattern, code):
                insights.append({
                    'type': 'code_smell',
                    'severity': 'info',
                    'message': "📋 Long parameter list detected. Consider using objects or reducing parameters."
                })

            # Duplicate code patterns
            lines = [line.strip() for line in code.split(
                '\n') if line.strip() and not line.strip().startswith('#')]
            line_counts = {}
            for line in lines:
                if len(line) > 15:  # Only check substantial lines
                    line_counts[line] = line_counts.get(line, 0) + 1

            duplicates = [line for line,
                          count in line_counts.items() if count > 2]
            if duplicates:
                insights.append({
                    'type': 'code_smell',
                    'severity': 'info',
                    'message': f"🔄 Duplicate code detected ({len(duplicates)} patterns). Consider refactoring common logic."
                })

            # Very large functions (estimate)
            function_pattern = r'def\s+(\w+)'
            functions = re.findall(function_pattern, code)
            if len(functions) == 1 and len(code.split('\n')) > 100:
                insights.append({
                    'type': 'code_smell',
                    'severity': 'warning',
                    'message': "🏗️ Very large function detected. Consider breaking into smaller, focused functions."
                })

            # Empty catch blocks
            empty_except_pattern = r'except[^:]*:\s*pass'
            if re.search(empty_except_pattern, code):
                insights.append({
                    'type': 'code_smell',
                    'severity': 'warning',
                    'message': "🕳️ Empty exception handling detected. Consider proper error handling."
                })

        except Exception as e:
            logger.error(f"Code smell detection failed: {e}")

        return insights

    def calculate_complexity_score(self, code: str) -> Dict:
        """Public interface for complexity calculation"""
        return self._calculate_smart_complexity(code)
