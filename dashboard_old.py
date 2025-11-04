import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
import pandas as pd
from website_classifier import WebsiteClassifier
import random

# Modern UI styling
class ModernStyle:
    """Modern UI styling constants - Light Theme"""
    BG_DARK = '#ffffff'  # Pure white background
    BG_MEDIUM = '#f8f9fa'  # Light gray for cards
    BG_LIGHT = '#e9ecef'  # Lighter gray for headers
    FG_LIGHT = '#212529'  # Dark text for contrast
    FG_MEDIUM = '#6c757d'  # Medium gray text
    FG_DARK = '#495057'  # Darker gray text
    ACCENT_BLUE = '#007bff'  # Modern blue
    ACCENT_GREEN = '#28a745'  # Success green
    ACCENT_ORANGE = '#fd7e14'  # Warning orange
    ACCENT_RED = '#dc3545'  # Error red
    BORDER_COLOR = '#dee2e6'  # Light border

    FONT_TITLE = ('Segoe UI', 16, 'bold')
    FONT_HEADER = ('Segoe UI', 12, 'bold')
    FONT_BODY = ('Segoe UI', 10)
    FONT_SMALL = ('Segoe UI', 9)

    @staticmethod
    def apply_theme(root):
        """Apply modern light theme to the application"""
        style = ttk.Style()

        # Configure overall theme
        style.theme_use('default')

        # Frame styling
        style.configure('TFrame', background=ModernStyle.BG_DARK)
        style.configure('Card.TFrame', background=ModernStyle.BG_MEDIUM, relief='raised', borderwidth=1)
        style.configure('Header.TFrame', background=ModernStyle.BG_LIGHT)

        # Label styling
        style.configure('TLabel', background=ModernStyle.BG_DARK, foreground=ModernStyle.FG_LIGHT, font=ModernStyle.FONT_BODY)
        style.configure('Title.TLabel', font=ModernStyle.FONT_TITLE, foreground=ModernStyle.ACCENT_BLUE)
        style.configure('Header.TLabel', font=ModernStyle.FONT_HEADER, foreground=ModernStyle.FG_LIGHT)
        style.configure('Status.TLabel', font=ModernStyle.FONT_SMALL, foreground=ModernStyle.FG_MEDIUM)

        # Button styling
        style.configure('TButton', font=ModernStyle.FONT_BODY, padding=8, relief='flat')
        style.map('TButton',
                 background=[('active', ModernStyle.ACCENT_BLUE),
                           ('pressed', ModernStyle.BG_LIGHT)])
        style.configure('Primary.TButton', background=ModernStyle.ACCENT_BLUE, foreground=ModernStyle.BG_DARK)
        style.configure('Success.TButton', background=ModernStyle.ACCENT_GREEN, foreground=ModernStyle.BG_DARK)
        style.configure('Danger.TButton', background=ModernStyle.ACCENT_RED, foreground=ModernStyle.BG_DARK)

        # Entry styling
        style.configure('TEntry', font=ModernStyle.FONT_BODY, fieldbackground=ModernStyle.BG_DARK,
                       bordercolor=ModernStyle.BORDER_COLOR, lightcolor=ModernStyle.BORDER_COLOR,
                       darkcolor=ModernStyle.BORDER_COLOR)

        # Combobox styling
        style.configure('TCombobox', font=ModernStyle.FONT_BODY, fieldbackground=ModernStyle.BG_DARK)

        # Notebook styling
        style.configure('TNotebook', background=ModernStyle.BG_DARK, tabmargins=[2, 5, 2, 0])
        style.configure('TNotebook.Tab', background=ModernStyle.BG_MEDIUM, foreground=ModernStyle.FG_LIGHT,
                       font=ModernStyle.FONT_BODY, padding=[10, 5], relief='flat')
        style.map('TNotebook.Tab',
                 background=[('selected', ModernStyle.ACCENT_BLUE),
                           ('active', ModernStyle.BG_LIGHT)],
                 foreground=[('selected', ModernStyle.BG_DARK)])

        # LabelFrame styling
        style.configure('Card.TLabelframe', background=ModernStyle.BG_MEDIUM, foreground=ModernStyle.FG_LIGHT,
                       font=ModernStyle.FONT_HEADER, bordercolor=ModernStyle.BORDER_COLOR)
        style.configure('Card.TLabelframe.Label', background=ModernStyle.BG_MEDIUM, foreground=ModernStyle.ACCENT_BLUE,
                       font=ModernStyle.FONT_HEADER)

        # Scrollbar styling
        style.configure('TScrollbar', background=ModernStyle.BG_MEDIUM, troughcolor=ModernStyle.BG_LIGHT,
                       bordercolor=ModernStyle.BORDER_COLOR, arrowcolor=ModernStyle.FG_DARK)

        # Apply to root window
        root.configure(bg=ModernStyle.BG_DARK)
        root.option_add('*TCombobox*Listbox.background', ModernStyle.BG_DARK)
        root.option_add('*TCombobox*Listbox.foreground', ModernStyle.FG_LIGHT)
        root.option_add('*TCombobox*Listbox.selectBackground', ModernStyle.ACCENT_BLUE)
        root.option_add('*TCombobox*Listbox.selectForeground', ModernStyle.BG_DARK)

