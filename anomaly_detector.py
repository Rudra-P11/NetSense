import time
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from collections import defaultdict, deque
import threading
from typing import Dict, List, Tuple, Optional
import pandas as pd

class AnomalyDetector:
    """
    Anomaly detection system for network behavior using Isolation Forest.
    Detects unusual patterns in domain access, packet rates, and timing.
    """

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        """
        Initialize the anomaly detector.

        Args:
            contamination: Expected proportion of anomalies (0.1 = 10%)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state

        # ML components
        self.isolation_forest = None
        self.scaler = None
        self.is_trained = False

        # Data storage
        self.feature_history = deque(maxlen=1000)  # Store recent feature vectors
        self.anomaly_alerts = deque(maxlen=100)    # Store recent alerts
        self.baseline_features = []                # Baseline normal behavior
        self.lock = threading.Lock()

        # Feature extraction parameters
        self.work_hours = (9, 17)  # 9 AM to 5 PM
        self.min_baseline_samples = 50

        # Initialize the model
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the Isolation Forest model"""
        self.isolation_forest = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto'
        )
        self.scaler = StandardScaler()

    def extract_features(self, domain: str, packet_info: Dict, domain_stats: Dict) -> Dict:
        """
        Extract features for anomaly detection from packet and domain data.

        Args:
            domain: Domain name
            packet_info: Packet information (timestamp, protocol, etc.)
            domain_stats: Current domain statistics

        Returns:
            Dictionary of extracted features
        """
        current_time = packet_info.get('timestamp', time.time())

        # Time-based features
        hour_of_day = time.localtime(current_time).tm_hour
        is_work_hours = 1 if self.work_hours[0] <= hour_of_day < self.work_hours[1] else 0
        is_weekend = 1 if time.localtime(current_time).tm_wday >= 5 else 0

        # Domain-based features
        domain_length = len(domain)
        subdomain_count = domain.count('.')
        has_www = 1 if domain.startswith('www.') else 0

        # Packet-based features
        packet_count = domain_stats.get('packet_count', 0)
        time_since_first_seen = current_time - domain_stats.get('first_seen', current_time)
        time_since_last_seen = current_time - domain_stats.get('last_seen', current_time)

        # Rate calculations (packets per minute)
        if time_since_first_seen > 0:
            packet_rate = packet_count / (time_since_first_seen / 60)
        else:
            packet_rate = 0

        # Protocol distribution (simplified)
        protocol = packet_info.get('protocol', 'HTTPS')
        is_https = 1 if protocol == 'HTTPS' else 0
        is_dns = 1 if protocol == 'DNS' else 0

        # Domain category (if available)
        category = packet_info.get('category', 'neutral')
        is_productive = 1 if category == 'productive' else 0
        is_unproductive = 1 if category == 'unproductive' else 0

        features = {
            'hour_of_day': hour_of_day,
            'is_work_hours': is_work_hours,
            'is_weekend': is_weekend,
            'domain_length': domain_length,
            'subdomain_count': subdomain_count,
            'has_www': has_www,
            'packet_count': packet_count,
            'packet_rate': packet_rate,
            'time_since_first_seen': time_since_first_seen,
            'time_since_last_seen': time_since_last_seen,
            'is_https': is_https,
            'is_dns': is_dns,
            'is_productive': is_productive,
            'is_unproductive': is_unproductive
        }

        return features

    def detect_anomaly(self, domain: str, packet_info: Dict, domain_stats: Dict) -> Tuple[bool, float, str]:
        """
        Detect if the current activity is anomalous.

        Args:
            domain: Domain name
            packet_info: Packet information
            domain_stats: Domain statistics

        Returns:
            Tuple of (is_anomaly, anomaly_score, alert_message)
        """
        features = self.extract_features(domain, packet_info, domain_stats)

        # Store features for baseline building
        with self.lock:
            self.feature_history.append(features)

        # Rule-based checks (always active)
        rule_anomaly, rule_message = self._rule_based_detection(domain, features, packet_info)

        # ML-based detection (if trained)
        ml_anomaly = False
        ml_score = 0.0

        if self.is_trained and len(self.feature_history) >= self.min_baseline_samples:
            try:
                feature_vector = np.array([list(features.values())])
                scaled_features = self.scaler.transform(feature_vector)
                ml_score = self.isolation_forest.decision_function(scaled_features)[0]
                ml_anomaly = self.isolation_forest.predict(scaled_features)[0] == -1
            except Exception as e:
                print(f"ML anomaly detection error: {e}")

        # Combine rule-based and ML detection
        is_anomaly = rule_anomaly or ml_anomaly
        anomaly_score = max(ml_score, 1.0 if rule_anomaly else 0.0)

        # Generate alert message
        alert_message = rule_message if rule_anomaly else "ML-detected anomaly" if ml_anomaly else ""

        # Store alert if anomaly detected
        if is_anomaly:
            alert = {
                'timestamp': time.time(),
                'domain': domain,
                'anomaly_score': anomaly_score,
                'alert_message': alert_message,
                'features': features,
                'packet_info': packet_info
            }
            with self.lock:
                self.anomaly_alerts.append(alert)

        return is_anomaly, anomaly_score, alert_message

    def _rule_based_detection(self, domain: str, features: Dict, packet_info: Dict) -> Tuple[bool, str]:
        """
        Rule-based anomaly detection for common patterns.

        Returns:
            Tuple of (is_anomaly, message)
        """
        # High packet rate anomaly
        if features['packet_rate'] > 100:  # More than 100 packets per minute
            return True, f"High packet rate: {features['packet_rate']:.1f} packets/min for {domain}"

        # Unusual timing for unproductive sites
        if features['is_unproductive'] and features['is_work_hours']:
            return True, f"Unproductive site {domain} accessed during work hours"

        # Sudden traffic spike (compare to recent average)
        if len(self.feature_history) > 10:
            recent_rates = [f.get('packet_rate', 0) for f in list(self.feature_history)[-10:]]
            avg_rate = np.mean(recent_rates)
            if features['packet_rate'] > avg_rate * 3:  # 3x average
                return True, f"Traffic spike: {features['packet_rate']:.1f} vs avg {avg_rate:.1f} packets/min"

        # New domain with immediate high activity
        if features['time_since_first_seen'] < 60 and features['packet_count'] > 10:
            return True, f"New domain {domain} with high initial activity ({features['packet_count']} packets)"

        return False, ""

    def update_baseline(self):
        """Update the baseline model with recent normal behavior"""
        with self.lock:
            if len(self.feature_history) < self.min_baseline_samples:
                return False

            # Use recent features for training
            recent_features = list(self.feature_history)[-self.min_baseline_samples:]
            feature_matrix = np.array([list(f.values()) for f in recent_features])

            try:
                # Fit scaler
                self.scaler.fit(feature_matrix)

                # Fit isolation forest
                scaled_features = self.scaler.transform(feature_matrix)
                self.isolation_forest.fit(scaled_features)

                self.is_trained = True
                print(f"Baseline updated with {len(recent_features)} samples")
                return True

            except Exception as e:
                print(f"Error updating baseline: {e}")
                return False

    def get_anomaly_stats(self) -> Dict:
        """Get statistics about detected anomalies"""
        with self.lock:
            total_alerts = len(self.anomaly_alerts)
            recent_alerts = list(self.anomaly_alerts)[-10:]  # Last 10 alerts

            # Calculate alert frequency
            if total_alerts > 1:
                time_span = recent_alerts[-1]['timestamp'] - recent_alerts[0]['timestamp']
                alerts_per_hour = (len(recent_alerts) / time_span) * 3600 if time_span > 0 else 0
            else:
                alerts_per_hour = 0

            return {
                'total_alerts': total_alerts,
                'alerts_per_hour': alerts_per_hour,
                'is_trained': self.is_trained,
                'baseline_samples': len(self.feature_history),
                'recent_alerts': recent_alerts
            }

    def clear_data(self):
        """Clear all stored data and reset the model"""
        with self.lock:
            self.feature_history.clear()
            self.anomaly_alerts.clear()
            self.baseline_features.clear()
            self.is_trained = False
            self._initialize_model()

    def get_feature_importance(self) -> Dict:
        """Get feature importance scores (simplified)"""
        if not self.is_trained or not hasattr(self.isolation_forest, 'feature_importances_'):
            return {}

        # For Isolation Forest, we can use feature importances if available
        try:
            importances = self.isolation_forest.feature_importances_
            feature_names = [
                'hour_of_day', 'is_work_hours', 'is_weekend', 'domain_length',
                'subdomain_count', 'has_www', 'packet_count', 'packet_rate',
                'time_since_first_seen', 'time_since_last_seen', 'is_https',
                'is_dns', 'is_productive', 'is_unproductive'
            ]

            return dict(zip(feature_names, importances))
        except:
            return {}
