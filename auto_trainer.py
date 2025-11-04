"""
Automatic Model Training Scheduler
Automatically retrains models every 60 minutes with accumulated data.
"""

import threading
import time
from typing import Callable, Optional

class AutoTrainer:
    """Background scheduler for automatic model retraining"""
    
    def __init__(self, productivity_predictor, interval_minutes: int = 60):
        """
        Initialize auto-trainer.
        
        Args:
            productivity_predictor: ProductivityPredictor instance
            interval_minutes: Retraining interval in minutes (default: 60)
        """
        self.predictor = productivity_predictor
        self.interval = interval_minutes * 60  # Convert to seconds
        self.running = False
        self.thread = None
        self.last_training_time = time.time()
        self.training_count = 0
        
    def start(self):
        """Start the auto-training scheduler"""
        if self.running:
            print("[AUTO-TRAINER] Already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.thread.start()
        print(f"[AUTO-TRAINER] Started with {self.interval//60} minute interval")
    
    def stop(self):
        """Stop the auto-training scheduler"""
        self.running = False
        print("[AUTO-TRAINER] Stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop - runs in background thread"""
        print("[AUTO-TRAINER] Scheduler loop started")
        
        while self.running:
            try:
                current_time = time.time()
                time_since_last_training = current_time - self.last_training_time
                
                # Check if it's time to retrain
                if time_since_last_training >= self.interval:
                    self._perform_training()
                    self.last_training_time = current_time
                
                # Sleep for a short interval before checking again
                time.sleep(30)  # Check every 30 seconds if retraining is needed
                
            except Exception as e:
                print(f"[AUTO-TRAINER] Error in scheduler loop: {e}")
                time.sleep(60)
    
    def _perform_training(self):
        """Perform the actual model training"""
        try:
            print(f"\n{'='*60}")
            print(f"[AUTO-TRAINER] Starting automatic model training cycle #{self.training_count + 1}")
            print(f"{'='*60}")
            
            # Check if we have enough data
            with self.predictor.lock:
                data_points = len(self.predictor.productivity_history)
            
            if data_points < self.predictor.min_samples_for_training:
                print(f"[AUTO-TRAINER] Insufficient data: {data_points}/{self.predictor.min_samples_for_training} samples")
                return
            
            print(f"[AUTO-TRAINER] Training with {data_points} data points...")
            
            # Train all models
            start_time = time.time()
            
            results = {
                'linear': self.predictor.train_linear_model(),
                'gradient_boost': self.predictor.train_gradient_boost_model(),
                'arima': self.predictor.train_arima_model(),
                'sarimax': self.predictor.train_sarimax_model(),
            }
            
            # Conditional training
            try:
                from prophet import Prophet
                results['prophet'] = self.predictor.train_prophet_model()
            except:
                results['prophet'] = False
            
            try:
                import tensorflow
                results['lstm'] = self.predictor.train_lstm_model()
            except:
                results['lstm'] = False
            
            elapsed_time = time.time() - start_time
            
            # Summary
            trained_count = sum(1 for v in results.values() if v)
            print(f"\n[AUTO-TRAINER] Training completed in {elapsed_time:.2f}s")
            print(f"[AUTO-TRAINER] Successfully trained {trained_count}/{len(results)} models:")
            
            for model_name, success in results.items():
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"  {status} - {model_name.upper()}")
            
            # Display performance metrics
            perf = self.predictor.get_model_performance_summary()
            print(f"\n[AUTO-TRAINER] Performance Metrics:")
            for model, metrics in perf['performance'].items():
                r2 = metrics.get('r2', 'N/A')
                r2_str = f"{r2:.4f}" if isinstance(r2, (int, float)) else r2
                print(f"  {model.upper()}: R²={r2_str}")
            
            self.training_count += 1
            print(f"[AUTO-TRAINER] Cycle #{self.training_count} completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"[AUTO-TRAINER] Error during training: {e}")
            import traceback
            traceback.print_exc()
    
    def get_status(self) -> dict:
        """Get current auto-trainer status"""
        return {
            'running': self.running,
            'interval_minutes': self.interval // 60,
            'training_count': self.training_count,
            'last_training': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_training_time)),
            'next_training_in_seconds': max(0, self.interval - (time.time() - self.last_training_time))
        }

class TrainingScheduler:
    """High-level training scheduler with multiple strategies"""
    
    STRATEGY_INTERVAL = "interval"  # Train every N minutes
    STRATEGY_DATA_DRIVEN = "data_driven"  # Train when data amount changes
    
    def __init__(self, predictor, strategy: str = STRATEGY_INTERVAL, interval_minutes: int = 60):
        """
        Initialize training scheduler.
        
        Args:
            predictor: ProductivityPredictor instance
            strategy: Training strategy ('interval' or 'data_driven')
            interval_minutes: Interval between trainings (for interval strategy)
        """
        self.predictor = predictor
        self.strategy = strategy
        self.interval_minutes = interval_minutes
        self.auto_trainer = AutoTrainer(predictor, interval_minutes)
        self.data_points_last_check = 0
    
    def start(self):
        """Start the scheduler"""
        self.auto_trainer.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.auto_trainer.stop()
    
    def force_training(self):
        """Force immediate training"""
        print("[SCHEDULER] Forcing immediate training...")
        self.auto_trainer._perform_training()
        self.auto_trainer.last_training_time = time.time()
    
    def get_next_training_time(self) -> str:
        """Get time until next training"""
        status = self.auto_trainer.get_status()
        seconds_until = status['next_training_in_seconds']
        
        minutes = int(seconds_until // 60)
        seconds = int(seconds_until % 60)
        
        if seconds_until <= 0:
            return "Now"
        else:
            return f"{minutes}m {seconds}s"