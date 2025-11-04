# ⚡ NetSense Quick Start Guide

## 🎯 5-Minute Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run as Administrator
```
Right-click Command Prompt → "Run as administrator"
cd C:\Users\ASUS\Desktop\NetworkAnalyser - Copy
python main.py
```

### Step 3: Start Capturing
1. Click **"▶️ Start Capture"** button
2. The status should show **"🟢 Status: Running"**

### Step 4: Generate Data
Visit these websites in your browser:
- **Productive**: github.com, youtube.com (educational content), stack overflow.com
- **Unproductive**: netflix.com, instagram.com, tiktok.com
- **Neutral**: google.com, gmail.com, amazon.com

### Step 5: Watch Real-Time Data
- **Dashboard Tab**: Shows activity log
- **Productivity Tab**: Pie chart updates with your data
- **Network Tab**: Real-time bandwidth usage

---

## 📈 Timeline of Features

| Time | What Happens | Where to Check |
|------|--------------|-----------------|
| **Now** | Live activity tracking | Dashboard Tab |
| **1-5 min** | Pie chart shows data | Productivity Tab |
| **30 min** | Statistics populate | Dashboard stats |
| **1 hour** | Models auto-train | Console output |
| **2 hours** | Forecast available | Forecast Tab |
| **24 hours** | Better accuracy | ML Insights Tab |
| **Every 60 min** | Auto-retraining | Console (automated) |

---

## 🎛️ GUI Overview

### Tabs (Left to Right):

#### 1. 📊 **Dashboard**
- Real-time stats (domains, packets, score)
- Live activity log with color coding
- Scrollable interface

#### 2. 📈 **Productivity**
- Pie chart of productive/unproductive/neutral
- Detailed insights and recommendations
- Time breakdown analysis

#### 3. 🔮 **Forecast** ⭐ NEW
- 24-hour auto-generated predictions
- Multiple models (Linear, Gradient Boost, ARIMA, Prophet, LSTM)
- Ensemble forecast with confidence intervals
- Model performance metrics

#### 4. 🧠 **ML Insights** ⭐ NEW
- Seasonal decomposition graphs
- Productivity clustering analysis
- Advanced statistics
- Model training status

#### 5. 📶 **Network**
- Upload/Download speeds
- Real-time network graph
- Connection count

#### 6. ⚠️ **Anomalies**
- Unusual activity detection
- Anomaly alerts
- Pattern analysis

---

## 🚀 What's New (vs Original)

### ✨ Automatic Features (No Buttons Needed)
- ✅ **Auto-Training**: Models retrain every 60 minutes
- ✅ **Auto-Forecasting**: Forecasts generated automatically
- ✅ **Auto-Updates**: All visualizations refresh in real-time

### ❌ Removed Unnecessary Buttons
- ~~"Train Model"~~ → Auto-trained now
- ~~"Train ARIMA Model"~~ → Included in auto-training
- ~~"Generate Forecast"~~ → Auto-generated now

### 📊 New Visualizations
- Seasonal decomposition (trend, seasonal, residual)
- Productivity clustering analysis
- Model performance comparison
- Confidence intervals on forecasts

