# 📡 NetSense – Real-Time Network Analyzer for Productivity Tracking

A smart, privacy-focused application that passively monitors your network activity and translates it into real-time insights about your digital productivity.

---

## 🏗️ Technical Architecture

### 🔍 Packet Capture
- Uses **Scapy** with **Npcap** to monitor traffic on ports:
  - 53 (DNS)
  - 80 (HTTP)
  - 443, 8080, 8443 (HTTPS)

### 🔎 Multi-Layer Analysis
- DNS query monitoring
- SSL/TLS SNI extraction (for HTTPS sites)
- HTTP header inspection
- IP-to-domain mapping via DNS responses

### 🧠 Smart Filtering
- Filters out:
  - CDNs (Cloudflare, Akamai, etc.)
  - Cloud service domains
  - Reverse DNS noise
- Only captures actual website domains

### ⚡ Real-Time Classification
- Instantly categorizes domains as:
  - ✅ Productive
  - ❌ Unproductive
  - ⚪ Neutral  
  based on customizable rules

---

## 🧩 Core Components

- **DNS Sniffer** (`dns_sniffer.py`): Captures and processes raw network packets
- **Data Collector** (`data_collector.py`): Aggregates network data and extracts ML-ready features
- **Website Classifier** (`website_classifier.py`): scikit-learn based ML model for domain categorization (Productive/Unproductive/Neutral)
- **Content Analyzer** (`content_analyzer.py`): NLTK-powered text analysis for enhanced classification
- **Anomaly Detector** (`anomaly_detector.py`): Real-time anomaly detection for suspicious network activity
- **Auto Trainer** (`auto_trainer.py`): Continuous model retraining with user feedback
- **Model Storage** (`model_storage.py`): Persistent model serialization and versioning
- **Network Monitor** (`network_usage.py`): Tracks bandwidth usage and connections
- **Productivity Predictor** (`productivity_predictor.py`): Forecasts productivity trends
- **Dashboard** (`dashboard.py`): Tkinter-based GUI with real-time visualizations and anomaly alerts

---

## 🌟 Key Features

### 🔍 Detection & Analysis
- ✅ Real-time tracking of websites (e.g. YouTube, Netflix, Instagram, GitHub)
- ✅ Productivity scoring algorithm (0–100%)
- ✅ Time spent analysis per category
- ✅ Live bandwidth monitoring
- ✅ Multi-layer packet analysis (DNS, HTTP, HTTPS/SNI)
- ✅ Automatic IP-to-domain mapping with reverse DNS validation

### 📊 Visual Analytics
- 📈 Real-time usage graphs
- 📊 Interactive pie charts showing productivity distribution
- 🎯 Color-coded activity logs
- 📱 Multi-tab GUI dashboard with 6 specialized views:
  - Overview (live stats)
  - Websites (detailed access log)
  - Timeline (productivity trends)
  - Productivity (scoring breakdown)
  - Anomalies (security alerts)
  - Insights (recommendations)

### 🧠 Smart Insights
- 💡 Personalized productivity recommendations
- ⚡ Instant statistics and real-time alerts
- 📝 Historical activity tracking
- 🎮 Customizable website classifications
- 🤖 ML-powered website categorization (scikit-learn)
- 📚 NLP analysis for enhanced accuracy (NLTK)

### 🔐 Anomaly Detection & Security
- 🚨 Real-time anomaly detection for suspicious network patterns:
  - Unusual packet rates (high/low thresholds)
  - Unexpected bandwidth spikes
  - Abnormal connection patterns
- 🎯 Smart alerting with confidence scoring (0.0-1.0)
- 📊 Historical anomaly tracking and trend analysis
- ⚠️ Live anomaly feed in dashboard with timestamps

### 🤖 Machine Learning & Auto-Training
- 🧠 Continuous model improvement with user feedback
- 📈 scikit-learn RandomForest classifier
- 🔄 Automatic retraining triggered by domain misclassifications
- 💾 Persistent model storage with versioning
- 📊 Feature engineering: TLD analysis, domain length, keyword matching
- 🎯 Adaptive learning from user corrections

---

## 🚀 Why This Project?

### 💢 Problem Solved
Most users don’t realize how much time they waste online.  
This tool brings **digital self-awareness** by providing clear, actionable data about browsing habits.

### 🌍 Real-World Applications
- 🧑‍💻 **Personal Productivity**: Focus tracking & time management
- 🏢 **Workplace Monitoring**: Employee analytics (with consent)
- 🎓 **Education**: Helps students monitor study vs distraction
- 👨‍👩‍👧 **Parental Control**: Track kids’ online activity trends

### 🧪 Technical Innovation
- Overcomes modern web complexity:
  - CDNs
  - HTTPS encryption
  - Dynamic IP/domain mapping
