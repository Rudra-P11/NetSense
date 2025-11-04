import re
import time
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import threading
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class ContentAnalyzer:
    """
    Advanced content analyzer using NLP for deep packet inspection.
    Performs sentiment analysis, keyword extraction, and content categorization.
    """

    def __init__(self, enable_deep_analysis: bool = False):
        self.enable_deep_analysis = enable_deep_analysis
        self.lock = threading.Lock()

        # Initialize NLTK resources
        self._initialize_nltk()

        # Content storage
        self.domain_content = defaultdict(lambda: {
            'text_samples': [],
            'sentiment_scores': [],
            'keywords': Counter(),
            'categories': Counter(),
            'last_analyzed': 0,
            'total_packets': 0
        })

        # Privacy and consent settings
        self.consent_domains = set()  # Domains user has consented to analyze
        self.privacy_filters = {
            'exclude_patterns': [
                r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',  # Credit cards
                r'\b\d{3}[\s\-]?\d{3}[\s\-]?\d{4}\b',  # SSN
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                r'\b\d{10,15}\b',  # Phone numbers
                r'password|passwd|pwd',  # Password keywords
            ]
        }

    def _initialize_nltk(self):
        """Initialize NLTK resources with better error handling"""
        try:
            # Download required NLTK data with better fallback handling
            required_packages = ['vader_lexicon', 'stopwords', 'wordnet']

            # Try punkt_tab first (newer NLTK), fallback to punkt
            try:
                nltk.download('punkt_tab', quiet=True)
                required_packages.append('punkt_tab')
            except:
                try:
                    nltk.download('punkt', quiet=True)
                    required_packages.append('punkt')
                except:
                    print("Warning: Could not download punkt tokenizer")
                    self.sia = None
                    return

            # Download other required packages
            for package in required_packages:
                try:
                    nltk.download(package, quiet=True)
                except Exception as e:
                    print(f"Warning: Failed to download {package}: {e}")

            # Initialize analyzers
            self.sia = SentimentIntensityAnalyzer()
            self.lemmatizer = WordNetLemmatizer()
            self.stop_words = set(stopwords.words('english'))

            # Add domain-specific stop words
            self.stop_words.update([
                'http', 'https', 'www', 'com', 'org', 'net', 'edu', 'gov',
                'html', 'php', 'asp', 'jsp', 'xml', 'json', 'api', 'css', 'js',
                'img', 'src', 'href', 'div', 'span', 'class', 'id', 'style'
            ])

        except Exception as e:
            print(f"Warning: NLTK initialization failed: {e}")
            self.sia = None

    def add_consent(self, domain: str):
        """Add user consent for deep analysis of a domain"""
        with self.lock:
            self.consent_domains.add(domain.lower())

    def remove_consent(self, domain: str):
        """Remove consent for a domain"""
        with self.lock:
            self.consent_domains.discard(domain.lower())

    def has_consent(self, domain: str) -> bool:
        """Check if user has consented to analyze a domain"""
        return domain.lower() in self.consent_domains

    def _sanitize_text(self, text: str) -> str:
        """Remove sensitive information from text"""
        sanitized = text
        for pattern in self.privacy_filters['exclude_patterns']:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
        return sanitized

    def _extract_text_from_payload(self, payload: bytes) -> Optional[str]:
        """Extract readable text from packet payload with improved filtering"""
        try:
            # Try to decode as UTF-8 first
            text = payload.decode('utf-8', errors='ignore')

            # Basic filtering - only keep printable characters and some punctuation
            text = re.sub(r'[^\x20-\x7E\n\r\t]', '', text)

            # Skip if too short
            if len(text) < 10:
                return None

            # Skip if too many non-text characters (strict threshold for quality)
            # Only count letters and spaces, not punctuation
            text_chars = sum(1 for c in text if c.isalpha() or c.isspace())
            if text_chars / len(text) < 0.4:
                return None

            # Skip if it looks like HTML content (lower threshold)
            if text.count('<') > len(text) * 0.05 or text.count('=') > len(text) * 0.05:
                return None

            return text

        except Exception:
            return None

    def analyze_payload(self, domain: str, payload: bytes, protocol: str = 'unknown') -> Optional[Dict]:
        """
        Analyze packet payload for content insights.
        Only performs analysis if deep analysis is enabled and user has consented.
        """
        if not self.enable_deep_analysis or not self.has_consent(domain):
            return None

        text = self._extract_text_from_payload(payload)
        if not text:
            return None

        # Sanitize text for privacy
        sanitized_text = self._sanitize_text(text)

        # Perform NLP analysis
        analysis_result = self._perform_nlp_analysis(sanitized_text)

        # Store results
        with self.lock:
            domain_data = self.domain_content[domain]
            domain_data['text_samples'].append(sanitized_text[:500])  # Store first 500 chars
            domain_data['sentiment_scores'].append(analysis_result.get('sentiment', {}))
            domain_data['keywords'].update(analysis_result.get('keywords', []))
            domain_data['categories'].update([analysis_result.get('category', 'unknown')])
            domain_data['last_analyzed'] = time.time()
            domain_data['total_packets'] += 1

            # Keep only recent samples (last 100)
            if len(domain_data['text_samples']) > 100:
                domain_data['text_samples'] = domain_data['text_samples'][-100:]
            if len(domain_data['sentiment_scores']) > 100:
                domain_data['sentiment_scores'] = domain_data['sentiment_scores'][-100:]

        return analysis_result

    def _perform_nlp_analysis(self, text: str) -> Dict:
        """Perform comprehensive NLP analysis on text"""
        result = {
            'sentiment': {},
            'keywords': [],
            'category': 'unknown',
            'readability_score': 0,
            'word_count': 0
        }

        if not self.sia:
            return result

        try:
            # Sentiment analysis
            sentiment = self.sia.polarity_scores(text)
            result['sentiment'] = {
                'compound': sentiment['compound'],
                'positive': sentiment['pos'],
                'negative': sentiment['neg'],
                'neutral': sentiment['neu']
            }

            # Keyword extraction
            keywords = self._extract_keywords(text)
            result['keywords'] = keywords[:10]  # Top 10 keywords

            # Content categorization
            category = self._categorize_content(text, keywords)
            result['category'] = category

            # Basic readability metrics
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            result['word_count'] = len(words)
            result['readability_score'] = len(words) / max(len(sentences), 1)

        except Exception as e:
            print(f"NLP analysis error: {e}")

        return result

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        try:
            # Tokenize and clean
            words = word_tokenize(text.lower())
            words = [w for w in words if w.isalnum() and w not in self.stop_words and len(w) > 2]

            # Lemmatize
            words = [self.lemmatizer.lemmatize(w) for w in words]

            # Count frequencies
            word_freq = Counter(words)

            # Return most common keywords
            return [word for word, _ in word_freq.most_common(20)]

        except Exception:
            return []

    def _categorize_content(self, text: str, keywords: List[str]) -> str:
        """Categorize content based on keywords and text patterns with improved accuracy"""
        text_lower = text.lower()
        keyword_str = ' '.join(keywords).lower()

        # Define category patterns with more comprehensive keywords
        categories = {
            'news': ['news', 'article', 'headline', 'breaking', 'update', 'report', 'journal', 'press', 'media'],
            'social': ['friend', 'post', 'share', 'like', 'comment', 'follow', 'timeline', 'profile', 'social', 'network'],
            'entertainment': ['video', 'music', 'movie', 'game', 'stream', 'watch', 'play', 'entertainment', 'fun'],
            'shopping': ['buy', 'price', 'sale', 'cart', 'checkout', 'product', 'store', 'shop', 'purchase', 'order'],
            'educational': ['learn', 'course', 'tutorial', 'study', 'research', 'guide', 'education', 'training', 'lesson'],
            'communication': ['message', 'chat', 'email', 'contact', 'inbox', 'notification', 'mail', 'conversation'],
            'financial': ['bank', 'money', 'payment', 'account', 'transaction', 'finance', 'investment', 'stock', 'loan'],
            'search': ['search', 'query', 'result', 'find', 'lookup', 'browse', 'google', 'bing', 'yahoo'],
            'productivity': ['work', 'task', 'project', 'document', 'file', 'edit', 'office', 'business', 'meeting'],
            'health': ['health', 'medical', 'fitness', 'diet', 'exercise', 'wellness', 'doctor', 'hospital', 'medicine']
        }

        # Score each category with weighted scoring
        scores = {}
        for category, patterns in categories.items():
            # Count keyword matches (higher weight)
            keyword_score = sum(1 for pattern in patterns if pattern in keyword_str) * 2
            # Count text matches (lower weight)
            text_score = sum(1 for pattern in patterns if pattern in text_lower)
            total_score = keyword_score + text_score

            if total_score > 0:
                scores[category] = total_score

        # Return highest scoring category
        if scores:
            return max(scores, key=scores.get)

        return 'general'

    def get_domain_insights(self, domain: str) -> Dict:
        """Get comprehensive insights for a domain"""
        with self.lock:
            if domain not in self.domain_content:
                return {}

            data = self.domain_content[domain]

            # Calculate average sentiment
            avg_sentiment = {}
            if data['sentiment_scores']:
                sentiments = data['sentiment_scores']
                for key in ['compound', 'positive', 'negative', 'neutral']:
                    values = [s.get(key, 0) for s in sentiments]
                    avg_sentiment[key] = sum(values) / len(values) if values else 0

            # Get top keywords
            top_keywords = data['keywords'].most_common(10)

            # Get top categories
            top_categories = data['categories'].most_common(3)

            return {
                'domain': domain,
                'total_packets_analyzed': data['total_packets'],
                'last_analyzed': data['last_analyzed'],
                'average_sentiment': avg_sentiment,
                'top_keywords': top_keywords,
                'top_categories': top_categories,
                'sample_count': len(data['text_samples']),
                'sentiment_trend': self._calculate_sentiment_trend(sentiments)
            }

    def _calculate_sentiment_trend(self, sentiments: List[Dict]) -> str:
        """Calculate sentiment trend over time"""
        if len(sentiments) < 5:
            return 'insufficient_data'

        # Get compound scores
        compounds = [s.get('compound', 0) for s in sentiments[-20:]]  # Last 20 samples

        if len(compounds) < 2:
            return 'stable'

        # Simple trend calculation
        first_half = compounds[:len(compounds)//2]
        second_half = compounds[len(compounds)//2:]

        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)

        diff = second_avg - first_avg

        if diff > 0.1:
            return 'improving'
        elif diff < -0.1:
            return 'declining'
        else:
            return 'stable'

    def get_content_statistics(self) -> Dict:
        """Get overall content analysis statistics"""
        with self.lock:
            total_domains = len(self.domain_content)
            total_packets = sum(data['total_packets'] for data in self.domain_content.values())

            # Overall sentiment distribution
            all_sentiments = []
            for data in self.domain_content.values():
                all_sentiments.extend(data['sentiment_scores'])

            sentiment_summary = {}
            if all_sentiments:
                for key in ['compound', 'positive', 'negative', 'neutral']:
                    values = [s.get(key, 0) for s in all_sentiments]
                    sentiment_summary[key] = {
                        'average': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values)
                    }

            # Category distribution
            category_counts = Counter()
            for data in self.domain_content.values():
                category_counts.update(data['categories'])

            return {
                'total_domains_analyzed': total_domains,
                'total_packets_analyzed': total_packets,
                'consented_domains': len(self.consent_domains),
                'sentiment_summary': sentiment_summary,
                'category_distribution': dict(category_counts.most_common()),
                'deep_analysis_enabled': self.enable_deep_analysis
            }

    def clear_domain_data(self, domain: str):
        """Clear all data for a specific domain"""
        with self.lock:
            if domain in self.domain_content:
                del self.domain_content[domain]

    def clear_all_data(self):
        """Clear all content analysis data"""
        with self.lock:
            self.domain_content.clear()

    def export_insights(self, domains: List[str] = None) -> Dict:
        """Export insights for specified domains or all domains"""
        with self.lock:
            if domains is None:
                domains = list(self.domain_content.keys())

            insights = {}
            for domain in domains:
                if domain in self.domain_content:
                    insights[domain] = self.get_domain_insights(domain)

            return {
                'export_timestamp': time.time(),
                'domains_analyzed': domains,
                'insights': insights,
                'statistics': self.get_content_statistics()
            }
