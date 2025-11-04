#!/usr/bin/env python3
"""
NetSense Setup Verification Script
Checks all dependencies and verifies proper installation
"""

import sys
import os

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python_version():
    """Check Python version"""
    print_header("Python Version Check")
    version = sys.version_info
    print(f"Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_core_modules():
    """Check core Python modules"""
    print_header("Core Modules Check")
    
    modules = {
        'tkinter': 'GUI Framework',
        'threading': 'Threading Support',
        'time': 'Time Operations',
        'json': 'JSON Processing',
        'collections': 'Data Structures',
        're': 'Regular Expressions'
    }
    
    all_ok = True
    for module, description in modules.items():
        try:
            __import__(module)
            print(f"✅ {module:20} - {description}")
        except ImportError:
            print(f"❌ {module:20} - {description} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_dependencies():
    """Check external dependencies"""
    print_header("External Dependencies Check")
    
    dependencies = {
        'scapy': 'Network packet capture',
        'matplotlib': 'Data visualization',
        'pandas': 'Data manipulation',
        'numpy': 'Numerical computing',
        'psutil': 'System monitoring',
        'sklearn': 'Machine learning (scikit-learn)',
        'statsmodels': 'Statistical modeling',
        'nltk': 'Natural language toolkit',
        'seaborn': 'Statistical visualization'
    }
    
    all_ok = True
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:20} - {description}")
        except ImportError:
            print(f"⚠️  {module:20} - {description} - OPTIONAL (will skip)")
            all_ok = False

def check_optional_modules():
    """Check optional advanced modules"""
    print_header("Optional Advanced Modules Check")
    
    optional = {
        'tensorflow': 'Deep Learning (LSTM)',
        'torch': 'PyTorch',
        'prophet': 'Facebook Prophet',
        'schedule': 'Task Scheduling'
    }
    
    for module, description in optional.items():
        try:
            __import__(module)
            print(f"✅ {module:20} - {description}")
        except ImportError:
            print(f"⚠️  {module:20} - {description} - OPTIONAL")

def check_local_files():
    """Check that all required local files exist"""
    print_header("Local Files Check")
    
    files = [
        'main.py',
        'dashboard.py',
        'productivity_predictor.py',
        'dns_sniffer.py',
        'website_classifier.py',
        'network_usage.py',
        'anomaly_detector.py',
        'content_analyzer.py',
        'data_collector.py',
        'model_storage.py',
        'auto_trainer.py',
        'requirements.txt'
    ]
    
    all_ok = True
    for file in files:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file:35} ({size:>8} bytes)")
        else:
            print(f"❌ {file:35} - NOT FOUND")
            all_ok = False
    
    return all_ok

def check_admin_privileges():
    """Check if running as administrator"""
    print_header("Administrator Privileges Check")
    
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                print("✅ Running as Administrator")
                return True
            else:
                print("⚠️  NOT running as Administrator")
                print("   Note: Packet capture requires admin privileges")
                print("   Solution: Right-click Command Prompt → 'Run as administrator'")
                return False
        else:  # Linux/Mac
            if os.getuid() == 0:
                print("✅ Running as Root")
                return True
            else:
                print("⚠️  NOT running as Root")
                print("   Note: Packet capture may require root privileges")
                return False
    except Exception as e:
        print(f"❌ Could not check admin status: {e}")
        return False

def test_imports():
    """Test importing all NetSense modules"""
    print_header("NetSense Modules Import Test")
    
    modules_to_import = [
        ('website_classifier', 'WebsiteClassifier'),
        ('dns_sniffer', 'DNSSniffer'),
        ('network_usage', 'NetworkUsageMonitor'),
        ('productivity_predictor', 'ProductivityPredictor'),
        ('auto_trainer', 'TrainingScheduler'),
        ('anomaly_detector', 'AnomalyDetector'),
        ('content_analyzer', 'ContentAnalyzer'),
        ('data_collector', 'DataCollector'),
    ]
    
    all_ok = True
    for module_name, class_name in modules_to_import:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"✅ {module_name:30} - {class_name}")
        except (ImportError, AttributeError) as e:
            print(f"❌ {module_name:30} - {class_name} - ERROR: {e}")
            all_ok = False
    
    return all_ok

def check_ml_capabilities():
    """Check ML model capabilities"""
    print_header("ML Models Availability")
    
    models = {
        'Linear Regression': True,  # Always available via sklearn
        'Gradient Boosting': True,  # Always available via sklearn
        'ARIMA': False,
        'SARIMAX': False,
        'Prophet': False,
        'LSTM': False
    }
    
    # Check sklearn
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.ensemble import GradientBoostingRegressor
        print("✅ Linear Regression      - Available")
        print("✅ Gradient Boosting      - Available")
    except:
        print("❌ scikit-learn models    - Not available")
    
    # Check ARIMA/SARIMAX
    try:
        from statsmodels.tsa.arima.model import ARIMA
        print("✅ ARIMA                  - Available")
        print("✅ SARIMAX                - Available")
    except:
        print("⚠️  ARIMA/SARIMAX         - Not available (optional)")
    
    # Check Prophet
    try:
        from prophet import Prophet
        print("✅ Prophet                - Available")
    except:
        print("⚠️  Prophet                - Not available (optional)")
    
    # Check TensorFlow/LSTM
    try:
        import tensorflow
        print("✅ LSTM (TensorFlow)      - Available")
    except:
        print("⚠️  LSTM (TensorFlow)     - Not available (optional)")

def main():
    """Run all checks"""
    print("\n" + "█"*60)
    print("█  NetSense Setup Verification")
    print("█"*60)
    
    results = {
        'Python Version': check_python_version(),
        'Core Modules': check_core_modules(),
        'Dependencies': check_dependencies(),
        'Local Files': check_local_files(),
        'Admin Privileges': check_admin_privileges(),
        'NetSense Modules': test_imports(),
    }
    
    check_optional_modules()
    check_ml_capabilities()
    
    # Summary
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    # Recommendations
    print_header("Next Steps")
    
    if passed == total:
        print("✅ All checks passed! You're ready to run NetSense.")
        print("\nRun the application with:")
        print("  python main.py")
        print("\n(Make sure to run as Administrator)")
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\nTo install missing dependencies:")
        print("  pip install -r requirements.txt")
        print("\nFor advanced features:")
        print("  pip install pystan==2.19.1.1 prophet")
        print("  pip install tensorflow")
    
    print("\n" + "█"*60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)