- Combines multi-layer packet analysis with smart local filtering
- Fully real-time, no delay or lag
- Local-only processing, ensuring privacy

---

## 🧠 Key Technical Achievements

- ✅ **Bypassed Modern Web Obstacles**:
  - Handles HTTPS and CDN-heavy traffic
  - Accurately detects actual domains (e.g. `youtube.com`, not `ytcdn.net`)
  - Robust port handling for IP:port combinations in ML pipeline
- ✅ **Intelligent Filtering**:
  - Eliminates infrastructure noise
  - Domain normalization and deduplication
- ✅ **High Performance**:
  - Real-time packet processing + GUI updates
  - Non-blocking background threads for ML inference
  - Efficient feature extraction and caching
- ✅ **Machine Learning Integration**:
  - Custom feature engineering pipeline
  - Thread-safe model training and inference
  - Persistent model storage with metadata
- ✅ **Anomaly Detection**:
  - Statistical threshold-based detection
  - Deque-based alert history with automatic pruning
  - Real-time scoring with confidence metrics
- ✅ **User-Friendly Interface**:
  - Converts complex network data into readable insights
  - 6 specialized dashboard tabs with rich visualizations
  - Live anomaly alerts with severity indicators

## 🔧 Recent Improvements (Latest Release)

- ✅ **TensorFlow Optimization**: Suppressed oneDNN warnings for cleaner startup
- ✅ **ML Pipeline Fix**: Added port stripping in domain feature extraction to handle IP:port strings
- ✅ **Anomaly Display Implementation**: 
  - Real-time anomaly alerts now display in Anomalies tab
  - Shows timestamp, alert message, and confidence score
  - Reverse chronological ordering (newest first)
  - Thread-safe deque access pattern
- ✅ **Enhanced Error Handling**: Improved robustness in network data processing

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+** (tested on 3.10+)
- **Windows OS** (with Npcap driver for packet capture)
- Administrator privileges (required for packet sniffing)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/NetSense.git
   cd NetSense
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

### Required Dependencies
- **scapy**: Packet capture and analysis
- **scikit-learn**: ML model training and inference
- **pandas**: Data processing
- **matplotlib/seaborn**: Visualization
- **nltk**: NLP analysis
- **psutil**: System monitoring
- **tkinter**: GUI framework

See `requirements.txt` for complete list with versions.

### Platform Requirements
- **Npcap**: Required for packet capture on Windows
  - Download from: https://nmap.org/npcap/
  - Install with WinPcap compatibility checked
- **Admin privileges**: Application must run as administrator

---

## 📁 Project Structure

```
NetSense/
├── main.py                      # Entry point
├── dns_sniffer.py              # Packet capture engine
├── data_collector.py           # Network data aggregation
├── website_classifier.py       # ML-based domain classification
├── content_analyzer.py         # NLTK-powered text analysis
├── anomaly_detector.py         # Real-time anomaly detection
├── auto_trainer.py             # Continuous model retraining
├── model_storage.py            # Model persistence
├── network_usage.py            # Bandwidth monitoring
├── productivity_predictor.py   # Trend forecasting
├── dashboard.py                # GUI dashboard (Tkinter)
├── requirements.txt            # Production dependencies
├── ml_data/                    # ML training data cache
│   ├── training_data.json     # Historical training samples
│   └── feature_cache.json     # Cached feature vectors
├── ml_models/                  # Trained model storage
│   ├── website_classifier_*.pkl  # Classification model
│   ├── feature_scaler_*.pkl      # Feature normalization
│   └── models_metadata.json      # Model metadata
└── README.md                   # This file
```

---

## 🎮 Usage Guide

### Dashboard Overview

The application displays real-time analytics across 6 main tabs:

#### 📊 **Overview Tab**
- Live statistics: total productivity score, uptime, active connections
- Real-time bandwidth usage graphs
- Current network activity status

#### 🌐 **Websites Tab**
- Detailed log of all visited websites
- Classification status (Productive/Unproductive/Neutral)
- Visit timestamps and duration
- Right-click to mark as misclassified for model retraining

#### 📈 **Timeline Tab**
- Productivity trends over time
- Hourly/daily productivity breakdown
- Visual patterns of your work habits
- Export trends for analysis

#### 🎯 **Productivity Tab**
- Category-wise productivity breakdown
- Pie charts showing time distribution
- Top productive and unproductive websites
- Customizable category definitions

#### ⚠️ **Anomalies Tab** *(NEW)*
- Real-time security alerts
- Suspicious network patterns detected:
  - High packet rate bursts
  - Unusual bandwidth spikes
  - Abnormal connection patterns
- Alert severity with confidence scoring
- Timestamp and detailed anomaly messages
- Historical anomaly tracking

