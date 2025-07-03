import os
import re
import logging
from typing import List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

logger = logging.getLogger(__name__)


class LightweightAIAnalyzer:
    """Lightweight AI analyzer that works on Render free tier"""

    def __init__(self):
        self.use_transformers = os.getenv(
            "USE_LIGHTWEIGHT_TRANSFORMERS", "false").lower() == "true"
        self.model = None
        self.tokenizer = None

        # Always available: TF-IDF based analysis
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english'
        )

        # Code pattern database (lightweight knowledge base)
        self.code_patterns = self._load_code_patterns()

        if self.use_transformers:
            self._try_load_lightweight_model()
        else:
            print("🚀 Using TF-IDF + heuristics mode (ultra-lightweight)")

    def _try_load_lightweight_model(self):
        """Try to load a lightweight transformer model"""
        try:
            print("🤖 Loading lightweight CodeBERT...")

            # Try the smallest models first
            models_to_try = [
                "Salesforce/codet5-small",
                "microsoft/codebert-base-mlm",
                "huggingface/CodeBERTa-small-v1"
            ]

            for model_name in models_to_try:
                try:
                    from transformers import AutoTokenizer, AutoModel
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.model = AutoModel.from_pretrained(model_name)
                    print(f"✅ Loaded {model_name} successfully!")
                    break
                except Exception as e:
                    print(f"⚠️ Failed to load {model_name}: {e}")
                    continue

        except ImportError:
            print("📦 Transformers not available, using TF-IDF mode")
        except Exception as e:
            print(f"⚠️ Model loading failed: {e}, falling back to TF-IDF")

    def is_ai_available(self) -> bool:
        """Check if any AI model is available"""
        return self.model is not None or self.tfidf_vectorizer is not None

    def _load_code_patterns(self) -> Dict:
        """Load lightweight code pattern knowledge base"""
        return {
            'complexity_indicators': [
                'for.*for.*for',  # Nested loops
                'if.*if.*if.*if',  # Nested conditions
                'try.*except.*try.*except',  # Multiple exception handling
                'def.*def.*def',  # Many functions in one block
            ],
            'quality_patterns': {
                'good': [
                    r'def\s+test_\w+',  # Test functions
                    r'""".*"""',  # Docstrings
                    r'#\s*TODO:.*',  # Documented todos
                    r'logging\.',  # Proper logging
                    r'raise\s+\w+Error',  # Proper exception raising
                ],
                'bad': [
                    r'eval\s*\(',  # Dangerous eval
                    r'exec\s*\(',  # Dangerous exec
                    r'import\s+\*',  # Star imports
                    r'except\s*:',  # Bare except
                    r'print\s*\(',  # Print instead of logging
                ]
            },
            'code_smells': [
                r'def\s+\w+\([^)]{50,}\)',  # Long parameter lists
                r'class\s+\w+.*:\s*pass',  # Empty classes
                r'if\s+.*:\s*pass',  # Empty if blocks
                r'while\s+True:',  # Infinite loops
            ]
        }

    def analyze_code_intelligence(self, code: str, filename: str = "") -> List[Dict]:
        """Main AI analysis method"""
        insights = []

        # Method 1: Transformer-based analysis (if available)
        if self.model is not None:
            transformer_insights = self._analyze_with_transformers(
                code, filename)
            insights.extend(transformer_insights)

        # Method 2: TF-IDF based similarity analysis
        tfidf_insights = self._analyze_with_tfidf(code, filename)
        insights.extend(tfidf_insights)

        # Method 3: Pattern-based AI insights
        pattern_insights = self._analyze_with_patterns(code, filename)
        insights.extend(pattern_insights)

        # Method 4: Statistical analysis
        stats_insights = self._analyze_code_statistics(code, filename)
        insights.extend(stats_insights)

        return insights

    def _analyze_with_transformers(self, code: str, filename: str) -> List[Dict]:
        """Analysis using lightweight transformer model"""
        insights = []

        try:
            # Tokenize code
            inputs = self.tokenizer(
                code,
                return_tensors="pt",
                max_length=256,  # Shorter for speed
                truncation=True,
                padding=True
            )

            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)

            # Analyze embedding patterns
            embedding_norm = torch.norm(embeddings).item()

            if embedding_norm > 50:  # High complexity indicator
                insights.append({
                    'type': 'ai_complexity',
                    'severity': 'info',
                    'message': f'🧠 AI detected high semantic complexity (score: {embedding_norm:.1f})',
                    'source': 'transformer_analysis'
                })

        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")

        return insights

    def _analyze_with_tfidf(self, code: str, filename: str) -> List[Dict]:
        """TF-IDF based code analysis"""
        insights = []

        try:
            # Split code into tokens for analysis
            code_tokens = re.findall(r'\b\w+\b', code.lower())
            code_text = ' '.join(code_tokens)

            # Compare with known code patterns
            similarity_score = self._calculate_pattern_similarity(code_text)

            if similarity_score > 0.8:
                insights.append({
                    'type': 'pattern_similarity',
                    'severity': 'info',
                    'message': f'📊 Code follows common patterns (similarity: {similarity_score:.1f})',
                    'source': 'tfidf_analysis'
                })
            elif similarity_score < 0.3:
                insights.append({
                    'type': 'pattern_uniqueness',
                    'severity': 'info',
                    'message': f'🔍 Unique code patterns detected (similarity: {similarity_score:.1f})',
                    'source': 'tfidf_analysis'
                })

        except Exception as e:
            logger.error(f"TF-IDF analysis failed: {e}")

        return insights

    def _analyze_with_patterns(self, code: str, filename: str) -> List[Dict]:
        """Pattern-based AI insights"""
        insights = []

        # Good patterns
        good_patterns = 0
        for pattern in self.code_patterns['quality_patterns']['good']:
            if re.search(pattern, code, re.MULTILINE):
                good_patterns += 1

        # Bad patterns
        bad_patterns = 0
        for pattern in self.code_patterns['quality_patterns']['bad']:
            if re.search(pattern, code, re.MULTILINE):
                bad_patterns += 1

        # Calculate quality score
        total_patterns = good_patterns + bad_patterns
        if total_patterns > 0:
            quality_ratio = good_patterns / total_patterns

            if quality_ratio > 0.7:
                insights.append({
                    'type': 'quality_patterns',
                    'severity': 'info',
                    'message': f'✨ Good coding patterns detected ({good_patterns}/{total_patterns})',
                    'source': 'pattern_analysis'
                })
            elif quality_ratio < 0.3:
                insights.append({
                    'type': 'quality_patterns',
                    'severity': 'warning',
                    'message': f'⚠️ Concerning patterns detected ({bad_patterns}/{total_patterns})',
                    'source': 'pattern_analysis'
                })

        return insights

    def _analyze_code_statistics(self, code: str, filename: str) -> List[Dict]:
        """Statistical analysis of code"""
        insights = []

        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        # Calculate metrics
        avg_line_length = np.mean(
            [len(line) for line in non_empty_lines]) if non_empty_lines else 0
        complexity_indicators = sum(1 for line in non_empty_lines
                                    if any(keyword in line.lower()
                                           for keyword in ['if', 'for', 'while', 'try', 'def', 'class']))

        # Generate insights
        if avg_line_length > 80:
            insights.append({
                'type': 'line_length',
                'severity': 'info',
                'message': f'📏 Average line length is {avg_line_length:.1f} chars (consider shorter lines)',
                'source': 'statistical_analysis'
            })

        if complexity_indicators > len(non_empty_lines) * 0.3:
            insights.append({
                'type': 'keyword_density',
                'severity': 'info',
                'message': f'🔢 High keyword density detected ({complexity_indicators} keywords in {len(non_empty_lines)} lines)',
                'source': 'statistical_analysis'
            })

        return insights

    def _calculate_pattern_similarity(self, code_text: str) -> float:
        """Calculate similarity to common code patterns"""
        try:
            # Common code patterns (simplified)
            common_patterns = [
                "def function return if else for while try except",
                "import class method self return value error",
                "data process result check validate test setup",
                "file read write open close save load"
            ]

            # Fit vectorizer and calculate similarity
            all_texts = common_patterns + [code_text]
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)

            # Calculate similarity with common patterns
            code_vector = tfidf_matrix[-1]
            pattern_vectors = tfidf_matrix[:-1]

            similarities = cosine_similarity(code_vector, pattern_vectors)[0]
            return float(np.max(similarities))

        except Exception:
            return 0.5  # Default neutral similarity

    def get_code_embedding_lightweight(self, code: str) -> Optional[np.ndarray]:
        """Get lightweight code embedding"""
        if self.model is not None:
            return self._get_transformer_embedding(code)
        else:
            return self._get_tfidf_embedding(code)

    def _get_tfidf_embedding(self, code: str) -> np.ndarray:
        """Get TF-IDF based embedding"""
        code_tokens = re.findall(r'\b\w+\b', code.lower())
        code_text = ' '.join(code_tokens)

        try:
            # Create a simple embedding based on code characteristics
            features = {
                'length': len(code),
                'lines': len(code.split('\n')),
                'functions': len(re.findall(r'def\s+\w+', code)),
                'classes': len(re.findall(r'class\s+\w+', code)),
                'imports': len(re.findall(r'import\s+\w+', code)),
                'complexity': len(re.findall(r'if|for|while|try', code))
            }

            return np.array(list(features.values()), dtype=np.float32)

        except Exception:
            return np.zeros(6, dtype=np.float32)
