import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from website_classifier import WebsiteClassifier

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
        self.root.title("Network Analyzer - Productivity Monitor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')
        
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(header_frame, text="Network Analyzer", 
                                   font=('Arial', 20, 'bold'))
        self.title_label.pack(side=tk.LEFT)
        
        # Control buttons
        control_frame = ttk.Frame(header_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.start_btn = ttk.Button(control_frame, text="Start Analysis", 
                                  command=self.start_analysis)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop Analysis", 
                                 command=self.stop_analysis, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="Clear Data", 
                                  command=self.clear_data)
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

        # Setup each tab
        self.setup_dashboard_tab()
        self.setup_productivity_tab()
        self.setup_ml_tab()
        self.setup_network_tab()
        
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
                    category, _ = self.dns_sniffer.classifier.classify_website(domain)
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

⏱️  Total Tracking Time: {total_time/60:.1f} minutes
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
            messagebox.showinfo("Success", f"Model trained successfully!\n\n{result}")
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
            messagebox.showinfo("Success", f"Model retrained successfully!\n\n{result}")
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

            ml_info = f"""🤖 Machine Learning Statistics
{'=' * 40}

📊 Model Performance:
• Accuracy: {stats.get('accuracy', 'N/A'):.1f}%
• Precision: {stats.get('precision', 'N/A'):.1f}%
• Recall: {stats.get('recall', 'N/A'):.1f}%
• F1-Score: {stats.get('f1_score', 'N/A'):.1f}%

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
