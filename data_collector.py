import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict
import time
import json
import os
from datetime import datetime, timedelta

class DataCollector:
    """
    Collects and preprocesses training data for ML models from user interactions.
    Handles data persistence and feature engineering for website classification.
    """

    def __init__(self, data_dir: str = "ml_data"):
        self.data_dir = data_dir
        self.training_data_file = os.path.join(data_dir, "training_data.json")
        self.feature_cache_file = os.path.join(data_dir, "feature_cache.json")

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Initialize data structures
        self.training_samples = []
        self.feature_cache = {}
        self.load_existing_data()

    def load_existing_data(self):
        """Load existing training data and feature cache"""
        try:
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r') as f:
                    self.training_samples = json.load(f)
                print(f"Loaded {len(self.training_samples)} training samples")
        except Exception as e:
            print(f"Error loading training data: {e}")
            self.training_samples = []

        try:
            if os.path.exists(self.feature_cache_file):
                with open(self.feature_cache_file, 'r') as f:
                    self.feature_cache = json.load(f)
                print(f"Loaded feature cache for {len(self.feature_cache)} domains")
        except Exception as e:
            print(f"Error loading feature cache: {e}")
            self.feature_cache = {}

    def save_data(self):
        """Save training data and feature cache to disk"""
        try:
            with open(self.training_data_file, 'w') as f:
                json.dump(self.training_samples, f, indent=2)
            print(f"Saved {len(self.training_samples)} training samples")

            with open(self.feature_cache_file, 'w') as f:
                json.dump(self.feature_cache, f, indent=2)
            print(f"Saved feature cache for {len(self.feature_cache)} domains")
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_training_sample(self, domain: str, category: str, confidence: float = 1.0,
                          timestamp: float = None, context: Dict = None):
        """
        Add a new training sample from user labeling.

        Args:
            domain: The website domain
            category: User-labeled category ('productive', 'unproductive', 'neutral')
            confidence: User confidence in the label (0-1)
            timestamp: When the sample was collected
            context: Additional context (time of day, frequency, etc.)
        """
        if timestamp is None:
            timestamp = time.time()

        if context is None:
            context = {}

        sample = {
            'domain': domain.lower().strip(),
            'category': category,
            'confidence': confidence,
            'timestamp': timestamp,
            'context': context
        }

        # Check if we already have this domain labeled
        existing_idx = None
        for i, existing in enumerate(self.training_samples):
            if existing['domain'] == sample['domain']:
                existing_idx = i
                break

        if existing_idx is not None:
            # Update existing sample with new label (user override)
            self.training_samples[existing_idx] = sample
            print(f"Updated label for {domain}: {category}")
        else:
            # Add new sample
            self.training_samples.append(sample)
            print(f"Added new training sample: {domain} -> {category}")

        # Invalidate feature cache for this domain
        if domain in self.feature_cache:
            del self.feature_cache[domain]

        self.save_data()

    def extract_domain_features(self, domain: str, access_history: Dict = None) -> Dict:
        """
        Extract features for a domain for ML classification.

        Args:
            domain: The domain to extract features for
            access_history: Historical access data for the domain

        Returns:
            Dictionary of features for ML model
        """
        domain = domain.lower().strip()

        # Check cache first
        if domain in self.feature_cache:
            return self.feature_cache[domain]

        features = {}

        # Basic domain features
        features['domain_length'] = len(domain)
        features['has_subdomain'] = 1 if '.' in domain and len(domain.split('.')) > 2 else 0
        features['tld'] = domain.split('.')[-1] if '.' in domain else 'unknown'
        features['has_numbers'] = 1 if any(c.isdigit() for c in domain) else 0
        features['has_hyphen'] = 1 if '-' in domain else 0

        # Keyword presence features (expanded from classifier)
        productive_keywords = [
            'learn', 'course', 'tutorial', 'doc', 'github', 'stackoverflow',
            'research', 'academic', 'study', 'code', 'dev', 'tech', 'science'
        ]
        unproductive_keywords = [
            'game', 'video', 'stream', 'social', 'chat', 'music', 'entertainment',
            'fun', 'play', 'watch', 'media', 'news', 'sport'
        ]
        neutral_keywords = [
            'search', 'mail', 'calendar', 'drive', 'cloud', 'bank', 'shop',
            'map', 'weather', 'gov', 'edu', 'org'
        ]

        features['productive_keywords'] = sum(1 for kw in productive_keywords if kw in domain)
        features['unproductive_keywords'] = sum(1 for kw in unproductive_keywords if kw in domain)
        features['neutral_keywords'] = sum(1 for kw in neutral_keywords if kw in domain)

        # Access pattern features (if history available)
        if access_history:
            features['total_access_time'] = access_history.get('total_time', 0)
            features['access_frequency'] = access_history.get('packet_count', 0)
            features['avg_session_length'] = access_history.get('avg_session', 0)
            features['peak_hour'] = access_history.get('peak_hour', 12)  # Default noon
            features['weekday_score'] = access_history.get('weekday_usage', 0.5)
        else:
            features['total_access_time'] = 0
            features['access_frequency'] = 0
            features['avg_session_length'] = 0
            features['peak_hour'] = 12
            features['weekday_score'] = 0.5

        # Domain reputation features (simplified)
        features['is_educational'] = 1 if any(ext in domain for ext in ['.edu', '.ac.', 'course', 'learn']) else 0
        features['is_government'] = 1 if '.gov' in domain or 'gov.' in domain else 0
        features['is_social'] = 1 if any(platform in domain for platform in ['facebook', 'twitter', 'instagram', 'tiktok']) else 0
        features['is_video'] = 1 if any(platform in domain for platform in ['youtube', 'netflix', 'twitch', 'vimeo']) else 0

        # Cache the features
        self.feature_cache[domain] = features
        return features

    def get_training_dataset(self, min_samples: int = 10) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare training dataset for ML model.

        Returns:
            X: Feature matrix
            y: Labels (0=neutral, 1=productive, 2=unproductive)
        """
        if len(self.training_samples) < min_samples:
            print(f"Warning: Only {len(self.training_samples)} samples, need at least {min_samples}")
            return pd.DataFrame(), np.array([])

        # Extract features for all samples
        features_list = []
        labels = []

        category_mapping = {'neutral': 0, 'productive': 1, 'unproductive': 2}

        for sample in self.training_samples:
            domain = sample['domain']
            category = sample['category']

            if category not in category_mapping:
                continue

            features = self.extract_domain_features(domain)
            features_list.append(features)
            labels.append(category_mapping[category])

        if not features_list:
            return pd.DataFrame(), np.array([])

        # Convert to DataFrame
        df = pd.DataFrame(features_list)

        # Handle missing values
        df = df.fillna(0)

        # Convert categorical features
        if 'tld' in df.columns:
            df['tld'] = pd.Categorical(df['tld']).codes

        return df, np.array(labels)

    def get_statistics(self) -> Dict:
        """Get statistics about collected training data"""
        if not self.training_samples:
            return {
                'total_samples': 0,
                'productive_count': 0,
                'unproductive_count': 0,
                'neutral_count': 0,
                'user_labels_count': 0,
                'recent_labels': []
            }

        categories = defaultdict(int)
        recent_samples = 0
        week_ago = time.time() - (7 * 24 * 60 * 60)
        recent_labels = []

        for sample in self.training_samples:
            categories[sample['category']] += 1
            if sample['timestamp'] > week_ago:
                recent_samples += 1
                recent_labels.append({
                    'domain': sample['domain'],
                    'category': sample['category'],
                    'timestamp': sample['timestamp']
                })

        # Sort recent labels by timestamp (most recent first)
        recent_labels.sort(key=lambda x: x['timestamp'], reverse=True)

        return {
            'total_samples': len(self.training_samples),
            'productive_count': categories.get('productive', 0),
            'unproductive_count': categories.get('unproductive', 0),
            'neutral_count': categories.get('neutral', 0),
            'user_labels_count': len(self.training_samples),
            'recent_labels': recent_labels[:10],  # Last 10 labels
            'categories': dict(categories),
            'recent_samples': recent_samples,
            'cached_features': len(self.feature_cache),
            'last_updated': max(s['timestamp'] for s in self.training_samples) if self.training_samples else 0
        }

    def clear_old_data(self, days: int = 90):
        """Clear training samples older than specified days"""
        cutoff = time.time() - (days * 24 * 60 * 60)
        original_count = len(self.training_samples)

        self.training_samples = [
            sample for sample in self.training_samples
            if sample['timestamp'] > cutoff
        ]

        removed = original_count - len(self.training_samples)
        if removed > 0:
            print(f"Cleared {removed} old training samples")
            self.save_data()

        return removed
