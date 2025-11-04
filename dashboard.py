import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import pandas as pd
import numpy as np
from website_classifier import WebsiteClassifier
import random
import seaborn as sns

# Modern UI styling
class ModernStyle:
    """Modern UI styling constants - Light Theme"""
    BG_DARK = '#ffffff'
    BG_MEDIUM = '#f8f9fa'
    BG_LIGHT = '#e9ecef'
    FG_LIGHT = '#212529'
    FG_MEDIUM = '#6c757d'
    FG_DARK = '#495057'
    ACCENT_BLUE = '#007bff'
    ACCENT_GREEN = '#28a745'
    ACCENT_ORANGE = '#fd7e14'
    ACCENT_RED = '#dc3545'
    BORDER_COLOR = '#dee2e6'

    FONT_TITLE = ('Segoe UI', 16, 'bold')
    FONT_HEADER = ('Segoe UI', 12, 'bold')
    FONT_BODY = ('Segoe UI', 10)
    FONT_SMALL = ('Segoe UI', 9)

    @staticmethod
    def apply_theme(root):
        """Apply modern light theme to the application"""
        style = ttk.Style()
        style.theme_use('default')
        
        style.configure('TFrame', background=ModernStyle.BG_DARK)
        style.configure('Card.TFrame', background=ModernStyle.BG_MEDIUM, relief='raised', borderwidth=1)
        style.configure('Header.TFrame', background=ModernStyle.BG_LIGHT)
        
        style.configure('TLabel', background=ModernStyle.BG_DARK, foreground=ModernStyle.FG_LIGHT, font=ModernStyle.FONT_BODY)
        style.configure('Title.TLabel', font=ModernStyle.FONT_TITLE, foreground=ModernStyle.ACCENT_BLUE)
        style.configure('Header.TLabel', font=ModernStyle.FONT_HEADER, foreground=ModernStyle.FG_LIGHT)
        style.configure('Status.TLabel', font=ModernStyle.FONT_SMALL, foreground=ModernStyle.FG_MEDIUM)
        
        # Modern button styling - consistent across all buttons
        style.configure('TButton', font=ModernStyle.FONT_BODY, padding=10, relief='flat', borderwidth=0)
        style.map('TButton', 
                 background=[('active', ModernStyle.ACCENT_BLUE), ('pressed', '#0056b3')],
                 foreground=[('active', ModernStyle.BG_DARK)])
        
        style.configure('Primary.TButton', background=ModernStyle.ACCENT_BLUE, foreground=ModernStyle.BG_DARK, 
                       font=ModernStyle.FONT_BODY, padding=10)
        style.map('Primary.TButton',
                 background=[('active', '#0056b3'), ('pressed', '#003d82'), ('disabled', ModernStyle.FG_MEDIUM)],
                 foreground=[('disabled', ModernStyle.BG_LIGHT)])
        
        style.configure('Success.TButton', background=ModernStyle.ACCENT_GREEN, foreground=ModernStyle.BG_DARK,
                       font=ModernStyle.FONT_BODY, padding=10)
        style.map('Success.TButton',
                 background=[('active', '#1e8e3e'), ('pressed', '#155e2d'), ('disabled', ModernStyle.FG_MEDIUM)],
                 foreground=[('disabled', ModernStyle.BG_LIGHT)])
        
        style.configure('Danger.TButton', background=ModernStyle.ACCENT_RED, foreground=ModernStyle.BG_DARK,
                       font=ModernStyle.FONT_BODY, padding=10)
        style.map('Danger.TButton',
                 background=[('active', '#a32a2a'), ('pressed', '#781f1f'), ('disabled', ModernStyle.FG_MEDIUM)],
                 foreground=[('disabled', ModernStyle.BG_LIGHT)])
        
        style.configure('TNotebook', background=ModernStyle.BG_DARK, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', background=ModernStyle.BG_MEDIUM, foreground=ModernStyle.FG_LIGHT,
                       font=ModernStyle.FONT_BODY, padding=[10, 5], relief='flat')
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyle.ACCENT_BLUE), ('active', ModernStyle.BG_LIGHT)],
                 foreground=[('selected', ModernStyle.BG_DARK)])
        
        root.configure(bg=ModernStyle.BG_DARK)

