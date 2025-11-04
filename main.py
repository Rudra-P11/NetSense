import tkinter as tk
from website_classifier import WebsiteClassifier
from dns_sniffer import DNSSniffer
from network_usage import NetworkUsageMonitor
from dashboard import NetworkAnalyzerDashboard
from productivity_predictor import ProductivityPredictor
from auto_trainer import TrainingScheduler
import sys
import os
import warnings
warnings.filterwarnings('ignore')

def check_admin_privileges():
    """Check if the script is running with administrator privileges"""
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:  # Linux/Mac
            return os.getuid() == 0
    except:
        return False

def main():
    # Check for admin privileges
    if not check_admin_privileges():
        print("⚠️  Warning: This application requires administrator privileges to capture network packets.")
        print("Please run the script as administrator:")
        print("1. Open Command Prompt as Administrator")
        print("2. Navigate to the script directory")
        print("3. Run: python main.py")
        response = input("Do you want to continue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n" + "="*70)
    print("🚀 NetSense - Advanced Network Productivity Analyzer")
    print("="*70)
    print("📡 Initializing components...\n")
    
    # Initialize components
    print("✓ Loading website classifier...")
    classifier = WebsiteClassifier()
    
    print("✓ Initializing productivity predictor...")
    productivity_predictor = ProductivityPredictor()
    
    print("✓ Starting DNS sniffer...")
    dns_sniffer = DNSSniffer(classifier, productivity_predictor)
    
    print("✓ Initializing network monitor...")
    network_monitor = NetworkUsageMonitor()
    
    print("✓ Setting up auto-training scheduler (every 60 minutes)...")
    training_scheduler = TrainingScheduler(productivity_predictor, interval_minutes=60)
    training_scheduler.start()
    print("✓ Auto-trainer started! Models will retrain automatically.\n")
    
    print("="*70)
    print("💡 Tips:")
    print("  • Visit various websites (YouTube, GitHub, Netflix, etc.) to collect data")
    print("  • Models automatically retrain every 60 minutes")
    print("  • Forecasts are auto-generated using multiple ML models")
    print("  • Check the 'ML Insights' tab for advanced analytics")
    print("="*70 + "\n")
    
    # Create main window
    root = tk.Tk()
    
    # Create dashboard with auto-trainer reference
    app = NetworkAnalyzerDashboard(root, dns_sniffer, network_monitor)
    app.training_scheduler = training_scheduler
    
    # Handle window close
    def on_closing():
        print("\n🛑 Shutting down...")
        training_scheduler.stop()
        app.stop_analysis()
        root.destroy()
        print("✓ Shutdown complete. Goodbye!")
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        on_closing()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        on_closing()

if __name__ == "__main__":
    main()