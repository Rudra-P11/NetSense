# NetSense ML Enhancements Implementation Plan

## Phase 1: Setup and Data Collection Infrastructure ✅
- [x] Update requirements.txt with ML dependencies (scikit-learn, tensorflow, joblib, nltk)
- [x] Create data_collector.py for training data collection and preprocessing
- [x] Create model_storage.py for saving/loading trained models locally
- [x] Test Phase 1 components

## Phase 2: Adaptive Website Classification with ML ✅
- [x] Refactor website_classifier.py to support ML-based classification
- [x] Add feature extraction (domain patterns, access times, etc.)
- [x] Implement user labeling UI in dashboard.py
- [x] Add confidence scoring and fallback to rules
- [x] Enhance filtering for common repeating sites (chrome-cloudflaredns.com, akamai.net, etc.)
- [x] Add ML statistics and training methods
- [x] Update data_collector.py to provide dashboard-compatible statistics

## Phase 3: Anomaly Detection for Unusual Network Behavior
- [ ] Create anomaly_detector.py with Isolation Forest
- [ ] Integrate anomaly detection into dns_sniffer.py
- [ ] Add anomaly alerts and visualization in dashboard.py

## Phase 4: Predictive Productivity Forecasting
- [ ] Create productivity_predictor.py with LSTM/ARIMA models
- [ ] Add forecasting charts in dashboard.py
- [ ] Implement productivity recommendations

## Phase 5: Deep Packet Inspection for Content Analysis
- [ ] Create content_analyzer.py with NLP models
- [ ] Extend dns_sniffer.py for payload inspection (with consent)
- [ ] Add content-based insights in dashboard.py

## Followup Steps
- [x] Install and test new dependencies
- [ ] Performance testing for real-time inference
- [ ] User testing and validation
- [ ] Data privacy verification