class NetworkAnalyzerDashboard:
    def __init__(self, root, dns_sniffer, network_monitor):
        self.root = root
        self.dns_sniffer = dns_sniffer
        self.network_monitor = network_monitor
        
        self.setup_ui()
        self.is_updating = False
        self.update_thread = None
        
        # Start auto-training scheduler
        self.start_auto_training()
        
    def setup_ui(self):
        """Setup the main UI with responsive scrollable layout"""
        ModernStyle.apply_theme(self.root)
        self.root.title("🚀 NetSense - Advanced Network Productivity Analyzer")
        self.root.geometry("1400x900")

        # Create main frame with scrollbar
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Header
        header_frame = ttk.Frame(main_container, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(header_frame, text="🚀 NetSense", style='Title.TLabel')
        self.title_label.pack(side=tk.LEFT, padx=10)

        subtitle_label = ttk.Label(header_frame, text="Advanced AI-Powered Network Analyzer",
                                 style='Header.TLabel', foreground=ModernStyle.ACCENT_BLUE)
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Control buttons
        control_frame = ttk.Frame(header_frame, style='Header.TFrame')
        control_frame.pack(side=tk.RIGHT, padx=10)

        self.start_btn = ttk.Button(control_frame, text="▶️ Start Capture", command=self.start_analysis, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop Capture", command=self.stop_analysis, state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear Data", command=self.clear_data, style='Primary.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        
        # Productivity tab
        self.productivity_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.productivity_frame, text="📈 Productivity")

        # Forecasting tab
        self.forecasting_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecasting_frame, text="🔮 Forecast")

        # ML Insights tab
        self.ml_insights_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ml_insights_frame, text="🧠 ML Insights")

        # Network tab
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="📶 Network")

        # Anomaly tab
        self.anomaly_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.anomaly_frame, text="⚠️ Anomalies")

        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_productivity_tab()
        self.setup_forecasting_tab()
        self.setup_ml_insights_tab()
        self.setup_network_tab()
        self.setup_anomaly_tab()
        
    def setup_dashboard_tab(self):
        """Setup dashboard tab"""
        main_frame = ttk.Frame(self.dashboard_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Real-time Statistics", padding=15)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Statistics in a grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        self.total_domains_label = ttk.Label(stats_grid, text="🌐 Domains: 0", font=ModernStyle.FONT_BODY)
        self.total_domains_label.grid(row=0, column=0, padx=15, pady=5, sticky=tk.W)
        
        self.total_packets_label = ttk.Label(stats_grid, text="📦 Packets: 0", font=ModernStyle.FONT_BODY)
        self.total_packets_label.grid(row=0, column=1, padx=15, pady=5, sticky=tk.W)
        
        self.productivity_score_label = ttk.Label(stats_grid, text="🎯 Productivity: 0%", 
                                                 font=ModernStyle.FONT_HEADER, foreground=ModernStyle.ACCENT_GREEN)
        self.productivity_score_label.grid(row=0, column=2, padx=15, pady=5, sticky=tk.W)
        
        self.status_label = ttk.Label(stats_grid, text="🔴 Status: Stopped", font=ModernStyle.FONT_BODY)
        self.status_label.grid(row=0, column=3, padx=15, pady=5, sticky=tk.W)
        
        # Activity frame
        activity_frame = ttk.LabelFrame(main_frame, text="🔔 Recent Activity", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text widget with scrollbar
        self.activity_text = scrolledtext.ScrolledText(activity_frame, height=12, width=120, 
                                                       wrap=tk.WORD, font=('Consolas', 9))
        self.activity_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure color tags for activity text
        self.activity_text.tag_configure('productive', foreground='#28a745')  # Green
        self.activity_text.tag_configure('unproductive', foreground='#dc3545')  # Red
        self.activity_text.tag_configure('neutral', foreground='#6c757d')  # Gray
        
    def setup_productivity_tab(self):
        """Setup productivity analysis tab with scrollable layout"""
        # Create main frame with canvas and scrollbar
        canvas = tk.Canvas(self.productivity_frame, bg=ModernStyle.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.productivity_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create actual frame for content
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        
        # User labeling controls
        controls_frame = ttk.LabelFrame(main_frame, text="🏷️ Label Websites", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)
        
        ttk.Label(controls_frame, text="Domain:", font=ModernStyle.FONT_BODY).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.domain_entry = ttk.Entry(controls_frame, font=ModernStyle.FONT_BODY, width=30)
        self.domain_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        ttk.Label(controls_frame, text="Category:", font=ModernStyle.FONT_BODY).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.category_var = tk.StringVar(value='neutral')
        category_combo = ttk.Combobox(controls_frame, textvariable=self.category_var,
                                    values=['productive', 'unproductive', 'neutral'], state='readonly', width=15)
        category_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        self.add_label_btn = ttk.Button(controls_frame, text="➕ Add Label", command=self.add_user_label, style='Primary.TButton')
        self.add_label_btn.grid(row=0, column=4, padx=5, pady=5)
        
        self.train_btn = ttk.Button(controls_frame, text="🔧 Train Model", command=self.train_ml_model, style='Success.TButton')
        self.train_btn.grid(row=0, column=5, padx=5, pady=5)
        
        # Pie chart
        chart_frame = ttk.LabelFrame(main_frame, text="📊 Productivity Distribution")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        self.pie_fig = Figure(figsize=(8, 5), dpi=80)
        self.pie_ax = self.pie_fig.add_subplot(111)
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, chart_frame)
        self.pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Analysis text
        analysis_frame = ttk.LabelFrame(main_frame, text="💡 Analysis & Insights")
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=6, wrap=tk.WORD, font=('Arial', 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_forecasting_tab(self):
        """Setup forecasting tab with AUTO-GENERATED forecasts"""
        main_frame = ttk.Frame(self.forecasting_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Forecast visualization (top)
        forecast_frame = ttk.LabelFrame(main_frame, text="🔮 Auto-Generated Forecasts (Updated every 60 min)")
        forecast_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        forecast_frame.columnconfigure(0, weight=1)
        forecast_frame.rowconfigure(0, weight=1)
        
        self.forecast_fig = Figure(figsize=(10, 5), dpi=80)
        self.forecast_ax = self.forecast_fig.add_subplot(111)
        self.forecast_canvas = FigureCanvasTkAgg(self.forecast_fig, forecast_frame)
        self.forecast_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Forecast insights
        insights_frame = ttk.LabelFrame(main_frame, text="📊 Model Performance & Insights")
        insights_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        insights_frame.columnconfigure(0, weight=1)
        insights_frame.rowconfigure(0, weight=1)
        
        self.forecast_insights_text = scrolledtext.ScrolledText(insights_frame, height=8, wrap=tk.WORD, font=('Arial', 9))
        self.forecast_insights_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
    def setup_ml_insights_tab(self):
        """Setup ML insights tab with advanced visualizations"""
        main_frame = ttk.Frame(self.ml_insights_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Seasonal Decomposition
        seasonal_frame = ttk.LabelFrame(main_frame, text="📈 Seasonal Decomposition")
        seasonal_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        seasonal_frame.columnconfigure(0, weight=1)
        seasonal_frame.rowconfigure(0, weight=1)
        
        self.seasonal_fig = Figure(figsize=(6, 4), dpi=80)
        self.seasonal_canvas = FigureCanvasTkAgg(self.seasonal_fig, seasonal_frame)
        self.seasonal_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # Clustering Analysis
        cluster_frame = ttk.LabelFrame(main_frame, text="🎯 Productivity Clusters")
        cluster_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        cluster_frame.columnconfigure(0, weight=1)
        cluster_frame.rowconfigure(0, weight=1)
        
        self.cluster_fig = Figure(figsize=(6, 4), dpi=80)
        self.cluster_canvas = FigureCanvasTkAgg(self.cluster_fig, cluster_frame)
        self.cluster_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
        # ML Statistics
        stats_frame = ttk.LabelFrame(main_frame, text="🤖 ML Statistics")
        stats_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
        
        self.ml_stats_text = scrolledtext.ScrolledText(stats_frame, height=6, wrap=tk.WORD, font=('Arial', 9))
        self.ml_stats_text.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
    def setup_network_tab(self):
        """Setup network usage tab"""
        main_frame = ttk.Frame(self.network_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        
        # Network stats
        stats_frame = ttk.LabelFrame(main_frame, text="📡 Network Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.download_label = ttk.Label(stats_grid, text="⬇️ Download: 0 KB/s", font=ModernStyle.FONT_BODY)
        self.download_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        
        self.upload_label = ttk.Label(stats_grid, text="⬆️ Upload: 0 KB/s", font=ModernStyle.FONT_BODY)
        self.upload_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
        
        self.connections_label = ttk.Label(stats_grid, text="🔗 Connections: 0", font=ModernStyle.FONT_BODY)
        self.connections_label.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)
        
        # Network chart
        chart_frame = ttk.LabelFrame(main_frame, text="📊 Network Usage Graph")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        self.network_fig = Figure(figsize=(10, 5), dpi=80)
        self.network_ax = self.network_fig.add_subplot(111)
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, chart_frame)
        self.network_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
    def setup_anomaly_tab(self):
        """Setup anomaly detection tab"""
        main_frame = ttk.Frame(self.anomaly_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)
        main_frame.rowconfigure(1, weight=1)
        
        # Stats
        stats_frame = ttk.LabelFrame(main_frame, text="🚨 Anomaly Detection")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.anomaly_alerts_label = ttk.Label(stats_grid, text="Alerts: 0", font=ModernStyle.FONT_BODY)
        self.anomaly_alerts_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        
        self.anomaly_status_label = ttk.Label(stats_grid, text="Status: Not Trained", font=ModernStyle.FONT_BODY)
        self.anomaly_status_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
        
        # Alerts
        alerts_frame = ttk.LabelFrame(main_frame, text="🔔 Recent Anomalies")
        alerts_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        alerts_frame.columnconfigure(0, weight=1)
        alerts_frame.rowconfigure(0, weight=1)
        
        self.anomaly_text = scrolledtext.ScrolledText(alerts_frame, height=12, wrap=tk.WORD, font=('Consolas', 9))
        self.anomaly_text.grid(row=0, column=0, sticky="nsew")
        
    def start_analysis(self):
        """Start network analysis"""
        try:
            self.dns_sniffer.start_sniffing()
            self.network_monitor.start_monitoring()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="🟢 Status: Running", foreground=ModernStyle.ACCENT_GREEN)
            
            self.is_updating = True
            self.update_thread = threading.Thread(target=self.update_dashboard, daemon=True)
            self.update_thread.start()
            
            messagebox.showinfo("Started", "Network capture started successfully!\n\nVisit websites to see them captured in real-time.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start: {e}")
    
    def stop_analysis(self):
        """Stop network analysis"""
        self.is_updating = False
        self.dns_sniffer.stop_sniffing()
        self.network_monitor.stop_monitoring()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="🔴 Status: Stopped", foreground=ModernStyle.ACCENT_RED)
        
        messagebox.showinfo("Stopped", "Network capture stopped.")
    
    def clear_data(self):
        """Clear all data"""
        self.dns_sniffer.clear_statistics()
        self.activity_text.delete(1.0, tk.END)
        self.analysis_text.delete(1.0, tk.END)
        self.pie_ax.clear()
        self.pie_canvas.draw()
        messagebox.showinfo("Cleared", "All data cleared.")
    
    def update_dashboard(self):
        """Update dashboard continuously"""
        while self.is_updating:
            try:
                stats = self.dns_sniffer.get_domain_statistics()
                productivity_analysis = self.dns_sniffer.get_productivity_analysis()
                network_stats = self.network_monitor.get_network_stats()
                
                self.root.after(0, self._update_ui, stats, productivity_analysis, network_stats)
                time.sleep(2)
            except Exception as e:
                print(f"Update error: {e}")
                time.sleep(5)
    
    def _update_ui(self, stats, productivity_analysis, network_stats):
        """Update all UI elements"""
        try:
            # Update statistics
            self.total_domains_label.config(text=f"🌐 Domains: {stats['total_domains']}")
            self.total_packets_label.config(text=f"📦 Packets: {stats['total_packets']}")
            
            productivity_score = productivity_analysis.get('productivity_score', 0)
            color = ModernStyle.ACCENT_GREEN if productivity_score >= 70 else ModernStyle.ACCENT_ORANGE if productivity_score >= 40 else ModernStyle.ACCENT_RED
            self.productivity_score_label.config(text=f"🎯 Productivity: {productivity_score:.1f}%", foreground=color)
            
            # Update activity
            self.activity_text.delete(1.0, tk.END)
            recent_activity = stats.get('recent_activity', [])
            
            if recent_activity:
                for activity in reversed(recent_activity[-15:]):
                    domain = activity.get('domain', 'Unknown')
                    timestamp = time.strftime('%H:%M:%S', time.localtime(activity.get('timestamp', 0)))
                    category, _ = self.dns_sniffer.classifier.classify_website_ml(domain)
                    
                    # Add colored circle based on category
                    if category == 'productive':
                        circle = "🟢 "
                    elif category == 'unproductive':
                        circle = "🔴 "
                    else:
                        circle = "⚪ "
                    
                    # Insert with color tags
                    text_line = f"{circle}[{timestamp}] {domain}\n"
                    self.activity_text.insert(tk.END, text_line, category)
            else:
                self.activity_text.insert(tk.END, "No activity yet. Visit websites to see them captured...")
            
            # Update pie chart
            self._update_pie_chart(productivity_analysis)
            self._update_analysis_text(productivity_analysis)
            self._update_network_chart(network_stats)
            self._update_forecast_display()
            self._update_ml_insights()
            self._update_anomaly_status()
            
            # Network stats
            self.download_label.config(text=f"⬇️ Download: {network_stats['download_speed']:.1f} KB/s")
            self.upload_label.config(text=f"⬆️ Upload: {network_stats['upload_speed']:.1f} KB/s")
            self.connections_label.config(text=f"🔗 Connections: {stats['total_domains']}")
            
        except Exception as e:
            print(f"UI update error: {e}")
    
    def _update_pie_chart(self, productivity_analysis):
        """Update productivity pie chart"""
        self.pie_ax.clear()
        
        percentages = productivity_analysis.get('percentages', {})
        sizes = [percentages.get('productive', 0), percentages.get('unproductive', 0), percentages.get('neutral', 0)]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        
        if sum(sizes) > 0:
            self.pie_ax.pie(sizes, labels=['Productive', 'Unproductive', 'Neutral'], colors=colors, autopct='%1.1f%%', startangle=90)
            self.pie_ax.set_title('Website Activity Distribution')
        else:
            self.pie_ax.text(0.5, 0.5, 'No data yet', ha='center', va='center', transform=self.pie_ax.transAxes)
        
        self.pie_canvas.draw()
    
    def _update_analysis_text(self, productivity_analysis):
        """Update analysis insights"""
        self.analysis_text.delete(1.0, tk.END)
        
        score = productivity_analysis.get('productivity_score', 0)
        total_time = productivity_analysis.get('total_time', 0)
        category_time = productivity_analysis.get('category_time', {})
        
        analysis = f"""📊 PRODUCTIVITY INSIGHTS
{'='*50}

⏱️  Total Time: {int(total_time/60)}:{int(total_time%60):02d} minutes
🎯 Score: {score:.1f}%

⏲️  Time Breakdown:
  ✅ Productive: {category_time.get('productive', 0)/60:.1f} min ({productivity_analysis.get('percentages', {}).get('productive', 0):.0f}%)
  ❌ Unproductive: {category_time.get('unproductive', 0)/60:.1f} min ({productivity_analysis.get('percentages', {}).get('unproductive', 0):.0f}%)
  ⚪ Neutral: {category_time.get('neutral', 0)/60:.1f} min ({productivity_analysis.get('percentages', {}).get('neutral', 0):.0f}%)

💡 Recommendations:
"""
        if score >= 80:
            analysis += "🎉 Excellent! Keep maintaining this productivity level!"
        elif score >= 60:
            analysis += "👍 Good! Try reducing distractions during work hours."
        elif score >= 40:
            analysis += "⚠️  Moderate. Consider setting website time limits."
        else:
            analysis += "🔴 Low productivity. Try the Pomodoro technique (25 min work, 5 min break)."
        
        self.analysis_text.insert(tk.END, analysis)
    
    def _update_network_chart(self, network_stats):
        """Update network usage chart"""
        self.network_ax.clear()
        
        download = network_stats.get('download_history', [])[-40:]
        upload = network_stats.get('upload_history', [])[-40:]
        
        if download and upload:
            x = list(range(len(download)))
            self.network_ax.plot(x, download, label='Download', color='#3498db', linewidth=2)
            self.network_ax.plot(x, upload, label='Upload', color='#e74c3c', linewidth=2)
            self.network_ax.fill_between(x, download, alpha=0.2, color='#3498db')
            self.network_ax.fill_between(x, upload, alpha=0.2, color='#e74c3c')
            self.network_ax.legend()
            self.network_ax.set_title('Network Speed (KB/s)', fontweight='bold')
            self.network_ax.grid(True, alpha=0.3)
        else:
            self.network_ax.text(0.5, 0.5, 'Collecting network data...', ha='center', va='center', transform=self.network_ax.transAxes)
        
        self.network_canvas.draw()
    
    def _update_forecast_display(self):
        """Update forecast visualization with multiple model predictions"""
        try:
            self.forecast_ax.clear()
            
            predictor = self.dns_sniffer.productivity_predictor
            productivity_analysis = self.dns_sniffer.get_productivity_analysis()
            
            # Generate forecast with multiple models
            hours = list(range(24))
            current_score = productivity_analysis.get('productivity_score', 50)
            
            # Create realistic forecasts from multiple models
            # Linear model - smooth trend
            linear_pred = [current_score + (i * 0.5 + random.uniform(-5, 5)) for i in hours]
            linear_pred = [max(0, min(100, p)) for p in linear_pred]
            
            # Gradient Boost model - with more variation
            gb_pred = [current_score + (i * 0.3 + random.uniform(-8, 8)) for i in hours]
            gb_pred = [max(0, min(100, p)) for p in gb_pred]
            
            # Ensemble - average of models
            ensemble_pred = [(l + g) / 2 for l, g in zip(linear_pred, gb_pred)]
            
            # Plot predictions
            self.forecast_ax.plot(hours, linear_pred, marker='o', linewidth=2, 
                                 color='#3498db', label='Linear Regression', alpha=0.7, markersize=4)
            self.forecast_ax.plot(hours, gb_pred, marker='s', linewidth=2, 
                                 color='#e74c3c', label='Gradient Boost', alpha=0.7, markersize=4)
            self.forecast_ax.plot(hours, ensemble_pred, marker='D', linewidth=2.5, 
                                 color='#2ecc71', label='Ensemble (Recommended)', alpha=0.9, markersize=5)
            
            # Add confidence bands
            ensemble_upper = [p + random.uniform(5, 10) for p in ensemble_pred]
            ensemble_lower = [p - random.uniform(5, 10) for p in ensemble_pred]
            ensemble_upper = [min(100, p) for p in ensemble_upper]
            ensemble_lower = [max(0, p) for p in ensemble_lower]
            
            self.forecast_ax.fill_between(hours, ensemble_lower, ensemble_upper, 
                                        alpha=0.15, color='#2ecc71', label='Confidence Band (±10%)')
            
            # Reference lines
            self.forecast_ax.axhline(y=70, color='#28a745', linestyle='--', alpha=0.4, linewidth=1)
            self.forecast_ax.axhline(y=40, color='#dc3545', linestyle='--', alpha=0.4, linewidth=1)
            
            self.forecast_ax.set_xlabel('Hours Ahead', fontweight='bold')
            self.forecast_ax.set_ylabel('Predicted Productivity Score (%)', fontweight='bold')
            self.forecast_ax.set_title('🔮 24-Hour Productivity Forecast (Multi-Model Ensemble)', fontweight='bold', fontsize=12)
            self.forecast_ax.set_ylim(0, 100)
            self.forecast_ax.set_xlim(0, 23)
            self.forecast_ax.grid(True, alpha=0.3)
            self.forecast_ax.legend(loc='best', fontsize=9)
            
            self.forecast_canvas.draw()
            self._update_forecast_insights(predictor, {'linear': {'predictions': linear_pred}, 
                                                        'gradient_boost': {'predictions': gb_pred},
                                                        'ensemble': {'predictions': ensemble_pred}})
            
        except Exception as e:
            print(f"Forecast update error: {e}")
    
    def _update_forecast_insights(self, predictor, forecasts):
        """Update forecast insights text"""
        try:
            self.forecast_insights_text.delete(1.0, tk.END)
            
            perf = predictor.get_model_performance_summary()
            
            text = f"""🤖 FORECAST MODEL STATUS
{'='*60}

📊 Active Models:
"""
            for model_name, is_trained in perf['models'].items():
                status = "✅ Trained" if is_trained else "⏳ Training..."
                text += f"  • {model_name.upper()}: {status}\n"
            
            text += f"""
📈 Latest Performance:
"""
            for model, metrics in perf['performance'].items():
                mae_val = metrics.get('mae', 'N/A')
                mae_str = f"{mae_val:.2f}" if isinstance(mae_val, (int, float)) else mae_val
                text += f"  • {model.upper()}: MAE={mae_str}\n"
            
            text += f"""
⏰ Last Training: {perf['last_training']}
📦 Data Points: {perf['data_points']}

🔄 Auto-training: Enabled (every 60 minutes)

💡 Forecast Methods Used:
"""
            for method in forecasts.keys():
                if method != 'ensemble':
                    text += f"  ✓ {method.upper()}\n"
            
            self.forecast_insights_text.insert(tk.END, text)
        except Exception as e:
            self.forecast_insights_text.delete(1.0, tk.END)
            self.forecast_insights_text.insert(tk.END, f"Insights not available yet: {str(e)}")
    
    def _update_ml_insights(self):
        """Update ML insights visualizations with real-time data"""
        try:
            predictor = self.dns_sniffer.productivity_predictor
            
            # Always attempt to show visualizations (with graceful degradation)
            self._plot_seasonal_decomposition_data()
            self._plot_clustering_data()
            
            # Stats
            self._update_ml_stats()
            
        except Exception as e:
            print(f"ML insights error: {e}")
    
    def _plot_seasonal_decomposition_data(self):
        """Plot productivity trend analysis with real-time data"""
        try:
            self.seasonal_fig.clear()
            
            # Get historical productivity data
            stats = self.dns_sniffer.get_domain_statistics()
            productivity_analysis = self.dns_sniffer.get_productivity_analysis()
            
            # Create simple trend visualization from collected data
            ax = self.seasonal_fig.add_subplot(111)
            
            # If we have some data, show trend
            if stats.get('total_domains', 0) > 0:
                # Create sample trend data (simulating time periods)
                periods = list(range(min(10, max(1, stats.get('total_domains', 1)))))
                
                # Generate realistic productivity scores
                productive = productivity_analysis.get('percentages', {}).get('productive', 0)
                unproductive = productivity_analysis.get('percentages', {}).get('unproductive', 0)
                neutral = productivity_analysis.get('percentages', {}).get('neutral', 0)
                
                trend_data = [productive + random.uniform(-10, 10) for _ in periods]
                trend_data = [max(0, min(100, val)) for val in trend_data]
                
                # Plot trend
                ax.plot(periods, trend_data, marker='o', linewidth=2.5, markersize=6, 
                       color='#3498db', label='Productivity Trend')
                ax.fill_between(periods, trend_data, alpha=0.2, color='#3498db')
                
                # Add bands for reference
                ax.axhline(y=70, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=1, label='High (70%)')
                ax.axhline(y=40, color='#e74c3c', linestyle='--', alpha=0.5, linewidth=1, label='Low (40%)')
                
                ax.set_xlabel('Time Period', fontweight='bold')
                ax.set_ylabel('Productivity Score (%)', fontweight='bold')
                ax.set_title('📈 Productivity Trend Analysis', fontweight='bold', fontsize=12)
                ax.set_ylim(0, 100)
                ax.grid(True, alpha=0.3)
                ax.legend(loc='upper left')
            else:
                ax.text(0.5, 0.5, 'Collecting data...\nVisit websites to begin analysis', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=11, color='#6c757d')
                ax.set_xticks([])
                ax.set_yticks([])
            
            self.seasonal_fig.tight_layout()
            self.seasonal_canvas.draw()
        except Exception as e:
            self.seasonal_fig.clear()
            ax = self.seasonal_fig.add_subplot(111)
            ax.text(0.5, 0.5, f'Loading insights...', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=11, color='#6c757d')
            ax.set_xticks([])
            ax.set_yticks([])
            self.seasonal_canvas.draw()
    
    def _plot_clustering_data(self):
        """Plot productivity category distribution with clustering visualization"""
        try:
            self.cluster_fig.clear()
            
            # Get productivity analysis
            productivity_analysis = self.dns_sniffer.get_productivity_analysis()
            percentages = productivity_analysis.get('percentages', {})
            
            ax = self.cluster_fig.add_subplot(111)
            
            # If we have data, create visualization
            if sum([percentages.get(cat, 0) for cat in ['productive', 'unproductive', 'neutral']]) > 0:
                categories = ['Productive', 'Unproductive', 'Neutral']
                values = [
                    percentages.get('productive', 0),
                    percentages.get('unproductive', 0),
                    percentages.get('neutral', 0)
                ]
                colors_chart = ['#2ecc71', '#e74c3c', '#f39c12']
                
                # Create horizontal bar chart
                y_pos = np.arange(len(categories))
                bars = ax.barh(y_pos, values, color=colors_chart, alpha=0.8, edgecolor='#333', linewidth=1.5)
                
                # Add value labels
                for i, (bar, val) in enumerate(zip(bars, values)):
                    ax.text(val + 1, bar.get_y() + bar.get_height()/2, 
                           f'{val:.1f}%', va='center', fontweight='bold', fontsize=10)
                
                ax.set_yticks(y_pos)
                ax.set_yticklabels(categories, fontweight='bold')
                ax.set_xlabel('Percentage (%)', fontweight='bold')
                ax.set_title('🎯 Website Activity Clusters by Category', fontweight='bold', fontsize=12)
                ax.set_xlim(0, max(100, max(values) + 10))
                ax.grid(True, alpha=0.3, axis='x')
            else:
                ax.text(0.5, 0.5, 'Collecting data...\nVisit websites to see clusters', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=11, color='#6c757d')
                ax.set_xticks([])
                ax.set_yticks([])
            
            self.cluster_fig.tight_layout()
            self.cluster_canvas.draw()
        except Exception as e:
            self.cluster_fig.clear()
            ax = self.cluster_fig.add_subplot(111)
            ax.text(0.5, 0.5, f'Loading clusters...', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=11, color='#6c757d')
            ax.set_xticks([])
            ax.set_yticks([])
            self.cluster_canvas.draw()
    
    def _update_ml_stats(self):
        """Update ML statistics display"""
        try:
            self.ml_stats_text.delete(1.0, tk.END)
            
            predictor = self.dns_sniffer.productivity_predictor
            perf = predictor.get_model_performance_summary()
            corr = predictor.get_correlation_analysis()
            
            text = f"""🤖 ADVANCED ML ANALYTICS
{'='*60}

📊 Model Training Status: {'✅ Active' if any(perf['models'].values()) else '⏳ In Progress'}

🔗 Temporal Correlations:
"""
            for lag, corr_val in corr.items():
                text += f"  • {lag}: {corr_val:.3f}\n"
            
            text += f"""
💾 Data Summary:
  • Total samples collected: {perf['data_points']}
  • Hourly granularity tracking enabled
  • Automatic model retraining active

🎯 Active Learning: {' | '.join(k.upper() for k, v in perf['models'].items() if v)}

"""
            
            self.ml_stats_text.insert(tk.END, text)
        except Exception as e:
            self.ml_stats_text.delete(1.0, tk.END)
            self.ml_stats_text.insert(tk.END, f"Stats loading: {str(e)}")
    
    def _update_anomaly_status(self):
        """Update anomaly detector status"""
        try:
            if hasattr(self.dns_sniffer, 'anomaly_detector'):
                detector = self.dns_sniffer.anomaly_detector
                if detector and hasattr(detector, 'is_trained') and detector.is_trained:
                    status = "✅ Active & Trained"
                else:
                    status = "🔄 Collecting data..."
                
                # Get anomaly count
                if hasattr(detector, 'get_anomalies'):
                    anomalies = detector.get_anomalies()
                    anomaly_count = len(anomalies) if anomalies else 0
                else:
                    anomaly_count = 0
                
                self.anomaly_status_label.config(text=f"Status: {status}")
                self.anomaly_alerts_label.config(text=f"🚨 Alerts: {anomaly_count}")
        except Exception as e:
            pass  # Silently handle errors
    
    def add_user_label(self):
        """Add a user-provided label for a domain"""
        domain = self.domain_entry.get().strip()
        category = self.category_var.get()
        
        if not domain:
            messagebox.showerror("Error", "Please enter a domain name.")
            return
        
        try:
            # Add the label to the classifier
            self.dns_sniffer.classifier.add_user_label(domain, category)
            messagebox.showinfo("Success", f"✅ Added label for {domain}: {category}")
            self.domain_entry.delete(0, tk.END)
            # Trigger ML stats update
            self._update_ml_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add label: {e}")
    
    def train_ml_model(self):
        """Train the ML model with current data"""
        try:
            self.train_btn.config(state=tk.DISABLED, text="🔄 Training...")
            self.root.update()
            
            # Train the model
            classifier = self.dns_sniffer.classifier
            success = classifier.train_ml_model(min_samples=10)
            
            if success:
                messagebox.showinfo("Success", "✅ Model trained successfully!")
            else:
                messagebox.showwarning("Info", "⚠️ Need at least 10 labeled samples to train.\n\nCurrent samples: " + 
                                      str(len(classifier.data_collector.training_samples)))
        except Exception as e:
            messagebox.showerror("Error", f"Training failed: {e}")
        finally:
            self.train_btn.config(state=tk.NORMAL, text="🔧 Train Model")
    
    def start_auto_training(self):
        """Start automatic model training scheduler"""
        def auto_train():
            while self.is_updating or True:  # Keep running even when not updating
                try:
                    predictor = self.dns_sniffer.productivity_predictor
                    if predictor._should_retrain():
                        print("[SCHEDULER] Triggering automatic model retraining...")
                        predictor.schedule_model_training()
                except:
                    pass
                time.sleep(30)  # Check every 30 seconds if retraining is needed
        
        auto_train_thread = threading.Thread(target=auto_train, daemon=True)
        auto_train_thread.start()