#### 💡 **Insights Tab**
- AI-generated recommendations
- Productivity improvement suggestions
- Time management tips
- Personalized insights based on your patterns

### Feature Controls

- **Start/Stop Capture**: Begin/end network monitoring
- **Clear Data**: Reset current session statistics
- **Custom Classifications**: Edit website categorization rules
- **Model Training**: View model performance metrics
- **Settings**: Configure sensitivity, thresholds, alerts

---

## 🔬 Machine Learning Details

### Classification Model
- **Algorithm**: scikit-learn RandomForestClassifier
- **Features**:
  - Domain name characteristics (TLD, length, structure)
  - Keyword matching (productivity keywords vs distractions)
  - Historical classification data
  - User feedback corrections
- **Training**: Automatic on domain misclassification correction
- **Inference**: Real-time classification during packet analysis

### Anomaly Detection
- **Method**: Statistical threshold-based detection
- **Metrics Monitored**:
  - Packet rate (packets per minute)
  - Bandwidth usage (MB per timeframe)
  - Connection count spikes
  - Unusual protocol distributions
- **Scoring**: Confidence scores (0.0-1.0) for each alert
- **History**: Last 20 anomalies retained with full metadata

### Auto-Training System
- Triggered when user corrects domain classification
- Retrains model with expanded feature set
- Versions models with metadata timestamps
- Graceful fallback to previous model if training fails

---

## 🛡️ Privacy & Ethics

- 🔒 **Local Processing Only** – No data ever leaves your machine
- 🚫 **No Storage** – No logs or user data saved
- 🔍 **Transparent** – Open-source for full code visibility
- ✅ **Consent-based Design** – Intended for personal, ethical use
- 🔐 **No Packet Payload Inspection** – Only metadata analyzed
- 🌐 **No External API Calls** – Completely offline operation

---

## 📈 Impact & Value

This project demonstrates how **network programming**, **behavioral analytics**, **machine learning**, and **data visualization** can power real-world, high-impact applications.

It transforms raw packet data into real insights that help users:

- **Stay productive** – Understand where time is spent
- **Detect threats** – Real-time anomaly alerts for suspicious activity
- **Optimize workflows** – Data-driven productivity recommendations
- **Take control** – Machine learning adapts to your definitions

> **It bridges the gap between low-level networking and practical productivity tools with intelligent automation.**

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Permission Denied" or "Admin required"
- **Solution**: Run the application as Administrator (right-click → Run as administrator)

**Issue**: "Npcap not found" or packet capture not working
- **Solution**: Install Npcap from https://nmap.org/npcap/ with WinPcap compatibility enabled

**Issue**: "ModuleNotFoundError" for dependencies
- **Solution**: Run `pip install -r requirements.txt` in activated virtual environment

**Issue**: No websites appearing in dashboard
- **Solution**: 
  - Ensure capture is running (Start button)
  - Generate network traffic (visit websites, use browser)
  - Check that your network interface is selected
  - May take 5-10 seconds for first entries to appear

**Issue**: ML model crashes with "could not convert string to float"
- **Solution**: Ensure you're running the latest version with port-handling fixes

**Issue**: Anomalies not showing in Anomalies tab
- **Solution**: 
  - Check that capture is active
  - Anomalies may need 30+ seconds of capture for baseline
  - Ensure thresholds are appropriately configured
  - Check application logs for errors

**Issue**: Dashboard freezes during packet capture
- **Solution**: 
  - ML model inference runs in background threads
  - Initial model training may take 30 seconds on first run
  - Let application settle for 1-2 minutes after starting

---

## 📚 Documentation

- **QUICKSTART.md**: Step-by-step setup guide
- **START_HERE.md**: First-time user guide
- **TODO.md**: Planned features and improvements
- **IMPROVEMENTS.md**: Recent enhancements summary
- **CHANGES_SUMMARY.md**: Version history

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- **Feature Requests**: New analysis metrics or visualizations
- **Bug Fixes**: Edge cases in packet capture or ML pipeline
- **Performance**: Optimization for large datasets
- **Documentation**: Clearer guides and examples
- **UI/UX**: Enhanced dashboard design and usability

### Development Setup

```bash
# Clone and setup
git clone <repo>
cd NetSense
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run tests (if available)
pytest

# Make changes and submit PR
```

---

## 📞 Support & Contact

- **Issues**: GitHub Issues page
- **Discussions**: GitHub Discussions for questions
- **Email**: (contact information)

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **Scapy**: For powerful packet manipulation
- **scikit-learn**: For machine learning capabilities
- **Tkinter**: For the cross-platform GUI
- **NLTK**: For natural language processing
- **Matplotlib**: For beautiful visualizations

---

🎉 ***Digital awareness starts with understanding your traffic. NetSense makes it possible.***

**Built with ❤️ for productivity, powered by data.** 🚀