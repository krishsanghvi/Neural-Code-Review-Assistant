import re
import ast
import logging
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)


class SmartCodeAnalyzer:
    def __init__(self):
        """Initialize with lightweight mode for Railway free tier"""
        self.use_heavy_ai = os.getenv(
            "USE_HEAVY_AI", "false").lower() == "true"
        self.codebert_model = None

        if self.use_heavy_ai:
            try:
                print("🤖 Loading CodeBERT model...")
                from transformers import AutoTokenizer, AutoModel
                self.tokenizer = AutoTokenizer.from_pretrained(
                    "microsoft/codebert-base")
                self.model = AutoModel.from_pretrained(
                    "microsoft/codebert-base")
                print("✅ CodeBERT loaded successfully!")
            except Exception as e:
                print(
                    f"⚠️ CodeBERT unavailable, using lightweight analysis: {e}")
                self.use_heavy_ai = False
        else:
            print("🚀 Using lightweight analysis mode (Railway-optimized)")

    def is_heavy_ai_available(self) -> bool:
        return self.use_heavy_ai and self.model is not None

    def analyze_code_quality(self, code: str, filename: str = "") -> List[Dict]:
        """Smart analysis - heavy AI if available, lightweight otherwise"""
        if self.is_heavy_ai_available():
            return self._analyze_with_codebert(code, filename)
        else:
            return self._analyze_lightweight(code, filename)

    def _analyze_lightweight(self, code: str, filename: str) -> List[Dict]:
        """Lightweight analysis that works great on Railway free tier"""
        insights = []

        # Smart complexity analysis without heavy models
        complexity = self._calculate_smart_complexity(code)

        # High complexity warning
        if complexity['score'] > 7:
            insights.append({
                'type': 'complexity',
                'severity': 'warning',
                'message': f"🧮 High complexity detected (score: {complexity['score']:.1f}/10). Consider breaking down large functions.",
                'metrics': complexity
            })

        # Function length analysis
        if complexity['lines_of_code'] > 50:
            insights.append({
                'type': 'maintainability',
                'severity': 'info',
                'message': f"📏 Long code block ({complexity['lines_of_code']} lines). Consider splitting for better readability."
            })

        # Deep nesting detection
        if complexity['nesting_depth'] > 4:
            insights.append({
                'type': 'readability',
                'severity': 'warning',
                'message': f"🪆 Deep nesting detected ({complexity['nesting_depth']} levels). Consider refactoring to reduce complexity."
            })

        # Smart pattern analysis
        pattern_insights = self._analyze_smart_patterns(code, filename)
        insights.extend(pattern_insights)

        # Code smell detection
        smell_insights = self._detect_code_smells(code)
        insights.extend(smell_insights)

        return insights

    def _calculate_smart_complexity(self, code: str) -> Dict:
        """Calculate complexity without AST parsing (more robust)"""
        lines = [line.strip() for line in code.split('\n') if line.strip()]

        # Count complexity indicators
        complexity_indicators = [
            'if ', 'elif ', 'else:', 'while ', 'for ', 'try:', 'except:',
            'def ', 'class ', 'with ', 'match ', 'case '
        ]

        complexity_score = 1  # Base complexity
        nesting_depth = 0
        max_nesting = 0

        for line in lines:
            # Count indentation for nesting
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
            'method': 'lightweight_analysis'
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
            'deep_nesting': {
                'pattern': r'^\s{16,}',  # 4+ levels of indentation
                'count_threshold': 1,
                'message': "🪆 Deep nesting detected. Consider extracting methods or early returns.",
                'severity': 'warning'
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

        # Long parameter lists
        long_param_pattern = r'def\s+\w+\s*\([^)]{50,}\)'
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
            if len(line) > 10:  # Only check substantial lines
                line_counts[line] = line_counts.get(line, 0) + 1

        duplicates = [line for line, count in line_counts.items() if count > 2]
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

        return insights

    def calculate_complexity_score(self, code: str) -> Dict:
        """Public interface for complexity calculation"""
        return self._calculate_smart_complexity(code)
