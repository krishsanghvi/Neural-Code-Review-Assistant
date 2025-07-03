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
        try:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),
                stop_words='english'
            )
            print("✅ TF-IDF vectorizer initialized")
        except Exception as e:
            print(f"⚠️ TF-IDF initialization failed: {e}")
            self.tfidf_vectorizer = None

        # Code pattern database (lightweight knowledge base)
        self.code_patterns = self._load_code_patterns()

        if self.use_transformers:
            self._try_load_lightweight_model()
        else:
            print("🚀 Using TF-IDF + heuristics mode (ultra-lightweight)")

    def _try_load_lightweight_model(self):
        """Try to load a lightweight transformer model"""
        try:
            print("🤖 Attempting to load lightweight transformer model...")

            # Try the smallest models first (in order of preference)
            models_to_try = [
                ("microsoft/codebert-base-mlm", "CodeBERT MLM (smallest)"),
                ("Salesforce/codet5-small", "CodeT5 Small"),
                ("huggingface/CodeBERTa-small-v1", "CodeBERTa Small")
            ]

            for model_name, description in models_to_try:
                try:
                    print(f"  Trying {description}...")

                    # Import here to avoid errors if transformers not available
                    from transformers import AutoTokenizer, AutoModel
                    import torch

                    # Load model
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    self.model = AutoModel.from_pretrained(model_name)
                    self.model.eval()  # Set to evaluation mode

                    print(f"✅ Successfully loaded {description}!")
                    return  # Success, exit the loop

                except Exception as e:
                    print(f"  ⚠️ Failed to load {description}: {e}")
                    continue

            # If we get here, all models failed
            print("⚠️ All transformer models failed to load, using TF-IDF mode")

        except ImportError:
            print("📦 Transformers library not available, using TF-IDF mode")
        except Exception as e:
            print(f"⚠️ Model loading failed: {e}, falling back to TF-IDF")

    def is_ai_available(self) -> bool:
        """Check if any AI analysis is available"""
        return self.tfidf_vectorizer is not None or self.model is not None

    def is_transformer_available(self) -> bool:
        """Check if transformer model is loaded"""
        return self.model is not None and self.tokenizer is not None

    def _load_code_patterns(self) -> Dict:
        """Load lightweight code pattern knowledge base"""
        return {
            'complexity_indicators': [
                r'for.*for.*for',  # Triple nested loops
                r'if.*if.*if.*if',  # Deep nested conditions
                r'try.*except.*try.*except',  # Multiple exception handling
                r'def.*def.*def.*def',  # Many functions in one block
                r'while.*while',  # Nested while loops
            ],
            'quality_patterns': {
                'good': [
                    r'def\s+test_\w+',  # Test functions
                    r'"""[\s\S]*?"""',  # Docstrings
                    r'#\s*TODO:.*',  # Documented todos
                    r'logging\.',  # Proper logging
                    r'raise\s+\w+Error',  # Proper exception raising
                    r'@\w+',  # Decorators
                    r'assert\s+',  # Assertions
                    r'with\s+open',  # Context managers
                ],
                'bad': [
                    r'eval\s*\(',  # Dangerous eval
                    r'exec\s*\(',  # Dangerous exec
                    r'import\s+\*',  # Star imports
                    r'except\s*:(?!\s*raise)',  # Bare except without re-raise
                    r'print\s*\(',  # Print instead of logging
                    r'pass\s*#.*TODO',  # Empty implementations with TODO
                    r'\.format\s*\([^)]*request',  # Potential injection
                ]
            },
            'code_smells': [
                r'def\s+\w+\([^)]{80,}\)',  # Very long parameter lists
                r'class\s+\w+.*:\s*pass',  # Empty classes
                r'if\s+.*:\s*pass',  # Empty if blocks
                r'while\s+True:(?!\s*#)',  # Infinite loops without comments
                r'global\s+\w+',  # Global variables
                r'lambda.*lambda',  # Nested lambdas
            ],
            'security_patterns': [
                r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
                r'api_key\s*=\s*["\'][^"\']+["\']',  # Hardcoded API keys
                # Shell injection risk
                r'subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True',
                r'pickle\.loads?\s*\(',  # Unsafe deserialization
            ]
        }

    def analyze_code_intelligence(self, code: str, filename: str = "") -> List[Dict]:
        """Main AI analysis method"""
        insights = []

        try:
            # Method 1: Transformer-based analysis (if available)
            if self.is_transformer_available():
                transformer_insights = self._analyze_with_transformers(
                    code, filename)
                insights.extend(transformer_insights)

            # Method 2: TF-IDF based similarity analysis
            if self.tfidf_vectorizer is not None:
                tfidf_insights = self._analyze_with_tfidf(code, filename)
                insights.extend(tfidf_insights)

            # Method 3: Pattern-based AI insights
            pattern_insights = self._analyze_with_patterns(code, filename)
            insights.extend(pattern_insights)

            # Method 4: Statistical analysis
            stats_insights = self._analyze_code_statistics(code, filename)
            insights.extend(stats_insights)

            # Method 5: Semantic analysis
            semantic_insights = self._analyze_code_semantics(code, filename)
            insights.extend(semantic_insights)

        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            # Return at least basic analysis
            insights.append({
                'type': 'analysis_error',
                'severity': 'info',
                'message': f'⚠️ AI analysis partially unavailable, using fallback methods',
                'source': 'error_handler'
            })

        return insights

    def _analyze_with_transformers(self, code: str, filename: str) -> List[Dict]:
        """Analysis using lightweight transformer model"""
        insights = []

        try:
            # Import torch here to avoid import errors
            import torch

            # Prepare code for analysis (truncate if too long)
            code_sample = code[:1000] if len(code) > 1000 else code

            # Tokenize code
            inputs = self.tokenizer(
                code_sample,
                return_tensors="pt",
                max_length=256,  # Shorter for speed and memory
                truncation=True,
                padding=True
            )

            # Get embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)

                # Calculate various metrics from embeddings
                embedding_norm = torch.norm(embeddings).item()
                embedding_mean = torch.mean(embeddings).item()
                embedding_std = torch.std(embeddings).item()

            # Analyze embedding characteristics
            if embedding_norm > 15:  # High complexity indicator
                insights.append({
                    'type': 'ai_complexity',
                    'severity': 'info',
                    'message': f'🧠 AI detected high semantic complexity (embedding norm: {embedding_norm:.1f})',
                    'source': 'transformer_analysis',
                    'confidence': min(0.9, embedding_norm / 20)
                })

            if embedding_std > 0.5:  # High variability
                insights.append({
                    'type': 'ai_variability',
                    'severity': 'info',
                    'message': f'🔀 AI detected high code variability (std: {embedding_std:.2f}) - consider refactoring',
                    'source': 'transformer_analysis',
                    'confidence': min(0.8, embedding_std)
                })

            # Low complexity is also worth noting
            if embedding_norm < 5 and len(code.split('\n')) > 10:
                insights.append({
                    'type': 'ai_simplicity',
                    'severity': 'info',
                    'message': f'✨ AI detected well-structured, readable code patterns',
                    'source': 'transformer_analysis',
                    'confidence': 0.7
                })

        except Exception as e:
            logger.error(f"Transformer analysis failed: {e}")
            insights.append({
                'type': 'transformer_error',
                'severity': 'info',
                'message': '⚠️ Advanced AI analysis temporarily unavailable',
                'source': 'transformer_analysis'
            })

        return insights

    def _analyze_with_tfidf(self, code: str, filename: str) -> List[Dict]:
        """TF-IDF based code analysis"""
        insights = []

        try:
            # Extract meaningful tokens from code
            code_tokens = re.findall(
                r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code.lower())
            code_text = ' '.join(code_tokens)

            if len(code_text.strip()) == 0:
                return insights

            # Compare with known code patterns
            similarity_score = self._calculate_pattern_similarity(code_text)

            if similarity_score > 0.8:
                insights.append({
                    'type': 'pattern_similarity',
                    'severity': 'info',
                    'message': f'📊 Code follows established patterns (similarity: {similarity_score:.2f})',
                    'source': 'tfidf_analysis',
                    'confidence': similarity_score
                })
            elif similarity_score < 0.3:
                insights.append({
                    'type': 'pattern_uniqueness',
                    'severity': 'info',
                    'message': f'🔍 Unique code patterns detected (similarity: {similarity_score:.2f}) - ensure good documentation',
                    'source': 'tfidf_analysis',
                    'confidence': 1 - similarity_score
                })

            # Analyze code vocabulary diversity
            unique_tokens = len(set(code_tokens))
            total_tokens = len(code_tokens)

            if total_tokens > 0:
                vocabulary_diversity = unique_tokens / total_tokens

                if vocabulary_diversity > 0.7:
                    insights.append({
                        'type': 'vocabulary_diversity',
                        'severity': 'info',
                        'message': f'📚 High vocabulary diversity ({vocabulary_diversity:.2f}) - good abstraction',
                        'source': 'tfidf_analysis',
                        'confidence': vocabulary_diversity
                    })
                elif vocabulary_diversity < 0.3 and total_tokens > 20:
                    insights.append({
                        'type': 'vocabulary_repetition',
                        'severity': 'info',
                        'message': f'🔄 Repetitive vocabulary ({vocabulary_diversity:.2f}) - consider refactoring common patterns',
                        'source': 'tfidf_analysis',
                        'confidence': 1 - vocabulary_diversity
                    })

        except Exception as e:
            logger.error(f"TF-IDF analysis failed: {e}")

        return insights

    def _analyze_with_patterns(self, code: str, filename: str) -> List[Dict]:
        """Pattern-based AI insights"""
        insights = []

        try:
            # Good patterns analysis
            good_pattern_count = 0
            good_patterns_found = []
            for pattern in self.code_patterns['quality_patterns']['good']:
                matches = re.findall(pattern, code, re.MULTILINE | re.DOTALL)
                if matches:
                    good_pattern_count += len(matches)
                    good_patterns_found.append(pattern)

            # Bad patterns analysis
            bad_pattern_count = 0
            bad_patterns_found = []
            for pattern in self.code_patterns['quality_patterns']['bad']:
                matches = re.findall(pattern, code, re.MULTILINE)
                if matches:
                    bad_pattern_count += len(matches)
                    bad_patterns_found.append(pattern)

            # Security patterns
            security_pattern_count = 0
            for pattern in self.code_patterns['security_patterns']:
                matches = re.findall(pattern, code, re.MULTILINE)
                if matches:
                    security_pattern_count += len(matches)

            # Calculate quality score
            total_patterns = good_pattern_count + bad_pattern_count
            if total_patterns > 0:
                quality_ratio = good_pattern_count / total_patterns

                if quality_ratio > 0.7:
                    insights.append({
                        'type': 'quality_patterns',
                        'severity': 'info',
                        'message': f'✨ Excellent coding patterns detected ({good_pattern_count}/{total_patterns})',
                        'source': 'pattern_analysis',
                        'confidence': quality_ratio
                    })
                elif quality_ratio < 0.3:
                    insights.append({
                        'type': 'quality_patterns',
                        'severity': 'warning',
                        'message': f'⚠️ Concerning patterns detected ({bad_pattern_count}/{total_patterns}) - review recommended',
                        'source': 'pattern_analysis',
                        'confidence': 1 - quality_ratio
                    })

            # Security patterns warning
            if security_pattern_count > 0:
                insights.append({
                    'type': 'security_patterns',
                    'severity': 'warning',
                    'message': f'🔒 {security_pattern_count} potential security pattern(s) detected - review carefully',
                    'source': 'pattern_analysis',
                    'confidence': 0.8
                })

            # Code smell detection
            code_smell_count = 0
            for pattern in self.code_patterns['code_smells']:
                matches = re.findall(pattern, code, re.MULTILINE)
                if matches:
                    code_smell_count += len(matches)

            if code_smell_count > 0:
                insights.append({
                    'type': 'code_smells',
                    'severity': 'info',
                    'message': f'👃 {code_smell_count} code smell(s) detected - consider refactoring',
                    'source': 'pattern_analysis',
                    'confidence': 0.7
                })

        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")

        return insights

    def _analyze_code_statistics(self, code: str, filename: str) -> List[Dict]:
        """Statistical analysis of code"""
        insights = []

        try:
            lines = code.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]

            if len(non_empty_lines) == 0:
                return insights

            # Calculate various metrics
            avg_line_length = np.mean([len(line) for line in non_empty_lines])
            max_line_length = max([len(line) for line in non_empty_lines])

            # Indentation analysis
            indentations = []
            for line in non_empty_lines:
                if line.strip():  # Skip empty lines
                    indent = len(line) - len(line.lstrip())
                    indentations.append(indent)

            avg_indentation = np.mean(indentations) if indentations else 0
            max_indentation = max(indentations) if indentations else 0

            # Complexity indicators
            complexity_keywords = ['if', 'for', 'while',
                                   'try', 'def', 'class', 'elif', 'except']
            complexity_count = sum(1 for line in non_empty_lines
                                   for keyword in complexity_keywords
                                   if keyword in line.lower())

            complexity_density = complexity_count / \
                len(non_empty_lines) if non_empty_lines else 0

            # Generate insights based on statistics
            if avg_line_length > 100:
                insights.append({
                    'type': 'line_length',
                    'severity': 'info',
                    'message': f'📏 Average line length is {avg_line_length:.1f} chars (consider shorter lines for readability)',
                    'source': 'statistical_analysis',
                    'confidence': min(0.9, (avg_line_length - 80) / 50)
                })

            if max_indentation > 20:  # More than 5 levels of indentation
                insights.append({
                    'type': 'deep_nesting',
                    'severity': 'warning',
                    'message': f'🪆 Deep nesting detected ({max_indentation // 4} levels) - consider refactoring',
                    'source': 'statistical_analysis',
                    'confidence': min(0.9, max_indentation / 30)
                })

            if complexity_density > 0.4:
                insights.append({
                    'type': 'keyword_density',
                    'severity': 'info',
                    'message': f'🔢 High keyword density ({complexity_density:.2f}) - complex logic detected',
                    'source': 'statistical_analysis',
                    'confidence': min(0.8, complexity_density)
                })
            elif complexity_density < 0.1 and len(non_empty_lines) > 10:
                insights.append({
                    'type': 'low_complexity',
                    'severity': 'info',
                    'message': f'✨ Low complexity code ({complexity_density:.2f}) - well structured',
                    'source': 'statistical_analysis',
                    'confidence': 0.7
                })

        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")

        return insights

    def _analyze_code_semantics(self, code: str, filename: str) -> List[Dict]:
        """Semantic analysis of code structure"""
        insights = []

        try:
            # Function and class analysis
            functions = re.findall(r'def\s+(\w+)', code)
            classes = re.findall(r'class\s+(\w+)', code)
            imports = re.findall(r'(?:from\s+\w+\s+)?import\s+([^\n]+)', code)

            # Naming convention analysis
            function_naming_issues = 0
            for func in functions:
                if not re.match(r'^[a-z_][a-z0-9_]*$', func):  # snake_case check
                    function_naming_issues += 1

            class_naming_issues = 0
            for cls in classes:
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', cls):  # PascalCase check
                    class_naming_issues += 1

            # Generate semantic insights
            if len(functions) > 10:
                insights.append({
                    'type': 'function_density',
                    'severity': 'info',
                    'message': f'🏗️ High function density ({len(functions)} functions) - good modularization',
                    'source': 'semantic_analysis',
                    'confidence': 0.7
                })

            if function_naming_issues > 0:
                insights.append({
                    'type': 'naming_convention',
                    'severity': 'info',
                    'message': f'📝 {function_naming_issues} function naming convention issue(s) - consider snake_case',
                    'source': 'semantic_analysis',
                    'confidence': 0.8
                })

            if class_naming_issues > 0:
                insights.append({
                    'type': 'naming_convention',
                    'severity': 'info',
                    'message': f'📝 {class_naming_issues} class naming convention issue(s) - consider PascalCase',
                    'source': 'semantic_analysis',
                    'confidence': 0.8
                })

            # Import analysis
            if len(imports) > 15:
                insights.append({
                    'type': 'import_density',
                    'severity': 'info',
                    'message': f'📦 Many imports ({len(imports)}) - consider dependency management',
                    'source': 'semantic_analysis',
                    'confidence': 0.6
                })

        except Exception as e:
            logger.error(f"Semantic analysis failed: {e}")

        return insights

    def _calculate_pattern_similarity(self, code_text: str) -> float:
        """Calculate similarity to common code patterns"""
        try:
            # Common code patterns for different types of code
            common_patterns = [
                "def function return if else for while try except import class method self",
                "data process result check validate test setup teardown mock assert",
                "file read write open close save load json csv database connection",
                "request response http get post put delete api client server",
                "user authentication login logout session token password hash",
                "error exception handling logging debug info warning critical",
                "config settings environment variable parameter argument option",
                "model view controller service repository factory pattern"
            ]

            if not code_text.strip():
                return 0.5  # Neutral similarity for empty code

            # Fit vectorizer and calculate similarity
            all_texts = common_patterns + [code_text]

            # Use a simple approach if sklearn fails
            try:
                tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
                code_vector = tfidf_matrix[-1]
                pattern_vectors = tfidf_matrix[:-1]
                similarities = cosine_similarity(
                    code_vector, pattern_vectors)[0]
                return float(np.max(similarities))
            except:
                # Fallback to simple word overlap
                code_words = set(code_text.lower().split())
                max_similarity = 0

                for pattern in common_patterns:
                    pattern_words = set(pattern.lower().split())
                    if len(pattern_words) > 0:
                        overlap = len(code_words.intersection(pattern_words))
                        similarity = overlap / len(pattern_words)
                        max_similarity = max(max_similarity, similarity)

                return max_similarity

        except Exception as e:
            logger.error(f"Pattern similarity calculation failed: {e}")
            return 0.5  # Default neutral similarity

    def get_code_embedding_lightweight(self, code: str) -> Optional[np.ndarray]:
        """Get lightweight code embedding"""
        if self.is_transformer_available():
            return self._get_transformer_embedding(code)
        else:
            return self._get_statistical_embedding(code)

    def _get_transformer_embedding(self, code: str) -> Optional[np.ndarray]:
        """Get transformer-based embedding"""
        try:
            import torch

            # Prepare code
            code_sample = code[:500] if len(code) > 500 else code

            inputs = self.tokenizer(
                code_sample,
                return_tensors="pt",
                max_length=128,
                truncation=True,
                padding=True
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling
                embedding = outputs.last_hidden_state.mean(
                    dim=1).squeeze().numpy()

            return embedding

        except Exception as e:
            logger.error(f"Transformer embedding failed: {e}")
            return None

    def _get_statistical_embedding(self, code: str) -> np.ndarray:
        """Get statistical-based embedding"""
        try:
            # Create a feature vector based on code characteristics
            lines = code.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]

            features = {
                'length': len(code),
                'lines': len(non_empty_lines),
                'avg_line_length': np.mean([len(line) for line in non_empty_lines]) if non_empty_lines else 0,
                'functions': len(re.findall(r'def\s+\w+', code)),
                'classes': len(re.findall(r'class\s+\w+', code)),
                'imports': len(re.findall(r'import\s+\w+', code)),
                'complexity': len(re.findall(r'if|for|while|try', code)),
                'comments': len(re.findall(r'#.*', code)),
                'strings': len(re.findall(r'["\'].*?["\']', code)),
                'numbers': len(re.findall(r'\b\d+\b', code))
            }

            # Normalize features
            embedding = np.array(list(features.values()), dtype=np.float32)

            # Simple normalization
            if np.max(embedding) > 0:
                embedding = embedding / np.max(embedding)

            return embedding

        except Exception as e:
            logger.error(f"Statistical embedding failed: {e}")
            return np.zeros(10, dtype=np.float32)
