import tkinter as tk
from website_classifier import WebsiteClassifier
from dns_sniffer import DNSSniffer
from network_usage import NetworkUsageMonitor
from dashboard import NetworkAnalyzerDashboard
import sys
import os

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
    
    # Initialize components
    classifier = WebsiteClassifier()
    dns_sniffer = DNSSniffer(classifier)
    network_monitor = NetworkUsageMonitor()
    
    # Create main window
    root = tk.Tk()
    
    # Create dashboard
    app = NetworkAnalyzerDashboard(root, dns_sniffer, network_monitor)
    
    # Handle window close
    def on_closing():
        app.stop_analysis()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the application
    try:
        root.mainloop()
    except KeyboardInterrupt:
        on_closing()
    except Exception as e:
        print(f"Error: {e}")
        on_closing()

if __name__ == "__main__":
    main()