class NetworkAnalyzerDashboard:
    def __init__(self, root, dns_sniffer, network_monitor):
        self.root = root
        self.dns_sniffer = dns_sniffer
        self.network_monitor = network_monitor
        
        self.setup_ui()
        self.is_updating = False
        self.update_thread = None
        
    def setup_ui(self):
        """Setup the main UI"""
        # Apply modern theme
        ModernStyle.apply_theme(self.root)

        self.root.title("NetSense - Advanced Network Productivity Analyzer")
        self.root.geometry("1200x800")

        # Create main frame
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header
        header_frame = ttk.Frame(main_frame, style='Header.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = ttk.Label(header_frame, text="🚀 NetSense", style='Title.TLabel')
        self.title_label.pack(side=tk.LEFT)

        # Subtitle
        subtitle_label = ttk.Label(header_frame, text="Advanced Network Productivity Analyzer",
                                 style='Header.TLabel', foreground=ModernStyle.ACCENT_BLUE)
        subtitle_label.pack(side=tk.LEFT, padx=(10, 0))

        # Control buttons
        control_frame = ttk.Frame(header_frame, style='Header.TFrame')
        control_frame.pack(side=tk.RIGHT)

        self.start_btn = ttk.Button(control_frame, text="▶️ Start Analysis",
                                  command=self.start_analysis, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="⏹️ Stop Analysis",
                                 command=self.stop_analysis, state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear Data",
                                  command=self.clear_data, style='TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        
        # Productivity tab
        self.productivity_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.productivity_frame, text="Productivity Analysis")

        # ML Training tab
        self.ml_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ml_frame, text="ML Training")

        # Network tab
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="Network Usage")

        # Anomaly tab
        self.anomaly_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.anomaly_frame, text="Anomaly Detection")

        # Forecasting tab
        self.forecasting_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.forecasting_frame, text="Productivity Forecast")

        # Content Analysis tab
        self.content_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.content_frame, text="Content Analysis")

        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_productivity_tab()
        self.setup_ml_tab()
        self.setup_network_tab()
        self.setup_anomaly_tab()
        self.setup_forecasting_tab()
        self.setup_content_tab()
        
    def setup_dashboard_tab(self):
        """Setup dashboard tab with better layout"""
        # Main frame
        main_frame = ttk.Frame(self.dashboard_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Stats frame - fixed height
        main_frame.rowconfigure(1, weight=1)  # Activity frame - expands
        
        # Stats frame - TOP
        stats_frame = ttk.LabelFrame(main_frame, text="Real-time Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Statistics labels in a grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)
        
        self.total_domains_label = ttk.Label(stats_grid, text="Domains Tracked: 0", font=('Arial', 10))
        self.total_domains_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        
        self.total_packets_label = ttk.Label(stats_grid, text="Packets Captured: 0", font=('Arial', 10))
        self.total_packets_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
        
        self.productivity_score_label = ttk.Label(stats_grid, text="Productivity Score: 0%", font=('Arial', 10, 'bold'))
        self.productivity_score_label.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)
        
        # Status indicator
        self.status_label = ttk.Label(stats_grid, text="Status: Stopped", font=('Arial', 10))
        self.status_label.grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)
        
        # Recent activity - BOTTOM (expands)
        activity_frame = ttk.LabelFrame(main_frame, text="Recent Activity")
        activity_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        activity_frame.columnconfigure(0, weight=1)
        activity_frame.rowconfigure(0, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(activity_frame)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.activity_text = tk.Text(text_frame, height=15, width=100, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.activity_text.yview)
        self.activity_text.configure(yscrollcommand=scrollbar.set)
        
        self.activity_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
    def setup_productivity_tab(self):
        """Setup productivity analysis tab with better layout"""
        # Main frame with proper weight distribution
        main_frame = ttk.Frame(self.productivity_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights for proper resizing
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3)  # Chart gets more space
        main_frame.rowconfigure(1, weight=1)  # Analysis gets less space
        
        # Pie chart frame - TOP
        chart_frame = ttk.LabelFrame(main_frame, text="Productivity Distribution")
        chart_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure with smaller size
        self.pie_fig = Figure(figsize=(6, 4), dpi=80)  # Smaller figure
        self.pie_ax = self.pie_fig.add_subplot(111)
        
        # Create canvas
        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, chart_frame)
        self.pie_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Analysis frame - BOTTOM
        analysis_frame = ttk.LabelFrame(main_frame, text="Productivity Analysis")
        analysis_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
        
        # Use a frame with text and scrollbar
        text_frame = ttk.Frame(analysis_frame)
        text_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.analysis_text = tk.Text(text_frame, height=6, width=80, wrap=tk.WORD, font=('Arial', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def setup_ml_tab(self):
        """Setup ML training tab"""
        # Main frame
        main_frame = ttk.Frame(self.ml_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Controls frame
        main_frame.rowconfigure(1, weight=1)  # Content frame

        # Controls frame - TOP
        controls_frame = ttk.LabelFrame(main_frame, text="ML Training Controls")
        controls_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Controls grid
        controls_grid = ttk.Frame(controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=10)

        # Domain input
        ttk.Label(controls_grid, text="Domain:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.domain_entry = ttk.Entry(controls_grid, width=30)
        self.domain_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Category selection
        ttk.Label(controls_grid, text="Category:", font=('Arial', 10, 'bold')).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.category_var = tk.StringVar(value='neutral')
        category_combo = ttk.Combobox(controls_grid, textvariable=self.category_var,
                                    values=['productive', 'unproductive', 'neutral'], state='readonly', width=15)
        category_combo.grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        # Buttons
        self.add_label_btn = ttk.Button(controls_grid, text="Add Label", command=self.add_user_label)
        self.add_label_btn.grid(row=0, column=4, padx=5, pady=5)

        self.train_btn = ttk.Button(controls_grid, text="Train Model", command=self.train_ml_model)
        self.train_btn.grid(row=0, column=5, padx=5, pady=5)

        self.retrain_btn = ttk.Button(controls_grid, text="Retrain Model", command=self.retrain_model)
        self.retrain_btn.grid(row=0, column=6, padx=5, pady=5)

        # Content frame - BOTTOM (expands)
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Text widget for ML stats and training data
        self.ml_text = tk.Text(content_frame, height=20, width=100, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.ml_text.yview)
        self.ml_text.configure(yscrollcommand=scrollbar.set)

        self.ml_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Initial ML stats display
        self.update_ml_stats()

    def setup_network_tab(self):
        """Setup network usage tab"""
        # Main frame
        main_frame = ttk.Frame(self.network_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=3)  # Chart gets more space
        main_frame.rowconfigure(1, weight=0)  # Stats get fixed space
        
        # Network speed chart - TOP
        network_chart_frame = ttk.LabelFrame(main_frame, text="Network Usage Over Time")
        network_chart_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        network_chart_frame.columnconfigure(0, weight=1)
        network_chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure for network usage
        self.network_fig = Figure(figsize=(8, 4), dpi=80)
        self.network_ax = self.network_fig.add_subplot(111)
        
        # Create canvas
        self.network_canvas = FigureCanvasTkAgg(self.network_fig, network_chart_frame)
        self.network_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Current speeds frame - BOTTOM
        speed_frame = ttk.LabelFrame(main_frame, text="Current Network Statistics")
        speed_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        speed_grid = ttk.Frame(speed_frame)
        speed_grid.pack(fill=tk.X, padx=10, pady=10)
        
        # Upload speed
        upload_frame = ttk.Frame(speed_grid)
        upload_frame.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)
        ttk.Label(upload_frame, text="Upload Speed:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.upload_label = ttk.Label(upload_frame, text="0 KB/s", font=('Arial', 12, 'bold'), foreground='red')
        self.upload_label.pack(anchor=tk.W)
        
        # Download speed
        download_frame = ttk.Frame(speed_grid)
        download_frame.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)
        ttk.Label(download_frame, text="Download Speed:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.download_label = ttk.Label(download_frame, text="0 KB/s", font=('Arial', 12, 'bold'), foreground='blue')
        self.download_label.pack(anchor=tk.W)
        
        # Total data
        data_frame = ttk.Frame(speed_grid)
        data_frame.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)
        ttk.Label(data_frame, text="Active Connections:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.connections_label = ttk.Label(data_frame, text="0", font=('Arial', 12))
        self.connections_label.pack(anchor=tk.W)
        
    def start_analysis(self):
        """Start network analysis"""
        try:
            self.dns_sniffer.start_sniffing()
            self.network_monitor.start_monitoring()
            
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running")
            
            self.is_updating = True
            self.update_thread = threading.Thread(target=self.update_dashboard)
            self.update_thread.daemon = True
            self.update_thread.start()
            
            messagebox.showinfo("Success", "Network analysis started successfully!\n\nNow visit websites like:\n- youtube.com\n- instagram.com\n- github.com\n- netflix.com\n\nto see them captured in real-time.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start analysis: {e}")
    
    def stop_analysis(self):
        """Stop network analysis"""
        self.is_updating = False
        self.dns_sniffer.stop_sniffing()
        self.network_monitor.stop_monitoring()
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Status: Stopped")
        
        messagebox.showinfo("Stopped", "Network analysis stopped.")
    
    def clear_data(self):
        """Clear all collected data"""
        self.dns_sniffer.clear_statistics()
        self.activity_text.delete(1.0, tk.END)
        self.analysis_text.delete(1.0, tk.END)
        
        # Clear charts
        self.pie_ax.clear()
        self.pie_ax.text(0.5, 0.5, 'No data collected yet\nStart analysis to see charts', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.pie_ax.transAxes, fontsize=12)
        self.pie_ax.set_xticks([])
        self.pie_ax.set_yticks([])
        self.pie_canvas.draw()
        
        self.network_ax.clear()
        self.network_ax.text(0.5, 0.5, 'No network data yet\nStart analysis to see usage', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=self.network_ax.transAxes, fontsize=12)
        self.network_ax.set_xticks([])
        self.network_ax.set_yticks([])
        self.network_canvas.draw()
        
        messagebox.showinfo("Cleared", "All data has been cleared.")
    
    def update_dashboard(self):
        """Update dashboard in real-time"""
        while self.is_updating:
            try:
                # Update statistics
                stats = self.dns_sniffer.get_domain_statistics()
                productivity_analysis = self.dns_sniffer.get_productivity_analysis()
                network_stats = self.network_monitor.get_network_stats()
                
                # Update UI in main thread
                self.root.after(0, self._update_ui, stats, productivity_analysis, network_stats)
                
                time.sleep(2)  # Update every 2 seconds
                
            except Exception as e:
                print(f"Error updating dashboard: {e}")
                time.sleep(5)
    
    def _update_ui(self, stats, productivity_analysis, network_stats):
        """Update UI elements"""
        try:
            # Update statistics labels
            self.total_domains_label.config(text=f"Domains Tracked: {stats['total_domains']}")
            self.total_packets_label.config(text=f"Packets Captured: {stats['total_packets']}")
            
            productivity_score = productivity_analysis.get('productivity_score', 0)
            score_color = 'green' if productivity_score >= 70 else 'orange' if productivity_score >= 40 else 'red'
            self.productivity_score_label.config(
                text=f"Productivity Score: {productivity_score:.1f}%",
                foreground=score_color
            )
            
            # Update activity text
            self.activity_text.delete(1.0, tk.END)
            recent_activity = stats.get('recent_activity', [])
            
            if not recent_activity:
                self.activity_text.insert(tk.END, "No activity captured yet.\n\n")
                self.activity_text.insert(tk.END, "Visit websites like:\n")
                self.activity_text.insert(tk.END, "- youtube.com\n- instagram.com\n- github.com\n- netflix.com\n")
                self.activity_text.insert(tk.END, "\nMake sure you're running as Administrator!")
            else:
                for activity in reversed(recent_activity[-20:]):  # Show last 20 activities
                    domain = activity.get('domain', 'Unknown')
                    timestamp = time.strftime('%H:%M:%S', time.localtime(activity.get('timestamp', 0)))
                    protocol = activity.get('protocol', 'Unknown')
                    
                    # Color code based on domain type
                    category, _ = self.dns_sniffer.classifier.classify_website_ml(domain)

                    if category == 'productive':
                        color_tag = 'productive'
                    elif category == 'unproductive':
                        color_tag = 'unproductive'
                    else:
                        color_tag = 'neutral'
                    
                    self.activity_text.insert(tk.END, f"[{timestamp}] ", 'time')
                    self.activity_text.insert(tk.END, f"{domain} ", color_tag)
                    self.activity_text.insert(tk.END, f"({protocol})\n", 'protocol')
            
            # Configure text colors
            self.activity_text.tag_configure('time', foreground='gray')
            self.activity_text.tag_configure('protocol', foreground='blue')
            self.activity_text.tag_configure('productive', foreground='green')
            self.activity_text.tag_configure('unproductive', foreground='red')
            self.activity_text.tag_configure('neutral', foreground='orange')
            
            # Update pie chart
            self._update_pie_chart(productivity_analysis)
            
            # Update analysis text
            self._update_analysis_text(productivity_analysis)

            # Update network usage
            self._update_network_chart(network_stats)

            # Update anomaly stats
            self.update_anomaly_stats()

            
            # Update speed labels
            upload_speed = network_stats['upload_speed']
            download_speed = network_stats['download_speed']
            
            self.upload_label.config(text=f"{upload_speed:.1f} KB/s")
            self.download_label.config(text=f"{download_speed:.1f} KB/s")
            self.connections_label.config(text=f"{stats['total_domains']}")
            
        except Exception as e:
            print(f"Error updating UI: {e}")
    
    def _update_pie_chart(self, productivity_analysis):
        """Update the productivity pie chart"""
        self.pie_ax.clear()
        
        percentages = productivity_analysis.get('percentages', {})
        total_time = productivity_analysis.get('total_time', 0)
        
        labels = ['Productive', 'Unproductive', 'Neutral']
        sizes = [
            percentages.get('productive', 0),
            percentages.get('unproductive', 0),
            percentages.get('neutral', 0)
        ]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        explode = (0.05, 0.05, 0.05)  # Slight separation
        
        if sum(sizes) > 0:
            wedges, texts, autotexts = self.pie_ax.pie(
                sizes, explode=explode, labels=labels, colors=colors, 
                autopct='%1.1f%%', startangle=90, shadow=True
            )
            
            # Style the autopct text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            self.pie_ax.set_title(f'Website Productivity Distribution\n(Total Time: {total_time/60:.1f} min)', 
                                fontsize=12, fontweight='bold')
            
            # Add legend
            self.pie_ax.legend(wedges, labels, title="Categories", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        
        else:
            # Show placeholder when no data
            self.pie_ax.text(0.5, 0.5, 'No data collected yet\n\nVisit websites to see\nthe productivity analysis', 
                           horizontalalignment='center', verticalalignment='center', 
                           transform=self.pie_ax.transAxes, fontsize=11, 
                           bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.pie_ax.set_xticks([])
            self.pie_ax.set_yticks([])
        
        self.pie_canvas.draw()
    
    def _update_analysis_text(self, productivity_analysis):
        """Update productivity analysis text"""
        self.analysis_text.delete(1.0, tk.END)
        
        percentages = productivity_analysis.get('percentages', {})
        total_time = productivity_analysis.get('total_time', 0)
        productivity_score = productivity_analysis.get('productivity_score', 0)
        category_time = productivity_analysis.get('category_time', {})
        
        analysis_text = f"""📊 Overall Productivity Analysis
{'=' * 40}

⏱️  Total Tracking Time: {int(total_time // 60)}:{int(total_time % 60):02d} (HH:MM)

🎯 Productivity Score: {productivity_score:.1f}%

📈 Time Distribution:
• ✅ Productive: {percentages.get('productive', 0):.1f}% ({category_time.get('productive', 0)/60:.1f} min)
• ❌ Unproductive: {percentages.get('unproductive', 0):.1f}% ({category_time.get('unproductive', 0)/60:.1f} min)
• ⚪ Neutral: {percentages.get('neutral', 0):.1f}% ({category_time.get('neutral', 0)/60:.1f} min)

💡 Recommendations:
"""
        
        if productivity_score >= 80:
            analysis_text += "🎉 Excellent! You're maintaining high productivity. Keep up the great work!\nFocus on maintaining this balance while taking healthy breaks."
        elif productivity_score >= 60:
            analysis_text += "👍 Good job! You're mostly productive, but there's some room for improvement.\nConsider reducing time on entertainment sites during work hours."
        elif productivity_score >= 40:
            analysis_text += "⚠️  Moderate productivity detected. Consider setting time limits for social media and entertainment sites.\nTry using website blockers during focused work sessions."
        else:
            analysis_text += "🔴 Low productivity detected. Most of your time is spent on unproductive sites.\nTry the Pomodoro technique: 25min work / 5min break cycles."
        
        analysis_text += f"\n\n💭 Tip: {self._get_random_tip()}"
        
        self.analysis_text.insert(tk.END, analysis_text)
    
    def _get_random_tip(self):
        """Return a random productivity tip"""
        tips = [
            "Use website blockers during focused work sessions",
            "Try the 25-5 Pomodoro technique for better focus",
            "Schedule specific times for checking social media",
            "Use browser extensions to track time on websites",
            "Set daily goals for productive work",
            "Take regular breaks to maintain productivity",
            "Use separate browsers for work and personal use",
            "Disable notifications during deep work sessions"
        ]
        import random
        return random.choice(tips)
    
    def _update_network_chart(self, network_stats):
        """Update network usage chart"""
        self.network_ax.clear()
        
        upload_history = network_stats.get('upload_history', [])[-50:]
        download_history = network_stats.get('download_history', [])[-50:]
        
        if upload_history and download_history:
            x = list(range(len(upload_history)))
            
            # Plot with better styling
            self.network_ax.plot(x, upload_history, label='Upload (KB/s)', color='#e74c3c', linewidth=2)
            self.network_ax.plot(x, download_history, label='Download (KB/s)', color='#3498db', linewidth=2)
            
            # Fill under the lines
            self.network_ax.fill_between(x, upload_history, alpha=0.3, color='#e74c3c')
            self.network_ax.fill_between(x, download_history, alpha=0.3, color='#3498db')
            
            self.network_ax.legend(loc='upper right')
            self.network_ax.set_xlabel('Time (seconds)')
            self.network_ax.set_ylabel('Speed (KB/s)')
            self.network_ax.set_title('Real-time Network Usage', fontweight='bold')
            self.network_ax.grid(True, alpha=0.3)
            
            # Set y-axis to start from 0
            self.network_ax.set_ylim(bottom=0)
            
        else:
            # Show placeholder when no data
            self.network_ax.text(0.5, 0.5, 'No network data yet\n\nStart analysis to monitor\nnetwork usage in real-time', 
                               horizontalalignment='center', verticalalignment='center', 
                               transform=self.network_ax.transAxes, fontsize=12,
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.network_ax.set_xticks([])
            self.network_ax.set_yticks([])

        self.network_canvas.draw()

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
            messagebox.showinfo("Success", f"Added label for {domain}: {category}")
            self.domain_entry.delete(0, tk.END)
            self.update_ml_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add label: {e}")

    def train_ml_model(self):
        """Train the ML model with current data"""
        try:
            self.train_btn.config(state=tk.DISABLED, text="Training...")
            self.root.update()

            # Train the model
            result = self.dns_sniffer.classifier.train_model()

            self.train_btn.config(state=tk.NORMAL, text="Train Model")

            if "successfully" in result:
                messagebox.showinfo("Success", f"Model trained successfully!\n\n{result}")
            else:
                messagebox.showerror("Error", f"Training failed!\n\n{result}")

            self.update_ml_stats()
        except Exception as e:
            self.train_btn.config(state=tk.NORMAL, text="Train Model")
            messagebox.showerror("Error", f"Training failed: {e}")


    def retrain_model(self):
        """Retrain the model from scratch"""
        try:
            self.retrain_btn.config(state=tk.DISABLED, text="Retraining...")
            self.root.update()

            # Retrain the model
            result = self.dns_sniffer.classifier.retrain_model()

            self.retrain_btn.config(state=tk.NORMAL, text="Retrain Model")

            if result:
                messagebox.showinfo("Success", "Model retrained successfully!")
            else:
                messagebox.showerror("Error", "Retraining failed - insufficient data or error occurred.")

            self.update_ml_stats()
        except Exception as e:
            self.retrain_btn.config(state=tk.NORMAL, text="Retrain Model")
            messagebox.showerror("Error", f"Retraining failed: {e}")


    def update_ml_stats(self):
        """Update the ML statistics display"""
        try:
            self.ml_text.delete(1.0, tk.END)

            # Get ML statistics
            stats = self.dns_sniffer.classifier.get_ml_stats()

            # Format metrics safely
            accuracy = stats.get('accuracy', 'N/A')
            precision = stats.get('precision', 'N/A')
            recall = stats.get('recall', 'N/A')
            f1_score = stats.get('f1_score', 'N/A')

            accuracy_str = accuracy if isinstance(accuracy, str) else f"{accuracy:.1f}"
            precision_str = precision if isinstance(precision, str) else f"{precision:.1f}"
            recall_str = recall if isinstance(recall, str) else f"{recall:.1f}"
            f1_str = f1_score if isinstance(f1_score, str) else f"{f1_score:.1f}"

            ml_info = f"""🤖 Machine Learning Statistics
{'=' * 40}

📊 Model Performance:
• Accuracy: {accuracy_str}%
• Precision: {precision_str}%
• Recall: {recall_str}%
• F1-Score: {f1_str}%



📈 Training Data:
• Total Samples: {stats.get('total_samples', 0)}
• Productive: {stats.get('productive_count', 0)}
• Unproductive: {stats.get('unproductive_count', 0)}
• Neutral: {stats.get('neutral_count', 0)}

🔧 Model Details:
• Algorithm: {stats.get('algorithm', 'N/A')}
• Last Trained: {stats.get('last_trained', 'Never')}
• Features Used: {stats.get('features_count', 0)}

💡 User Labels Added: {stats.get('user_labels_count', 0)}

📝 Recent User Labels:
"""

            # Add recent user labels
            user_labels = stats.get('recent_user_labels', [])
            if user_labels:
                for label in user_labels[-10:]:  # Show last 10
                    ml_info += f"• {label['domain']} → {label['category']}\n"
            else:
                ml_info += "• No user labels added yet\n"

            ml_info += "\n💭 Tips:\n"
            ml_info += "• Add more labels to improve accuracy\n"
            ml_info += "• Train the model after adding labels\n"
            ml_info += "• Retrain periodically for better performance\n"

            self.ml_text.insert(tk.END, ml_info)

        except Exception as e:
            self.ml_text.delete(1.0, tk.END)
            self.ml_text.insert(tk.END, f"Error loading ML stats: {e}")

    def setup_anomaly_tab(self):
        """Setup anomaly detection tab"""
        # Main frame
        main_frame = ttk.Frame(self.anomaly_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Stats frame
        main_frame.rowconfigure(1, weight=1)  # Alerts frame
        main_frame.rowconfigure(2, weight=0)  # Controls frame

        # Anomaly statistics frame - TOP
        stats_frame = ttk.LabelFrame(main_frame, text="Anomaly Detection Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)

        # Statistics labels
        self.anomaly_total_alerts_label = ttk.Label(stats_grid, text="Total Alerts: 0", font=('Arial', 10))
        self.anomaly_total_alerts_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)

        self.anomaly_alerts_per_hour_label = ttk.Label(stats_grid, text="Alerts/Hour: 0", font=('Arial', 10))
        self.anomaly_alerts_per_hour_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)

        self.anomaly_training_status_label = ttk.Label(stats_grid, text="Training Status: Not Trained", font=('Arial', 10))
        self.anomaly_training_status_label.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        self.anomaly_baseline_samples_label = ttk.Label(stats_grid, text="Baseline Samples: 0", font=('Arial', 10))
        self.anomaly_baseline_samples_label.grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)

        # Recent alerts frame - MIDDLE (expands)
        alerts_frame = ttk.LabelFrame(main_frame, text="Recent Anomaly Alerts")
        alerts_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        alerts_frame.columnconfigure(0, weight=1)
        alerts_frame.rowconfigure(0, weight=1)

        # Text widget for alerts
        self.anomaly_text = tk.Text(alerts_frame, height=15, width=100, wrap=tk.WORD, font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(alerts_frame, orient=tk.VERTICAL, command=self.anomaly_text.yview)
        self.anomaly_text.configure(yscrollcommand=scrollbar.set)

        self.anomaly_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Controls frame - BOTTOM
        controls_frame = ttk.LabelFrame(main_frame, text="Anomaly Detection Controls")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Controls grid
        controls_grid = ttk.Frame(controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=10)

        # Buttons
        self.update_baseline_btn = ttk.Button(controls_grid, text="Update Baseline", command=self.update_anomaly_baseline)
        self.update_baseline_btn.grid(row=0, column=0, padx=5, pady=5)

        self.clear_anomaly_btn = ttk.Button(controls_grid, text="Clear Anomaly Data", command=self.clear_anomaly_data)
        self.clear_anomaly_btn.grid(row=0, column=1, padx=5, pady=5)

        # Initial anomaly stats display
        self.update_anomaly_stats()

    def update_anomaly_baseline(self):
        """Update the anomaly detection baseline"""
        try:
            self.update_baseline_btn.config(state=tk.DISABLED, text="Updating...")
            self.root.update()

            # Update baseline
            success = self.dns_sniffer.update_anomaly_baseline()

            self.update_baseline_btn.config(state=tk.NORMAL, text="Update Baseline")

            if success:
                messagebox.showinfo("Success", "Anomaly detection baseline updated successfully!")
                self.update_anomaly_stats()
            else:
                messagebox.showerror("Error", "Failed to update anomaly baseline.")

        except Exception as e:
            self.update_baseline_btn.config(state=tk.NORMAL, text="Update Baseline")
            messagebox.showerror("Error", f"Failed to update baseline: {e}")

    def clear_anomaly_data(self):
        """Clear anomaly detection data"""
        try:
            self.dns_sniffer.anomaly_detector.clear_data()
            self.anomaly_text.delete(1.0, tk.END)
            self.anomaly_text.insert(tk.END, "Anomaly data cleared.\n\nStart analysis to begin monitoring for anomalies.")
            self.update_anomaly_stats()
            messagebox.showinfo("Cleared", "Anomaly detection data has been cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear anomaly data: {e}")

    def update_anomaly_stats(self):
        """Update the anomaly detection statistics display"""
        try:
            # Get anomaly statistics
            anomaly_stats = self.dns_sniffer.get_anomaly_stats()

            # Update statistics labels
            total_alerts = anomaly_stats.get('total_alerts', 0)
            alerts_per_hour = anomaly_stats.get('alerts_per_hour', 0)
            training_status = "Trained" if anomaly_stats.get('is_trained', False) else "Not Trained"
            baseline_samples = anomaly_stats.get('baseline_samples', 0)

            self.anomaly_total_alerts_label.config(text=f"Total Alerts: {total_alerts}")
            self.anomaly_alerts_per_hour_label.config(text=f"Alerts/Hour: {alerts_per_hour:.1f}")
            self.anomaly_training_status_label.config(text=f"Training Status: {training_status}")
            self.anomaly_baseline_samples_label.config(text=f"Baseline Samples: {baseline_samples}")

            # Update alerts text
            self.anomaly_text.delete(1.0, tk.END)

            anomaly_info = f"""🚨 Anomaly Detection Monitor
{'=' * 40}

📊 Detection Statistics:
• Total Alerts: {total_alerts}
• Alerts per Hour: {alerts_per_hour:.1f}
• Training Status: {training_status}
• Baseline Samples: {baseline_samples}

🔍 Recent Alerts:
"""

            # Add recent alerts
            recent_alerts = anomaly_stats.get('recent_alerts', [])
            if recent_alerts:
                for alert in recent_alerts[-15:]:  # Show last 15 alerts
                    timestamp = time.strftime('%H:%M:%S', time.localtime(alert.get('timestamp', 0)))
                    domain = alert.get('domain', 'Unknown')
                    score = alert.get('anomaly_score', 0)
                    message = alert.get('alert_message', 'Unknown anomaly')

                    anomaly_info += f"\n[{timestamp}] {domain}\n"
                    anomaly_info += f"  Score: {score:.2f} | {message}\n"
            else:
                anomaly_info += "\n• No recent alerts\n"

            anomaly_info += "\n💡 Tips:\n"
            anomaly_info += "• Update baseline after initial training period\n"
            anomaly_info += "• High anomaly scores indicate unusual behavior\n"
            anomaly_info += "• Clear data periodically to reset monitoring\n"

            self.anomaly_text.insert(tk.END, anomaly_info)

        except Exception as e:
            self.anomaly_text.delete(1.0, tk.END)
            self.anomaly_text.insert(tk.END, f"Error loading anomaly stats: {e}")

    def setup_forecasting_tab(self):
        """Setup productivity forecasting tab"""
        # Main frame
        main_frame = ttk.Frame(self.forecasting_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Stats frame
        main_frame.rowconfigure(1, weight=1)  # Chart frame
        main_frame.rowconfigure(2, weight=0)  # Insights frame
        main_frame.rowconfigure(3, weight=0)  # Controls frame

        # Forecasting statistics frame - TOP
        stats_frame = ttk.LabelFrame(main_frame, text="Forecasting Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)

        # Statistics labels
        self.forecast_total_samples_label = ttk.Label(stats_grid, text="Total Samples: 0", font=('Arial', 10))
        self.forecast_total_samples_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)

        self.forecast_linear_status_label = ttk.Label(stats_grid, text="Linear Model: Not Trained", font=('Arial', 10))
        self.forecast_linear_status_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)

        self.forecast_arima_status_label = ttk.Label(stats_grid, text="ARIMA Model: Not Trained", font=('Arial', 10))
        self.forecast_arima_status_label.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        self.forecast_accuracy_label = ttk.Label(stats_grid, text="Forecast Accuracy: N/A", font=('Arial', 10))
        self.forecast_accuracy_label.grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)

        # Forecast chart frame - MIDDLE (expands)
        chart_frame = ttk.LabelFrame(main_frame, text="Productivity Forecast")
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)

        # Create matplotlib figure for forecasting
        self.forecast_fig = Figure(figsize=(10, 5), dpi=80)
        self.forecast_ax = self.forecast_fig.add_subplot(111)

        # Create canvas
        self.forecast_canvas = FigureCanvasTkAgg(self.forecast_fig, chart_frame)
        self.forecast_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Insights frame - BOTTOM MIDDLE
        insights_frame = ttk.LabelFrame(main_frame, text="Productivity Insights & Recommendations")
        insights_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        insights_frame.columnconfigure(0, weight=1)
        insights_frame.rowconfigure(0, weight=1)

        # Text widget for insights
        self.forecast_insights_text = tk.Text(insights_frame, height=8, width=100, wrap=tk.WORD, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(insights_frame, orient=tk.VERTICAL, command=self.forecast_insights_text.yview)
        self.forecast_insights_text.configure(yscrollcommand=scrollbar.set)

        self.forecast_insights_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Controls frame - BOTTOM
        controls_frame = ttk.LabelFrame(main_frame, text="Forecasting Controls")
        controls_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

        # Controls grid
        controls_grid = ttk.Frame(controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=10)

        # Days to forecast
        ttk.Label(controls_grid, text="Days to Forecast:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.forecast_days_var = tk.StringVar(value='7')
        forecast_days_combo = ttk.Combobox(controls_grid, textvariable=self.forecast_days_var,
                                         values=['3', '7', '14', '30'], state='readonly', width=5)
        forecast_days_combo.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Buttons
        self.train_linear_btn = ttk.Button(controls_grid, text="Train Linear Model", command=self.train_linear_model)
        self.train_linear_btn.grid(row=0, column=2, padx=5, pady=5)

        self.train_arima_btn = ttk.Button(controls_grid, text="Train ARIMA Model", command=self.train_arima_model)
        self.train_arima_btn.grid(row=0, column=3, padx=5, pady=5)

        self.generate_forecast_btn = ttk.Button(controls_grid, text="Generate Forecast", command=self.generate_forecast)
        self.generate_forecast_btn.grid(row=0, column=4, padx=5, pady=5)

        self.clear_forecast_btn = ttk.Button(controls_grid, text="Clear Forecast Data", command=self.clear_forecast_data)
        self.clear_forecast_btn.grid(row=0, column=5, padx=5, pady=5)

        # Initial forecast stats display
        self.update_forecast_stats()

    def train_linear_model(self):
        """Train the linear regression model"""
        try:
            self.train_linear_btn.config(state=tk.DISABLED, text="Training...")
            self.root.update()

            # Train linear model
            success = self.dns_sniffer.productivity_predictor.train_linear_model()

            self.train_linear_btn.config(state=tk.NORMAL, text="Train Linear Model")

            if success:
                messagebox.showinfo("Success", "Linear regression model trained successfully!")
                self.update_forecast_stats()
            else:
                messagebox.showerror("Error", "Failed to train linear model - insufficient data.")

        except Exception as e:
            self.train_linear_btn.config(state=tk.NORMAL, text="Train Linear Model")
            messagebox.showerror("Error", f"Failed to train linear model: {e}")

    def train_arima_model(self):
        """Train the ARIMA model"""
        try:
            self.train_arima_btn.config(state=tk.DISABLED, text="Training...")
            self.root.update()

            # Train ARIMA model
            success = self.dns_sniffer.productivity_predictor.train_arima_model()

            self.train_arima_btn.config(state=tk.NORMAL, text="Train ARIMA Model")

            if success:
                messagebox.showinfo("Success", "ARIMA model trained successfully!")
                self.update_forecast_stats()
            else:
                messagebox.showerror("Error", "Failed to train ARIMA model - insufficient data.")

        except Exception as e:
            self.train_arima_btn.config(state=tk.NORMAL, text="Train ARIMA Model")
            messagebox.showerror("Error", f"Failed to train ARIMA model: {e}")

    def generate_forecast(self):
        """Generate productivity forecast"""
        try:
            days_ahead = int(self.forecast_days_var.get())

            self.generate_forecast_btn.config(state=tk.DISABLED, text="Generating...")
            self.root.update()

            # Generate forecast
            forecasts = self.dns_sniffer.productivity_predictor.forecast_productivity(days_ahead)

            self.generate_forecast_btn.config(state=tk.NORMAL, text="Generate Forecast")

            if forecasts:
                self._update_forecast_chart(forecasts, days_ahead)
                self._update_forecast_insights()
                messagebox.showinfo("Success", f"Forecast generated for {days_ahead} days ahead!")
            else:
                messagebox.showerror("Error", "Failed to generate forecast - no trained models available.")

        except Exception as e:
            self.generate_forecast_btn.config(state=tk.NORMAL, text="Generate Forecast")
            messagebox.showerror("Error", f"Failed to generate forecast: {e}")

    def clear_forecast_data(self):
        """Clear forecasting data"""
        try:
            self.dns_sniffer.productivity_predictor.clear_data()
            self.forecast_ax.clear()
            self.forecast_ax.text(0.5, 0.5, 'Forecast data cleared\n\nTrain models and generate\nnew forecasts', 
                                horizontalalignment='center', verticalalignment='center', 
                                transform=self.forecast_ax.transAxes, fontsize=12,
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.forecast_ax.set_xticks([])
            self.forecast_ax.set_yticks([])
            self.forecast_canvas.draw()

            self.forecast_insights_text.delete(1.0, tk.END)
            self.forecast_insights_text.insert(tk.END, "Forecast data cleared.\n\nStart collecting productivity data to begin forecasting.")

            self.update_forecast_stats()
            messagebox.showinfo("Cleared", "Forecasting data has been cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear forecast data: {e}")

    def update_forecast_stats(self):
        """Update the forecasting statistics display"""
        try:
            # Get forecasting statistics
            predictor = self.dns_sniffer.productivity_predictor
            total_samples = len(predictor.productivity_history)

            linear_status = "Trained" if predictor.linear_trained else "Not Trained"
            arima_status = "Trained" if predictor.arima_trained else "Not Trained"

            # Get forecast accuracy
            accuracy_metrics = predictor.get_forecast_accuracy()
            accuracy_str = "N/A"
            if accuracy_metrics.get('mae') is not None:
                mae = accuracy_metrics['mae']
                mape = accuracy_metrics.get('mape', 0)
                accuracy_str = f"MAE: {mae:.1f}, MAPE: {mape:.1f}%"

            self.forecast_total_samples_label.config(text=f"Total Samples: {total_samples}")
            self.forecast_linear_status_label.config(text=f"Linear Model: {linear_status}")
            self.forecast_arima_status_label.config(text=f"ARIMA Model: {arima_status}")
            self.forecast_accuracy_label.config(text=f"Forecast Accuracy: {accuracy_str}")

        except Exception as e:
            print(f"Error updating forecast stats: {e}")

    def _update_forecast_chart(self, forecasts, days_ahead):
        """Update the forecast chart"""
        self.forecast_ax.clear()

        # Get historical data for context
        historical_df = self.dns_sniffer.productivity_predictor.get_historical_data(days=7)

        # Check if we have historical data to plot
        has_historical = not historical_df.empty and len(historical_df) > 0

        if has_historical:
            # Plot historical data
            historical_df['productivity_score'].plot(ax=self.forecast_ax, label='Historical', color='blue', linewidth=2)

        # Plot forecasts if available
        colors = ['red', 'green', 'orange', 'purple']
        forecast_plotted = False

        for i, (method, forecast_data) in enumerate(forecasts.items()):
            if method != 'ensemble' and 'predictions' in forecast_data:
                predictions = forecast_data['predictions']
                if predictions and len(predictions) > 0:
                    forecast_plotted = True
                    # Create future dates
                    last_date = historical_df.index[-1] if has_historical else pd.Timestamp.now()
                    future_dates = pd.date_range(start=last_date, periods=len(predictions) + 1, freq='D')[1:]

                    # Plot forecast
                    self.forecast_ax.plot(future_dates, predictions, label=f'{method.upper()} Forecast',
                                        color=colors[i % len(colors)], linestyle='--', linewidth=2)

                    # Add confidence intervals if available
                    if 'confidence_intervals' in forecast_data and forecast_data['confidence_intervals']:
                        cis = forecast_data['confidence_intervals']
                        if len(cis) == len(predictions):
                            lower_bounds = [ci[0] for ci in cis]
                            upper_bounds = [ci[1] for ci in cis]
                            self.forecast_ax.fill_between(future_dates, lower_bounds, upper_bounds,
                                                        color=colors[i % len(colors)], alpha=0.2)

        # If no data at all, show message
        if not has_historical and not forecast_plotted:
            self.forecast_ax.text(0.5, 0.5, 'No historical data available\n\nStart collecting productivity data\nto generate forecasts',
                                horizontalalignment='center', verticalalignment='center',
                                transform=self.forecast_ax.transAxes, fontsize=12,
                                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            self.forecast_ax.set_xticks([])
            self.forecast_ax.set_yticks([])
        else:
            # Set up axes for data plots
            self.forecast_ax.legend(loc='upper left')
            self.forecast_ax.set_xlabel('Date')
            self.forecast_ax.set_ylabel('Productivity Score (%)')
            self.forecast_ax.set_title(f'Productivity Forecast ({days_ahead} Days Ahead)', fontweight='bold')
            self.forecast_ax.grid(True, alpha=0.3)
            self.forecast_ax.set_ylim(0, 100)

        self.forecast_canvas.draw()

    def _update_forecast_insights(self):
        """Update forecast insights and recommendations"""
        self.forecast_insights_text.delete(1.0, tk.END)

        try:
            insights = self.dns_sniffer.productivity_predictor.get_productivity_insights()

            insights_text = f"""🔮 Productivity Forecasting Insights
{'=' * 45}

📊 Statistics:
• Average Productivity: {insights.get('statistics', {}).get('average_productivity', 0):.1f}%
• Max Productivity: {insights.get('statistics', {}).get('max_productivity', 0):.1f}%
• Min Productivity: {insights.get('statistics', {}).get('min_productivity', 0):.1f}%
• Total Samples: {insights.get('statistics', {}).get('total_samples', 0)}

📈 Trends:
"""

            # Add trends
            trends = insights.get('trends', {})
            if trends.get('recent_weekly_change') is not None:
                change = trends['recent_weekly_change']
                direction = "increasing" if change > 0 else "decreasing"
                insights_text += f"• Recent trend: Productivity is {direction} by {abs(change):.1f}% per week\n"
            else:
                insights_text += "• No trend data available yet\n"

            # Add patterns
            patterns = insights.get('patterns', {})
            weekly_pattern = patterns.get('weekly_pattern', {})
            if weekly_pattern:
                best_day = max(weekly_pattern, key=weekly_pattern.get)
                worst_day = min(weekly_pattern, key=weekly_pattern.get)
                insights_text += f"• Most productive day: {best_day} ({weekly_pattern[best_day]:.1f}%)\n"
                insights_text += f"• Least productive day: {worst_day} ({weekly_pattern[worst_day]:.1f}%)\n"

            work_vs_nonwork = patterns.get('work_vs_nonwork', {})
            if work_vs_nonwork:
                work_avg = work_vs_nonwork.get('work_hours_avg', 0)
                nonwork_avg = work_vs_nonwork.get('non_work_hours_avg', 0)
                insights_text += f"• Work hours average: {work_avg:.1f}%\n"
                insights_text += f"• Non-work hours average: {nonwork_avg:.1f}%\n"

            insights_text += "\n💡 Recommendations:\n"
            recommendations = insights.get('recommendations', [])
            if recommendations:
                for rec in recommendations:
                    insights_text += f"• {rec}\n"
            else:
                insights_text += "• Collect more data to generate personalized recommendations\n"

            insights_text += "\n🎯 Forecasting Tips:\n"
            insights_text += "• Train multiple models for better accuracy\n"
            insights_text += "• Update forecasts regularly as you collect more data\n"
            insights_text += "• Use ensemble forecasts for more reliable predictions\n"

            self.forecast_insights_text.insert(tk.END, insights_text)

        except Exception as e:
            self.forecast_insights_text.insert(tk.END, f"Error generating insights: {e}")

    def setup_content_tab(self):
        """Setup content analysis tab"""
        # Main frame
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=0)  # Stats frame
        main_frame.rowconfigure(1, weight=1)  # Analysis frame
        main_frame.rowconfigure(2, weight=0)  # Controls frame

        # Content analysis statistics frame - TOP
        stats_frame = ttk.LabelFrame(main_frame, text="Content Analysis Statistics")
        stats_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Stats grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X, padx=10, pady=10)

        # Statistics labels
        self.content_total_analyzed_label = ttk.Label(stats_grid, text="Total Analyzed: 0", font=('Arial', 10))
        self.content_total_analyzed_label.grid(row=0, column=0, padx=20, pady=5, sticky=tk.W)

        self.content_positive_sentiment_label = ttk.Label(stats_grid, text="Positive: 0%", font=('Arial', 10))
        self.content_positive_sentiment_label.grid(row=0, column=1, padx=20, pady=5, sticky=tk.W)

        self.content_negative_sentiment_label = ttk.Label(stats_grid, text="Negative: 0%", font=('Arial', 10))
        self.content_negative_sentiment_label.grid(row=0, column=2, padx=20, pady=5, sticky=tk.W)

        self.content_neutral_sentiment_label = ttk.Label(stats_grid, text="Neutral: 0%", font=('Arial', 10))
        self.content_neutral_sentiment_label.grid(row=0, column=3, padx=20, pady=5, sticky=tk.W)

        # Content analysis frame - MIDDLE (expands)
        analysis_frame = ttk.LabelFrame(main_frame, text="Content Analysis Results")
        analysis_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)

        # Text widget for content analysis
        self.content_text = tk.Text(analysis_frame, height=20, width=100, wrap=tk.WORD, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)

        self.content_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Controls frame - BOTTOM
        controls_frame = ttk.LabelFrame(main_frame, text="Content Analysis Controls")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        # Controls grid
        controls_grid = ttk.Frame(controls_frame)
        controls_grid.pack(fill=tk.X, padx=10, pady=10)

        # Domain input for content analysis
        ttk.Label(controls_grid, text="Domain to Analyze:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.content_domain_entry = ttk.Entry(controls_grid, width=30)
        self.content_domain_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Buttons
        self.analyze_content_btn = ttk.Button(controls_grid, text="Analyze Content", command=self.analyze_content)
        self.analyze_content_btn.grid(row=0, column=2, padx=5, pady=5)

        self.clear_content_btn = ttk.Button(controls_grid, text="Clear Analysis", command=self.clear_content_analysis)
        self.clear_content_btn.grid(row=0, column=3, padx=5, pady=5)

        # Privacy consent checkbox
        self.privacy_consent_var = tk.BooleanVar(value=False)
        self.privacy_consent_check = ttk.Checkbutton(controls_grid, text="Enable Deep Content Analysis (Requires Consent)",
                                                   variable=self.privacy_consent_var, command=self.toggle_deep_analysis)
        self.privacy_consent_check.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky=tk.W)

        # Initial content stats display
        self.update_content_stats()

    def toggle_deep_analysis(self):
        """Toggle deep content analysis based on privacy consent"""
        if self.privacy_consent_var.get():
            messagebox.showinfo("Privacy Notice",
                              "Deep content analysis enabled. This will analyze website content for sentiment and keywords.\n\n"
                              "Please ensure you have permission to analyze the content of websites you visit.\n"
                              "This feature is intended for personal productivity monitoring only.")
        else:
            messagebox.showinfo("Privacy Notice", "Deep content analysis disabled.")

    def analyze_content(self):
        """Analyze content for a specific domain"""
        domain = self.content_domain_entry.get().strip()

        if not domain:
            messagebox.showerror("Error", "Please enter a domain name to analyze.")
            return

        try:
            self.analyze_content_btn.config(state=tk.DISABLED, text="Analyzing...")
            self.root.update()

            # Analyze content
            analysis_result = self.dns_sniffer.analyze_domain_content(domain, deep_analysis=self.privacy_consent_var.get())

            self.analyze_content_btn.config(state=tk.NORMAL, text="Analyze Content")

            if analysis_result:
                self._update_content_display(analysis_result)
                messagebox.showinfo("Success", f"Content analysis completed for {domain}!")
            else:
                messagebox.showerror("Error", f"Failed to analyze content for {domain}.")

        except Exception as e:
            self.analyze_content_btn.config(state=tk.NORMAL, text="Analyze Content")
            messagebox.showerror("Error", f"Failed to analyze content: {e}")

    def clear_content_analysis(self):
        """Clear content analysis data"""
        try:
            self.dns_sniffer.content_analyzer.clear_analysis_data()
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, "Content analysis data cleared.\n\nEnter a domain and click 'Analyze Content' to begin analysis.")
            self.update_content_stats()
            messagebox.showinfo("Cleared", "Content analysis data has been cleared.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear content analysis data: {e}")

    def update_content_stats(self):
        """Update the content analysis statistics display"""
        try:
            # Get content analysis statistics
            content_stats = self.dns_sniffer.get_content_stats()

            # Update statistics labels
            total_analyzed = content_stats.get('total_analyzed', 0)
            sentiment_distribution = content_stats.get('sentiment_distribution', {})

            positive_pct = sentiment_distribution.get('positive', 0)
            negative_pct = sentiment_distribution.get('negative', 0)
            neutral_pct = sentiment_distribution.get('neutral', 0)

            self.content_total_analyzed_label.config(text=f"Total Analyzed: {total_analyzed}")
            self.content_positive_sentiment_label.config(text=f"Positive: {positive_pct:.1f}%")
            self.content_negative_sentiment_label.config(text=f"Negative: {negative_pct:.1f}%")
            self.content_neutral_sentiment_label.config(text=f"Neutral: {neutral_pct:.1f}%")

            # Update content analysis text
            self.content_text.delete(1.0, tk.END)

            content_info = f"""📝 Content Analysis Dashboard
{'=' * 40}

📊 Analysis Statistics:
• Total Domains Analyzed: {total_analyzed}
• Sentiment Distribution:
  - Positive: {positive_pct:.1f}%
  - Negative: {negative_pct:.1f}%
  - Neutral: {neutral_pct:.1f}%

🔍 Recent Analyses:
"""

            # Add recent analyses
            recent_analyses = content_stats.get('recent_analyses', [])
            if recent_analyses:
                for analysis in recent_analyses[-10:]:  # Show last 10
                    domain = analysis.get('domain', 'Unknown')
                    sentiment = analysis.get('sentiment', 'Unknown')
                    keywords = analysis.get('keywords', [])
                    timestamp = time.strftime('%H:%M:%S', time.localtime(analysis.get('timestamp', 0)))

                    content_info += f"\n[{timestamp}] {domain}\n"
                    content_info += f"  Sentiment: {sentiment.title()}\n"
                    if keywords:
                        content_info += f"  Keywords: {', '.join(keywords[:5])}\n"  # Show top 5 keywords
            else:
                content_info += "\n• No recent analyses\n"

            content_info += "\n💡 Tips:\n"
            content_info += "• Enable deep analysis for detailed sentiment and keyword extraction\n"
            content_info += "• Analysis results help understand content quality and relevance\n"
            content_info += "• Use privacy consent carefully and only for personal monitoring\n"

            self.content_text.insert(tk.END, content_info)

        except Exception as e:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Error loading content stats: {e}")

    def _update_content_display(self, analysis_result):
        """Update the content analysis display with results"""
        try:
            domain = analysis_result.get('domain', 'Unknown')
            sentiment = analysis_result.get('sentiment', 'Unknown')
            keywords = analysis_result.get('keywords', [])
            summary = analysis_result.get('summary', 'No summary available')
            timestamp = time.strftime('%H:%M:%S', time.localtime(analysis_result.get('timestamp', 0)))
            sample_content = analysis_result.get('sample_content', [])

            # Update the content text with detailed analysis
            content_display = f"""📝 Content Analysis Results for {domain}
{'=' * 50}

🎯 Domain: {domain}
🕒 Last Analyzed: {timestamp}

"""

            if sentiment == 'unknown':
                content_display += """❌ No Content Data Available

This domain hasn't been analyzed yet. To analyze content:

1. ✅ Enable "Deep Content Analysis" checkbox below
2. 🔄 Start network analysis (▶️ Start Analysis button)
3. 🌐 Visit the website you want to analyze
4. 📊 Click "Analyze Content" again

⚠️  Privacy Notice: Deep content analysis examines website text for sentiment and keywords.
    Only enable this for websites you have permission to analyze.

"""
            else:
                content_display += f"""📊 Sentiment Analysis:
• Overall Sentiment: {sentiment.title()}
• Confidence: {analysis_result.get('confidence', 0):.1f}%

🔑 Key Topics & Keywords:
"""

                if keywords:
                    for i, keyword in enumerate(keywords[:10], 1):  # Show top 10
                        content_display += f"{i}. {keyword}\n"
                else:
                    content_display += "• No keywords extracted\n"

                content_display += f"\n📝 Content Summary:\n{summary}\n"

                # Add sample content if available
                if sample_content:
                    content_display += "\n📄 Sample Content Analyzed:\n"
                    for i, sample in enumerate(sample_content, 1):
                        content_display += f"\n--- Sample {i} ---\n{sample}\n"
                else:
                    content_display += "\n📄 Sample Content: No content samples available\n"

                # Add recommendations based on analysis
                content_display += "\n💡 Recommendations:\n"
                if sentiment == 'positive':
                    content_display += "• This content appears to be engaging and positive\n"
                    content_display += "• Consider spending more time on similar content\n"
                elif sentiment == 'negative':
                    content_display += "• This content may be stressful or negative\n"
                    content_display += "• Consider limiting time on similar content\n"
                else:
                    content_display += "• This content is neutral in tone\n"
                    content_display += "• Evaluate based on your productivity goals\n"

                # Add productivity context
                category, _ = self.dns_sniffer.classifier.classify_website_ml(domain)
                content_display += f"\n🏷️ Productivity Category: {category.title()}\n"

            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, content_display)

            # Update stats after analysis
            self.update_content_stats()

        except Exception as e:
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(tk.END, f"Error displaying content analysis: {e}")