### 🧠 New ML Models
- Prophet (Facebook's time series)
- LSTM (Neural network)
- Gradient Boosting (non-linear patterns)

### 🎨 Improved GUI
- Responsive layout (adapts to window size)
- Scrollable tabs (mouse wheel support)
- Better spacing and organization
- Modern emoji-enhanced interface
- Color-coded activity logs

---

## 💡 Understanding the Forecasts

### What You See:
```
🔮 Forecast Tab
├── Blue line: Ensemble prediction (average of all models)
├── Shaded area: Confidence interval (uncertainty)
└── X-axis: Hours ahead (0-24)

Model Performance & Insights
├── Active Models: ✅ Linear, Gradient Boost, ARIMA, etc.
├── Performance Metrics: R², MAE for each model
└── Auto-training: Enabled (every 60 minutes)
```

### Interpreting Results:
- **R² Score**: How well model fits (0=bad, 1=perfect) → Aim for >0.5
- **Confidence Interval**: Wider = more uncertainty
- **Ensemble**: Most reliable since it combines all models

### Example Reading:
```
Hour 2: Prediction = 75% ± 10%
Meaning: Expected productivity 75%, but could be 65-85% with 95% confidence
```

---

## 🎓 ML Insights Explained

### Seasonal Decomposition
Shows how your productivity breaks down:
```
Trend (top):    Your overall productivity direction
Seasonal (mid):  Weekly patterns (e.g., Monday is always low)
Residual (bot):  Random variations
```

### Clustering
Groups your productivity into 3 patterns:
```
Cluster 1 (Green):   High productivity days/hours
Cluster 2 (Red):     Low productivity
Cluster 3 (Orange):  Medium productivity
```

**Use it to**: Identify when you're most productive!

---

## 📊 Monitoring Auto-Training

### In Console:
Look for messages like:
```
[AUTO-TRAINER] Starting automatic model training cycle #1
[AUTO-TRAINER] Training with 432 data points...
[AUTO-TRAINER] Successfully trained 6/6 models
```

### In GUI:
Check **Forecast Tab** → "Model Performance & Insights"
- Shows which models are trained ✅
- Last training time
- Next retraining countdown

---

## 🔧 Common Tasks

### Q: How do I see what websites were captured?
**A:** Dashboard Tab → Recent Activity (scrollable list)

### Q: Why is my productivity score 0%?
**A:** No data collected yet. Visit websites for 5+ minutes.

### Q: The forecast shows flat line - why?
**A:** Not enough data. Wait 2+ hours for models to train.

### Q: Can I manually force retraining?
**A:** Models auto-train every 60 min. No manual intervention needed.

### Q: How do I clear old data?
**A:** Click "🗑️ Clear Data" button in header.

### Q: What does the colored activity mean?
```
🟢 Green = Productive site
🔴 Red = Unproductive site
⚪ Gray = Neutral site
```

---

## ⚙️ Settings & Customization

### Auto-Training Interval
Edit in `main.py`:
```python
training_scheduler = TrainingScheduler(productivity_predictor, interval_minutes=60)
                                                                               ↑
                                                              Change this to any value
```

### Forecast Horizon
Edit in `dashboard.py`:
```python
forecasts = predictor.forecast_productivity(24)  # Change 24 to any hour
```

### Data Retention
Edit in `productivity_predictor.py`:
```python
self.max_history = 2000  # Maximum data points to keep
```

---

## 🚨 Troubleshooting

### App won't start?
```
❌ Error: Administrator privileges required
✅ Fix: Right-click Command Prompt → "Run as administrator"
```

### Models not training?
```
❌ Insufficient data warning
✅ Fix: Collect more data (minimum 48 data points)
        Visit 5-10 different websites for 30+ minutes
```

### Forecast not showing?
```
❌ "Models training automatically..."
✅ Fix: Wait 2+ hours for models to train on initial data
        Or manually visit more websites
```

### Import errors?
```
❌ ModuleNotFoundError: No module named 'prophet'
✅ Fix: pip install pystan==2.19.1.1 prophet
```

### GUI freezes?
```
❌ Application becomes unresponsive
✅ Fix: Models training in background (normal)
        Wait 30-60 seconds for training to complete
```

---

## 📚 Learn More

- **Full Documentation**: See `IMPROVEMENTS.md`
- **ML Details**: Check inline comments in `productivity_predictor.py`
- **Architecture**: See `main.py` component initialization

---

## ✅ Checklist for First Use

- [ ] Run as Administrator
- [ ] Dependencies installed
- [ ] App starts without errors
- [ ] Click "Start Capture"
- [ ] Visit 5+ different websites
- [ ] Check Dashboard tab for activity
- [ ] Check Productivity tab for pie chart
- [ ] Wait 1 hour for model training
- [ ] Check Forecast tab for predictions
- [ ] Check ML Insights tab for analysis

---

## 🎉 You're Ready!

You now have a state-of-the-art productivity analyzer running automatically!

**Key Points:**
- ✅ No manual training needed (auto every 60 min)
- ✅ Forecasts generated automatically
- ✅ Multiple ML models working together
- ✅ Beautiful, responsive interface
- ✅ Advanced analytics and insights

**Happy analyzing! 📊**

---

## 📞 Quick Reference

| Feature | Location | Status |
|---------|----------|--------|
| Activity Log | Dashboard Tab | ✅ Real-time |
| Productivity Score | Dashboard Stats | ✅ Real-time |
| Pie Chart | Productivity Tab | ✅ Real-time |
| Forecast | Forecast Tab | ✅ Auto-updated |
| Models Status | Forecast Tab → Insights | ✅ Auto-trained |
| Seasonal Analysis | ML Insights Tab | ✅ Auto-generated |
| Clustering | ML Insights Tab | ✅ Auto-generated |
| Network Speed | Network Tab | ✅ Real-time |
| Anomalies | Anomalies Tab | ✅ Auto-detected |

---

**Version**: 2.0
**Last Updated**: 2024
**Status**: ✅ Ready to Use