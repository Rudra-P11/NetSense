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

- **DNS Sniffer**: Captures and processes raw network packets
- **Website Classifier**: AI-like logic for domain categorization
- **Network Monitor**: Tracks bandwidth usage and connections
- **Dashboard**: Tkinter-based GUI with real-time visualizations

---

## 🌟 Key Features

### 🔍 Detection & Analysis
- ✅ Real-time tracking of websites (e.g. YouTube, Netflix, Instagram, GitHub)
- ✅ Productivity scoring algorithm (0–100%)
- ✅ Time spent analysis per category
- ✅ Live bandwidth monitoring

### 📊 Visual Analytics
- 📈 Real-time usage graphs
- 📊 Interactive pie charts showing productivity distribution
- 🎯 Color-coded activity logs
- 📱 Multi-tab GUI dashboard

### 🧠 Smart Insights
- 💡 Personalized productivity recommendations
- ⚡ Instant statistics and real-time alerts
- 📝 Historical activity tracking
- 🎮 Customizable website classifications

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
- ✅ **Intelligent Filtering**:
  - Eliminates infrastructure noise
- ✅ **High Performance**:
  - Real-time packet processing + GUI updates
- ✅ **User-Friendly Interface**:
  - Converts complex network data into readable insights

---

## 🛡️ Privacy & Ethics

- 🔒 **Local Processing Only** – No data ever leaves your machine
- 🚫 **No Storage** – No logs or user data saved
- 🔍 **Transparent** – Open-source for full code visibility
- ✅ **Consent-based Design** – Intended for personal, ethical use

---

## 📈 Impact & Value

This project demonstrates how **network programming**, **behavioral analytics**, and **data visualization** can power real-world, high-impact applications.

It transforms raw packet data into real insights that help users:

- Stay productive
- Understand their habits
- Take back control of their time

> **It bridges the gap between low-level networking and practical productivity tools.**

---

🎉 *Digital awareness starts with understanding your traffic. NetSense makes it possible.*